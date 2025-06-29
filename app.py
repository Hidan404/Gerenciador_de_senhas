import src.gerenciador_de_senhas.ui as ui
import flet as ft
from dotenv import load_dotenv
load_dotenv()

def main():
    ft.app(target=ui.main)

if __name__ == "__main__":
    main()