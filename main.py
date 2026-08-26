import flet as ft

def main(page: ft.Page):
    page.title = "Tam"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Simple texte de démarrage stable
    page.add(
        ft.Text("Bienvenue sur Tam", size=20, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Tester", on_click=lambda e: print("Clic OK"))
    )

ft.app(target=main)
