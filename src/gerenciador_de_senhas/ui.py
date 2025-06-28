from .core import gerar_senha
from .storage import salvar_json, carregar_json
from .crypto_utils import criptografar_dados, descriptografar_dados
import flet as ft
import asyncio
import json
import os

def main(page: ft.Page):
    page.title = "Gerenciador de Senhas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    campo_senha = ft.TextField(label="Senha Gerada", width=300)
    campo_site = ft.TextField(label="Digite sua senha", width=300)


    msg = ft.Text()
    msg_texto = ft.Text()

    botao_gerar = ft.ElevatedButton(text="Gerar Senha", on_click=adicionar_senha)
    botao_descriptografar = ft.ElevatedButton(text="Descriptografar Senhas", on_click=descriptografar_arquivo_csv)
    def adicionar_senha(e):
        senha = campo_senha.value
        site = campo_site.value

        if senha and site:
            page.add(ft.Text(f"Senha para {site}:" + f"\t Senha: {senha}"))
            salvar_json(senha, site)
            lista_senhas.controls.append(ft.Text(f"Senha para {site}:" + f"\t Senha: {senha}"))
            lista_senhas.update()
            campo_senha.value = ""
            campo_site.value = ""
            campo_senha.focus()
            campo_senha.update()
            campo_site.update()

    async def limpar_msg_apos_delay():
        await asyncio.sleep(5)
        msg_texto.value = ""
        page.update()

    lista_senhas = ft.Column(
        spacing=5,
        scroll="auto",
        width=400,
        height=200,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


    try:
        if os.path.exists("My_Pass/senhas.json"):
            with open("My_Pass/senhas.json", "r") as f:
                dados = json.load(f)
                for site, senha in dados.items():
                    lista_senhas.controls.append(
                        ft.Text(f"🔒 {site.strip()}: {senha.strip()}", selectable=True)
                    )
    except Exception as e:
        print(f"Erro ao carregar senhas: {e}")


    subtitulo = ft.ListView(
        controls=[
            ft.Text("Gerenciador de Senhas", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
            
        ],
        width=400,
        height=100,
        spacing=10,
        padding=10,
        auto_scroll=False
    )


    botoes1 = ft.Row([
        botao_gerar,
        ft.ElevatedButton(text="Adicionar Senha", on_click=adicionar_senha)
    ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )    
    layout = ft.Column([
        campo_site,
        campo_senha,
    ])

    botoes2 = ft.Row([
        ft.ElevatedButton(text="Salvar Senhas", on_click=criptograr_arquivo_csv),
        botao_descriptografar
    ], 
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
        
    )
    page.add(subtitulo)
    page.add(ft.Container(height=10))
    page.add(layout)
    page.add(ft.Container(height=20))
    page.add(botoes1)
    page.add(ft.Container(height=20))
    page.add(botoes2)
    page.add(lista_senhas)
    page.update()


ft.app(target=main)        
    