import flet as ft

def main(page: ft.Page):
    page.title = "Tam"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Ajout d'un contrôle visuel simple et direct
    txt = ft.Text("Tam Mobile - Prêt", size=22, weight=ft.FontWeight.BOLD)
    page.add(txt)

if __name__ == "__main__":
    ft.app(target=main)
