import flet as ft
import requests

API_URL = "https://tam-backend-srv-da67vu67bikc7385j9t0.onrender.com"

def main(page: ft.Page):
    page.title = "Tam"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20

    # Interface ultra-épurée pour valider le maintien de l'app
    txt_titre = ft.Text("Tam Mobile", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)
    txt_statut = ft.Text("Application initialisée avec succès", size=14, color=ft.colors.GREEN_700)
    
    tel_input = ft.TextField(label="Numéro de téléphone", width=280)
    result_text = ft.Text(value="", size=14)

    def tester_connexion(e):
        tel = tel_input.value.strip()
        if not tel:
            result_text.value = "Veuillez entrer un numéro."
            page.update()
            return
        
        result_text.value = "Connexion..."
        page.update()
        
        try:
            res = requests.get(f"{API_URL}/solde/{tel}", timeout=8)
            if res.status_code == 200:
                data = res.json()
                result_text.value = f"Succès ! Solde : {data.get('solde')} {data.get('devise')}"
            else:
                result_text.value = "Erreur de compte."
        except Exception as ex:
            result_text.value = f"Erreur réseau : {ex}"
        page.update()

    btn = ft.ElevatedButton("Vérifier le solde", on_click=tester_connexion)

    page.add(
        txt_titre,
        ft.Divider(height=10),
        txt_statut,
        ft.Divider(height=20),
        tel_input,
        ft.Divider(height=10),
        btn,
        ft.Divider(height=15),
        result_text
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
