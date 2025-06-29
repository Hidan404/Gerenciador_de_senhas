# storage.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


load_dotenv()
print("[DEBUG] USUÁRIO MYSQL:", os.getenv("DB_USER"))
print("[DEBUG] SENHA MYSQL:", os.getenv("DB_PASSWORD"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def conectar():
    """Cria e retorna uma conexão com o banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[!] Erro ao conectar ao MySQL: {e}")
        return None


def salvar_senha(site: str, senha: str):
    """Salva uma senha associada a um site no banco de dados."""
    conn = conectar()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        query = "INSERT INTO senhas (site, senha) VALUES (%s, %s)"
        cursor.execute(query, (site, senha))
        conn.commit()
        print(f"[✓] Senha para '{site}' salva com sucesso.")
    except Error as e:
        print(f"[!] Erro ao salvar senha: {e}")
    finally:
        cursor.close()
        conn.close()


def listar_senhas():
    """Retorna uma lista de tuplas (site, senha) do banco de dados."""
    conn = conectar()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT site, senha FROM senhas ORDER BY criado_em DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"[!] Erro ao buscar senhas: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
