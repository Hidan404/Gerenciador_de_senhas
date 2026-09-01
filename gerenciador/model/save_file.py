from gerenciador.model.arquivos import Arquivo
from gerenciador.model.caminho import caminho_arquivo
from pathlib import Path
import json


class SaveFile:
    def __init__(self, arquivo: Arquivo, path: str):
        self.arquivo = arquivo.__dict__
        self.path = caminho_arquivo(path)

    def load_data(self):
        if not self.path.exists():
            return []
        else:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
              

    def save_data(self, data_update: list = None):
        if data_update is None:
            data_update = self.load_data()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data_update, f, ensure_ascii=False, indent=4)    


    def append_data(self):
        load_data = self.load_data()

        if len(load_data) > 0:
            proximo_id = load_data[-1].get("id", 0) + 1
            self.arquivo["id"] = proximo_id
        else:
            proximo_id = 1    

        self.arquivo["id"] = proximo_id    

        new_data = self.arquivo  
        load_data.append(new_data)    
        self.save_data(load_data)


#teste = SaveFile(Arquivo("teste", "123"), "teste.json")
#teste.append_data()        