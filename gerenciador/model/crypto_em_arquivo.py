from gerenciador.model.crypto import GenerateKey


class Cryptography_data():
    def __init__(self):
        self.key = GenerateKey().get_key()