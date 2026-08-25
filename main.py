from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib

app = FastAPI(title="Tam Global Secure API", version="4.1")

# Base de données multi-pays et multi-devises (Solde initial large pour les tests)
COMPTES_DB = {
    "+22800000000": {
        "nom": "Tam Services (Commissions)",
        "pays": "Togo",
        "devise": "XOF",
        "solde": 0.0,
        "pin_hash": hashlib.sha256("0000".encode()).hexdigest(),
        "historique": [],
        "tentatives_echouees": 0,
        "bloque": False
    },
    "+22890000001": {
        "nom": "Koffi Mensah",
        "pays": "Togo",
        "devise": "XOF",
        "solde": 500000.0,
        "pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
        "historique": [],
        "tentatives_echouees": 0,
        "bloque": False
    },
    "+233241234567": { 
        "nom": "Kwame Mensah",
        "pays": "Ghana",
        "devise": "GHS",
        "solde": 5000.0,
        "pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
        "historique": [],
        "tentatives_echouees": 0,
        "bloque": False
    },
    "+33612345678": { 
        "nom": "Sophie Martin",
        "pays": "France",
        "devise": "EUR",
        "solde": 2000.0,
        "pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
        "historique": [],
        "tentatives_echouees": 0,
        "bloque": False
    },
}

# Taux de change de référence par rapport au XOF
TAUX_CHANGE_VERS_XOF = {
    "XOF": 1.0,
    "GHS": 55.0,
    "EUR": 655.957,
    "USD": 600.0
}

class TransfertRequest(BaseModel):
    expéditeur_telephone: str = Field(..., pattern=r"^\+\d{8,15}$")
    destinataire_telephone: str = Field(..., pattern=r"^\+\d{8,15}$")
    montant: float = Field(..., gt=0)
    pin: str = Field(..., min_length=4, max_length=4)

def convertir_montant(montant: float, devise_source: str, devise_cible: str) -> float:
    if devise_source == devise_cible:
        return montant
    montant_en_xof = montant * TAUX_CHANGE_VERS_XOF.get(devise_source, 1.0)
    taux_cible = TAUX_CHANGE_VERS_XOF.get(devise_cible, 1.0)
    return round(montant_en_xof / taux_cible, 2)

@app.get("/solde/{telephone}")
def verifier_solde(telephone: str):
    if telephone not in COMPTES_DB:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    compte = COMPTES_DB[telephone]
    if compte["bloque"]:
        raise HTTPException(status_code=403, detail="Compte temporairement bloqué pour sécurité.")
    
    return {
        "telephone": telephone,
        "nom": compte["nom"],
        "pays": compte["pays"],
        "devise": compte["devise"],
        "solde": compte["solde"],
        "historique": compte["historique"]
    }

@app.post("/transferer/")
def transferer_argent(data: TransfertRequest):
    if data.expéditeur_telephone not in COMPTES_DB:
        raise HTTPException(status_code=400, detail="Numéro d'expéditeur non enregistré.")
    
    compte_exp = COMPTES_DB[data.expéditeur_telephone]
    
    if compte_exp["bloque"]:
        raise HTTPException(status_code=403, detail="🔒 Compte bloqué suite à des tentatives suspectes.")
    
    pin_haché_saisi = hashlib.sha256(data.pin.encode()).hexdigest()
    if compte_exp["pin_hash"] != pin_haché_saisi:
        compte_exp["tentatives_echouees"] += 1
        if compte_exp["tentatives_echouees"] >= 3:
            compte_exp["bloque"] = True
            raise HTTPException(status_code=403, detail="🚨 3 erreurs de PIN. Compte sécurisé et bloqué !")
        restant = 3 - compte_exp["tentatives_echouees"]
        raise HTTPException(status_code=400, detail=f"Code PIN incorrect. Il vous reste {restant} tentative(s).")
    
    compte_exp["tentatives_echouees"] = 0

    if data.destinataire_telephone not in COMPTES_DB:
        raise HTTPException(status_code=400, detail="Numéro du destinataire introuvable.")
    
    if data.expéditeur_telephone == data.destinataire_telephone:
        raise HTTPException(status_code=400, detail="Impossible d'effectuer un transfert vers soi-même.")

    compte_dest = COMPTES_DB[data.destinataire_telephone]
    compte_admin = COMPTES_DB["+22800000000"]
    
    devise_exp = compte_exp["devise"]
    devise_dest = compte_dest["devise"]
    
    frais_exp = data.montant * 0.04
    total_a_debiter = data.montant + frais_exp
    
    if compte_exp["solde"] < total_a_debiter:
        raise HTTPException(
            status_code=400, 
            detail=f"Solde insuffisant. Requis : {data.montant} + {frais_exp} (frais 4%) = {total_a_debiter} {devise_exp}"
        )
    
    montant_recu_dest = convertir_montant(data.montant, devise_exp, devise_dest)
    frais_en_xof = convertir_montant(frais_exp, devise_exp, "XOF")
    
    compte_exp["solde"] -= total_a_debiter
    compte_dest["solde"] += montant_recu_dest
    compte_admin["solde"] += frais_en_xof
    
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    compte_exp["historique"].insert(0, {
        "type": "Envoi",
        "details": f"Vers {data.destinataire_telephone} ({montant_recu_dest} {devise_dest})",
        "montant": f"-{total_a_debiter} {devise_exp}",
        "date": date_str
    })
    
    compte_dest["historique"].insert(0, {
        "type": "Reçu",
        "details": f"De {data.expéditeur_telephone}",
        "montant": f"+{montant_recu_dest} {devise_dest}",
        "date": date_str
    })

    compte_admin["historique"].insert(0, {
        "type": "Reçu (Commission)",
        "details": f"Via {data.expéditeur_telephone} ({data.montant} {devise_exp} convertis)",
        "montant": f"+{frais_en_xof} XOF",
        "date": date_str
    })
    
    return {
        "status": "success",
        "message": f"Transfert réussi ! Le destinataire a reçu {montant_recu_dest} {devise_dest}.",
        "frais": f"{frais_exp} {devise_exp} (Convertis en {frais_en_xof} XOF pour Tam Services)",
        "nouveau_solde_expediteur": f"{compte_exp['solde']} {devise_exp}"
    }