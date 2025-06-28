# setup_db.py
import mysql.connector
from mysql.connector import Error

def criar_banco_e_tabela():
    try:
        print("[+] Conectando ao MySQL...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",           # ou outro usuário
            password="Hidan1994@#"   # substitua pela sua senha
        )

        if conn.is_connected():
            cursor = conn.cursor()
            print("[+] Criando banco de dados (se necessário)...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS gerenciador_senhas")
            cursor.execute("USE gerenciador_senhas")

            print("[+] Criando tabela (se necessário)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS senhas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    site VARCHAR(255) NOT NULL,
                    senha VARCHAR(255) NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("[✓] Banco e tabela criados/verificados com sucesso.")
        else:
            print("[-] Falha ao conectar.")
    except Error as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    criar_banco_e_tabela()
