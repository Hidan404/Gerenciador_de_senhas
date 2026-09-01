from pathlib import Path

from cryptography.fernet import Fernet
from gerenciador.model.caminho import caminho_arquivo

class GenerateKey:
    def __init__(self):
        key = Fernet.generate_key()
        self.key = key
        self.path_key = self.set_path_key("key.key")

    def set_path_key(self, name_arquivo: str):
        path_key = caminho_arquivo(name_arquivo)   
        if not path_key.parent.exists():
            path_key.parent.mkdir(parents=True, exist_ok=True)

        return path_key

    def save_key(self):
        
        with open(self.path_key, "wb") as key_file:
            key_file.write(self.key)  


    def load_key(self):
        with open(self.path_key, "rb") as key_file:
            self.key = key_file.read()  

        return self.key


    def get_key(self):
        if not self.path_key.exists():
            self.save_key()
        else:
            self.load_key()
            print(f"Chave carregada do arquivo: {self.path_key}")

        return self.key
            


#generate_key = GenerateKey()
#generate_key.get_key()