import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

CHAVE_PATH = os.path.join(os.path.dirname(__file__), "chave.key")


def gerar_chave():
    if not os.path.exists(CHAVE_PATH):
        chave = get_random_bytes(16)
        with open(CHAVE_PATH, "wb") as f:
            f.write(chave)
    else:
        with open(CHAVE_PATH, "rb") as f:
            chave = f.read()
    return chave


def criptografar_dados(texto: str, chave: bytes) -> str:
    cipher = AES.new(chave, AES.MODE_CBC)
    iv = cipher.iv
    cifrado = cipher.encrypt(pad(texto.encode(), AES.block_size))
    return base64.b64encode(iv + cifrado).decode()


def descriptografar_dados(dados_encriptados: str, chave: bytes) -> str:
    try:
        dados = base64.b64decode(dados_encriptados)
        iv = dados[:16]                      # <- primeiros 16 bytes = IV
        ciphertext = dados[16:]              # <- resto = dados criptografados
        cipher = AES.new(chave, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plaintext.decode()
    except Exception as e:
        return f"<erro: {str(e)}>"

