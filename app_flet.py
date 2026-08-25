import flet as ft
import requests

# URL de votre backend hébergé sur le cloud Render
API_URL = "https://tam-backend-a9vh.onrender.com"

def main(page: ft.Page):
    page.title = "Tam - Global Multi-Devises & Sécurité"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 480
    page.window_height = 880

    exp_input = ft.TextField(label="Votre Numéro (ex: +22890000001 ou +33...)", value="+22890000001", prefix_icon=ft.Icons.PHONE)
    pin_input = ft.TextField(label="Code PIN secret (4 chiffres)", password=True, can_reveal_password=True, max_length=4, prefix_icon=ft.Icons.LOCK)
    dest_input = ft.TextField(label="Numéro du destinataire international", value="+33612345678", prefix_icon=ft.Icons.SEND)
    montant_input = ft.TextField(label="Montant à envoyer", keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.ATTACH_MONEY)
    
    solde_card = ft.Text(value="Solde : Chargement...", size=15, weight="bold", color=ft.Colors.TEAL_900, text_align=ft.TextAlign.CENTER)
    result_text = ft.Text(value="", weight="bold", text_align=ft.TextAlign.CENTER, size=12)
    
    historique_lv = ft.ListView(expand=1, spacing=8, padding=5, auto_scroll=True)

    def actualiser_donnees(e=None):
        tel = exp_input.value.strip()
        if not tel:
            return
        try:
            res = requests.get(f"{API_URL}/solde/{tel}")
            if res.status_code == 200:
                data = res.json()
                solde_card.value = f"Compte : {data['nom']} ({data['pays']})\nSolde : {data['solde']:,.2f} {data['devise']}"
                
                historique_lv.controls.clear()
                for h in data["historique"]:
                    is_envoi = "Envoi" in h["type"]
                    historique_lv.controls.append(
                        ft.Container(
                            content=ft.ListTile(
                                leading=ft.Icon(
                                    ft.Icons.CALL_MADE if is_envoi else ft.Icons.CALL_RECEIVED,
                                    color=ft.Colors.RED_400 if is_envoi else ft.Colors.GREEN_400
                                ),
                                title=ft.Text(f"{h['type']} : {h['montant']}", weight="bold", size=12),
                                subtitle=ft.Text(f"{h['details']} — {h['date']}", size=10, color=ft.Colors.GREY_700),
                            ),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=8,
                            padding=2
                        )
                    )
            else:
                solde_card.value = "⚠️ Compte introuvable ou verrouillé"
        except:
            solde_card.value = "❌ Erreur de liaison avec le serveur cloud"
        page.update()

    exp_input.on_change = actualiser_donnees

    def executer_transfert(e):
        try:
            montant_val = float(montant_input.value)
        except ValueError:
            result_text.value = "❌ Veuillez entrer un montant valide."
            result_text.color = ft.Colors.RED_700
            page.update()
            return

        payload = {
            "expéditeur_telephone": exp_input.value.strip(),
            "destinataire_telephone": dest_input.value.strip(),
            "montant": montant_val,
            "pin": pin_input.value.strip()
        }

        try:
            res = requests.post(f"{API_URL}/transferer/", json=payload)
            data = res.json()
            if res.status_code == 200:
                result_text.value = f"✅ {data['message']}\nFrais : {data['frais']}"
                result_text.color = ft.Colors.GREEN_800
                montant_input.value = ""
                pin_input.value = ""
                actualiser_donnees()
            else:
                result_text.value = f"❌ {data.get('detail', 'Erreur de transaction')}"
                result_text.color = ft.Colors.RED_700
        except:
            result_text.value = "❌ Impossible d'atteindre le serveur Tam sur le cloud."
            result_text.color = ft.Colors.RED_700
        page.update()

    btn_valider = ft.ElevatedButton(
        content=ft.Text("Valider le Transfert International", weight="bold", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.TEAL_700,
        on_click=executer_transfert,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    actualiser_donnees()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PUBLIC, size=34, color=ft.Colors.TEAL_800),
                    ft.Text("TAM GLOBAL", size=26, weight="bold", color=ft.Colors.TEAL_900),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Transferts Multi-Pays & Multi-Devises Sécurisés", size=10, italic=True, color=ft.Colors.GREY_700),
                ft.Divider(color=ft.Colors.TEAL_200),
                
                ft.Container(
                    content=solde_card,
                    padding=10,
                    bgcolor=ft.Colors.TEAL_50,
                    border_radius=10
                ),
                
                exp_input,
                pin_input,
                dest_input,
                montant_input,
                
                btn_valider,
                result_text,
                
                ft.Divider(color=ft.Colors.TEAL_200),
                ft.Text("Historique Global", size=13, weight="bold", color=ft.Colors.BLUE_GREY_900),
                
                ft.Container(
                    content=historique_lv,
                    height=160,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                    padding=5
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=15
        )
    )

if __name__ == "__main__":
    ft.run(main)