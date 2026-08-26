import flet as ft
import requests

# URL de votre backend en ligne sur Render
API_URL = "https://tam-backend-srv-da67vu67bikc7385j9t0.onrender.com"

def main(page: ft.Page):
    page.title = "Tam Mobile"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # Composants de l'interface utilisateur
    titre_app = ft.Text("Tam - Services Financiers", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)
    telephone_input = ft.TextField(label="Numéro de téléphone (ex: +22890000001)", width=300)
    solde_text = ft.Text(value="", size=15, text_align=ft.TextAlign.CENTER)
    loader = ft.ProgressRing(visible=False)

    def verifier_solde_clic(e):
        tel = telephone_input.value.strip()
        if not tel:
            solde_text.value = "⚠️ Veuillez entrer un numéro de téléphone."
            solde_text.color = ft.colors.RED
            page.update()
            return
        
        # Affichage du chargement
        loader.visible = True
        solde_text.value = "Connexion au serveur..."
        solde_text.color = ft.colors.BLACK
        page.update()

        try:
            # Requête sécurisée vers votre API Render avec un délai de 10 secondes
            response = requests.get(f"{API_URL}/solde/{tel}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                solde_text.value = f"✅ Nom : {data['nom']}\n💰 Solde : {data['solde']} {data['devise']}\n🌍 Pays : {data['pays']}"
                solde_text.color = ft.colors.GREEN_800
            else:
                detail = response.json().get('detail', 'Compte introuvable')
                solde_text.value = f"❌ Erreur : {detail}"
                solde_text.color = ft.colors.RED
        except requests.exceptions.ConnectionError:
            solde_text.value = "🌐 Erreur de réseau : Vérifiez votre connexion Internet."
            solde_text.color = ft.colors.RED
        except requests.exceptions.Timeout:
            solde_text.value = "⏱️ Le serveur met trop de temps à répondre."
            solde_text.color = ft.colors.RED
        except Exception as ex:
            solde_text.value = f"❌ Erreur inattendue : {ex}"
            solde_text.color = ft.colors.RED
        
        loader.visible = False
        page.update()

    btn_valider = ft.ElevatedButton(
        text="Consulter mon solde", 
        on_click=verifier_solde_clic,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE
    )

    # Ajout des éléments sur la page de l'application
    page.add(
        titre_app,
        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
        telephone_input,
        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
        btn_valider,
        ft.Divider(height=15, color=ft.colors.TRANSPARENT),
        loader,
        solde_text
    )

if __name__ == "__main__":
    ft.app(target=main)
