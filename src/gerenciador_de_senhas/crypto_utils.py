from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def criptografar_dados(dados, chave):
    cipher = AES.new(chave, AES.MODE_CBC)
    iv = cipher.iv
    dados_padded = pad(dados.encode(), AES.block_size)
    dados_encriptados = cipher.encrypt(dados_padded)
    return iv + dados_encriptados

def descriptografar_dados(dados_encriptados, chave):
    iv = dados_encriptados[:AES.block_size]
    cipher = AES.new(chave, AES.MODE_CBC, iv)
    dados_padded = cipher.decrypt(dados_encriptados[AES.block_size:])
    return unpad(dados_padded, AES.block_size).decode()

def gerar_chave():
    return get_random_bytes(16) 