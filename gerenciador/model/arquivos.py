from pathlib import Path
from gerenciador.model.caminho import caminho_arquivo


class Arquivo:
    _contador_id = 0

    def __init__(self,name_site: str, password: str):
        self.id = self.generate_id()
        self.name_site = name_site
        self.password = password

    def generate_id(self):
        Arquivo._contador_id += 1
        return Arquivo._contador_id
        