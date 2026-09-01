from gerenciador.model.crypto import GenerateKey
from gerenciador.model.save_file import SaveFile
from gerenciador.model.arquivos import Arquivo
from cryptography.fernet import Fernet
import json



class Cryptography_data():
    def __init__(self, arquivo: Arquivo):
        self.key = Fernet(GenerateKey().get_key())
        self.file_load = SaveFile(arquivo=arquivo, path="data.json")

    def load_data_from_encrypted_file(self):
        return self.file_load.load_data()

    def encrypt_data(self) -> bytes:
        fernet = self.key

        try:
            datos = self.load_data_from_encrypted_file()
            data_to_json = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            data_encrypted = fernet.encrypt(data_to_json)
            print(self.file_load.path)
            with open(self.file_load.path, "wb") as f:
                f.write(data_encrypted)
            print("Dados criptografados e salvos com sucesso kkk")    
        except Exception as e:
            print(f"Erro ao criptografar os dados: {e}")
            return None        
 
        return data_encrypted


    def decrypt_data(self, data_encrypted: bytes) -> str:
        fernet = self.key
        try:
            data_decrypted = fernet.decrypt(data_encrypted)
            with open(self.file_load.path, "w", encoding="utf-8") as f:
                json.dump(json.loads(data_decrypted.decode()), f, ensure_ascii=False, indent=4)

            return data_decrypted.decode()
        except Exception as e:
            print(f"Erro ao descriptografar os dados: {e}")
            return None

teste = Cryptography_data(Arquivo("amazon.com", "123456"))
#print(teste.file_load.append_data())

print("ANTES DA CRIPTOGRAFIA:")
print(teste.file_load.load_data())

#teste.encrypt_data()
teste.decrypt_data(teste.file_load.path.read_bytes())