from pathlib import Path

def caminho_arquivo(name_arquivo: str) -> Path:
    path = Path(__file__).parent.parent / "data" / f"{name_arquivo}"
    return path
