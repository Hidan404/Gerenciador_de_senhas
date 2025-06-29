from .core import gerador_senhas
from .storage import salvar_senha, listar_senhas
from .crypto_utils import criptografar_dados, descriptografar_dados, gerar_chave
import flet as ft
import asyncio
from .storage import deletar_senha


def main(page: ft.Page):
    page.title = "Gerenciador de Senhas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    campo_senha = ft.TextField(label="Senha Gerada", width=300)
    campo_site = ft.TextField(label="Digite o nome do site", width=300)
    msg_texto = ft.Text()

    lista_senhas = ft.Column(
        spacing=5,
        scroll="auto",
        width=400,
        height=200,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def adicionar_senha(e):
        senha = campo_senha.value
        site = campo_site.value

        if senha and site:
            senha_criptografada = criptografar_dados(senha, gerar_chave())
            salvar_senha(site, senha_criptografada)  
            lista_senhas.controls.append(ft.Text(f"🔐 {site}: {senha}"))
            campo_senha.value = ""
            campo_site.value = ""
            campo_senha.focus()
            lista_senhas.update()
            page.update()

    async def limpar_msg_apos_delay():
        await asyncio.sleep(5)
        msg_texto.value = ""
        page.update()

    def carregar_senhas():
        lista_senhas.controls.clear()
        for site, senha_criptografada in listar_senhas():
            senha_descriptografada = descriptografar_dados(senha_criptografada, gerar_chave())
            
            def excluir(site=site):
                deletar_senha(site)
                carregar_senhas()
                page.update()

            linha = ft.Row([
                ft.Text(f"🔐 {site.strip()}: {senha_descriptografada.strip()}", selectable=True, expand=True),
                ft.IconButton(icon=ft.icons.DELETE, tooltip="Excluir", on_click=lambda e, s=site: excluir(s))
            ])

            lista_senhas.controls.append(linha)

    subtitulo = ft.ListView(
        controls=[
            ft.Text("Gerenciador de Senhas", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        ],
        width=400,
        height=100,
        spacing=10,
        padding=10,
        auto_scroll=False
    )

    botao_gerar = ft.ElevatedButton(text="Gerar Senha", on_click=lambda e: campo_senha.__setattr__('value', gerador_senhas()))
    botao_adicionar = ft.ElevatedButton(text="Adicionar Senha", on_click=adicionar_senha)
    botao_salvar = ft.ElevatedButton(text="Criptografar Dados", on_click=criptografar_dados)
    botao_descriptografar = ft.ElevatedButton(text="Descriptografar Dados", on_click=descriptografar_dados)

    botoes1 = ft.Row([botao_gerar, botao_adicionar], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    botoes2 = ft.Row([botao_salvar, botao_descriptografar], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    layout = ft.Column([campo_site, campo_senha])

    page.add(subtitulo)
    page.add(ft.Container(height=10))
    page.add(layout)
    page.add(ft.Container(height=20))
    page.add(botoes1)
    page.add(ft.Container(height=20))
    page.add(botoes2)
    page.add(lista_senhas)

    carregar_senhas()
    page.update()
