# Gerenciador de Senhas CLI — Plano do Projeto

Projeto pessoal de gerenciador de senhas em linha de comando. Um único arquivo
local cifrado com AES-GCM. Senha mestra para destrancar. Sem banco de dados,
sem servidor, sem complexidade desnecessária.

---

## 1. Visão Geral

- **Linguagem:** Python 3.13+
- **Interface:** CLI (linha de comando com `argparse`)
- **Persistência:** Arquivo `.enc` local cifrado com AES-GCM
- **Segurança:** Senha mestra → PBKDF2 → chave AES-256
- **Dependências:** apenas `pycryptodome`

### Por que estas escolhas?

| Decisão | Motivo |
|---|---|
| **Arquivo local cifrado** | Nada de banco de dados — um só arquivo, portátil, backup fácil |
| **AES-GCM** | Modo autenticado: detecta adulteração dos dados |
| **PBKDF2** | Torna brute force da senha mestra caro (600k iterações) |
| **Senha mestra** | Chave nunca fica salva em disco — só existe em memória |

---

## 2. Arquitetura MVC

O programa segue o padrão **MVC** (Model / View / Controller).

### O que cada camada faz

| Camada | Responsabilidade | Proibido fazer |
|---|---|---|
| **Model** | Criptografia e lógica dos dados | Não sabe que existe terminal |
| **View** | O que o usuário vê e digita | Não contém lógica de negócio |
| **Controller** | Orquestra tudo: lê comando, chama Model, manda View exibir | Não implementa criptografia |

### Como as camadas se conectam

```
app.py (Controller)
  │
  ├── View (cli.py): "digite a senha mestra"
  │       │
  │       └── getpass.getpass() → senha_mestra
  │
  ├── Model crypto (crypto.py): deriva_chave(senha_mestra, salt) → chave
  │
  ├── Model vault (vault.py): carregar_vault(.enc, chave) → dados (dict)
  │       │
  │       └── lê arquivo → decifra → retorna JSON como dict
  │
  ├── View (cli.py): mostra o que foi pedido
  │
  └── Model vault (vault.py): salvar_vault(.enc, chave, dados)
          │
          └── pega dict → cifra → grava no arquivo
```

**Regra de ouro:** o Controller (app.py) é o único que conhece Model e View.
O Model não conhece a View. A View não conhece o Model.

---

## 3. Estrutura de Pastas e Arquivos

```
.
├── app.py                          # Controller: entry point + argparse + fluxo
├── gerenciador/
│   ├── __init__.py                 # vazio
│   ├── model/
│   │   ├── __init__.py             # vazio
│   │   ├── crypto.py               # Criptografia: PBKDF2 + AES-GCM
│   │   └── vault.py                # CRUD do arquivo: carregar, salvar, adicionar, remover, listar
│   └── view/
│       ├── __init__.py             # vazio
│       └── cli.py                  # Interface: prompts, getpass, argparse, mensagens
├── tests/
│   ├── __init__.py
│   ├── test_crypto.py              # Testes unitários do crypto
│   └── test_vault.py               # Testes unitários do vault
├── requirements.txt                # pycryptodome==3.23.0
└── .gitignore
```

### Descrição detalhada de cada arquivo

#### `app.py` — O Controller

O entry point do programa. É o orquestrador.

- Configura o `argparse` com os comandos: `init`, `add`, `get`, `list`, `delete`, `generate`
- Lê o comando do usuário
- Chama a View para pedir a senha mestra
- Chama o Model crypto para derivar a chave
- Chama o Model vault para carregar/salvar o arquivo
- Chama a View para mostrar o resultado
- Trata erros e mostra mensagens amigáveis

**Não contém:** funções de criptografia, SQL, nem prompts diretos ao usuário
(os prompts ficam na View).

#### `gerenciador/model/crypto.py` — Criptografia

Responsabilidade: transformar senha em chave e cifrar/descriptografar dados.

Funções que deve ter:

- `gerar_salt()` → gera 16 bytes aleatórios seguros (só usado no `init`)
- `derivar_chave(senha_mestra, salt)` → senha → chave AES de 32 bytes via PBKDF2
- `cifrar(chave, texto)` → retorna blob (bytes) com nonce + tag + ciphertext
- `decifrar(chave, blob)` → lê o blob, extrai nonce/tag/ciphertext, descriptografa

**Não contém:** prompts, print, argparse, leitura de arquivos.

#### `gerenciador/model/vault.py` — O Cofre

Responsabilidade: gerenciar o conteúdo do arquivo `.enc` como um dicionário Python.

Funções que deve ter:

- `carregar_vault(caminho, chave)` → lê o arquivo .enc, decifra, retorna dict
- `salvar_vault(caminho, chave, dados)` → cifra o dict, grava no arquivo .enc
- `adicionar_credencial(dados, site, usuario, senha)` → adiciona entrada no dict
- `remover_credencial(dados, site, usuario)` → remove entrada do dict
- `listar_credenciais(dados)` → retorna lista de sites/usuarios

**Não contém:** criptografia (chama crypto.py), nem prompts ao usuário.

#### `gerenciador/view/cli.py` — Interface

Responsabilidade: interagir com o usuário no terminal.

- Configura o `argparse`: define os comandos, argumentos e help
- Pede a senha mestra via `getpass.getpass()` (não ecoa no terminal)
- Mostra listas formatadas de credenciais
- Mostra mensagens de sucesso/erro

**Não contém:** chamar `cifrar`, `decifrar`, `carregar_vault`, nem `salvar_vault`.

---

## 4. Fluxo de Dados

### Como o arquivo `.enc` funciona

O arquivo inteiro é um JSON com 4 campos, todos em base64:

```json
{
  "salt": "<base64 do salt PBKDF2>",
  "nonce": "<base64 do nonce AES>",
  "tag": "<base64 do tag GCM>",
  "dados": "<base64 do ciphertext>"
}
```

### Fluxo de gravar (`add`)

```
senha_mestra (digitada)
    │
    └─ PBKDF2(senha_mestra, salt) → chave (32 bytes, só em memória)
    │
    └─ carregar_vault(.enc, chave) → lê e decifra o JSON → dict
    │
    └─ adicionar_credencial(dict, site, usuario, senha) → dict atualizado
    │
    └─ salvar_vault(.enc, chave, dict) → cifra → grava .enc atualizado
```

### Fluxo de ler (`get`)

```
senha_mestra (digitada)
    │
    └─ PBKDF2(senha_mestra, salt) → chave (32 bytes, só em memória)
    │
    └─ carregar_vault(.enc, chave) → lê e decifra o JSON → dict
    │
    └─ mostra a credencial pedida ao usuário
```

### Fluxo do `init`

```
senha_mestra (digitada)
    │
    └─ gerar_salt() → 16 bytes aleatórios
    │
    └─ PBKDF2(senha_mestra, salt) → chave
    │
    └─ salvar_vault(.enc, chave, {}) → grava vault vazio cifrado
```

**Regra:** a senha mestra NUNCA é salva. A chave é derivada a cada comando.
O salt fica no arquivo `.enc` (não é segredo).

---

## 5. Segurança

### Derivação de chave

```
senha_mestra → PBKDF2-HMAC-SHA256(senha, salt, 600_000 iterações) → chave 32 bytes
```

- **Salt:** 16 bytes aleatórios, gerado no `init`, fica no `.enc`. Não é segredo.
- **600.000 iterações:** padrão OWASP. Torna brute force caro.
- **Validação implícita:** senha errada → chave errada → GCM falha na verificação.
  Não precisa guardar hash da senha mestra.

### AES-GCM (modo autenticado)

- Gera **nonce** único a cada cifragem (12 bytes)
- Gera **tag** de autenticação (16 bytes) — verifica integridade
- Qualquer alteração nos dados → `decrypt_and_verify` falha
- CBC (projeto antigo) não autenticava — GCM sim

### Regras de segurança

- Senha mestra sempre pedida via `getpass.getpass()` (não ecoa)
- Chave derivada a cada comando, nunca salva em disco
- Nunca logar senha mestra, chave ou dados descriptografados
- Arquivo `.enc` contém apenas bytes cifrados — sem ele, inútil

---

## 6. Comandos CLI

```
python app.py init                          # primeira vez: cria vault vazio
python app.py add site -u usuario           # adicionar credencial
python app.py list                          # listar sites (só nomes)
python app.py get site                      # ver credencial
python app.py delete site -u usuario        # remover credencial
python app.py generate [tamanho]            # gerar senha forte
```

### Local do arquivo vault

`~/.vault/vault.enc` — padrão de configuração do usuário.

---

## 7. Plano de Implementação (fases)

| Fase | Arquivo | O que fazer |
|---|---|---|
| **1** | `crypto.py` | Derivar chave, cifrar, decifrar. Fundação de tudo. |
| **2** | `vault.py` | CRUD do JSON. Depende do crypto. |
| **3** | `cli.py` | Prompts, argparse, getpass, mensagens. |
| **4** | `app.py` | Junta tudo: lê comando, chama model, mostra view. |
| **5** | `tests/` | Testes unitários de crypto e vault. |

### Por que essa ordem?

- `crypto.py` é a fundação — sem ele, nada funciona. Teste isoladamente primeiro.
- `vault.py` depende de crypto mas não de UI — teste com arquivo temporário.
- `cli.py` depende do model mas não contém lógica — é a "pele".
- `app.py` é o elo — faz sentido ser último, porque conhece tudo.

---

## 8. Checklist por fase

### Fase 1 (crypto.py)
- [ ] `derivar_chave` mesma senha+salt → mesma chave
- [ ] `cifrar` → `decifrar` volta o texto original
- [ ] chave errada → `decifrar` estoura exceção de autenticação
- [ ] dado adulterado (mudar 1 byte) → exceção

### Fase 2 (vault.py)
- [ ] `salvar_vault` cria arquivo se não existe
- [ ] `carregar_vault` lê e decifra corretamente
- [ ] Adicionar, remover, listar funcionam
- [ ] Vault vazio funciona (nenhuma credencial)

### Fase 3 (cli.py)
- [ ] `argparse` reconhece todos os comandos
- [ ] `getpass` usado (senha não ecoa)
- [ ] Erros exibidos claramente

### Fase 4 (app.py)
- [ ] `init` cria vault vazio
- [ ] `add` adiciona e salva
- [ ] `list` mostra só sites
- [ ] `get` descriptografa e mostra
- [ ] `delete` remove e salva

---

## 9. Conceitos de Estudo

### PBKDF2
Função "lenta" de propósito. Transforma senha em chave. Lenta porque torna
cada tentativa de brute force cara para o atacante.

### AES-GCM
Modo de cifra autenticado. Não só esconde os dados — verifica se foram
alterados. Combina confidencialidade + integridade + autenticidade.

### Salt
Número aleatório usado para dificultar ataques com tabelas pré-computadas.
Não é segredo — pode ficar no arquivo. Só serve para que a mesma senha
gere chaves diferentes em instalações diferentes.

### Nonce
Número único gerado a cada cifragem. Sem ele, o AES-GCM não funciona.
NUNCA reutilizar o mesmo nonce com a mesma chave.

### Tag
"Assinatura" do dado cifrado. Se alguém mexer no dado, o tag não bate
e a descriptografia falha. É o que torna o GCM autenticado.

### `secrets` vs `random`
`random` é previsível (não serve para segurança). `secrets` usa entropia
do sistema operacional e é próprio para criptografia e geração de senhas.

---

## 10. Referência Rápida — APIs do pycryptodome

```python
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

# Derivação de chave
chave = PBKDF2(senha, salt, dkLen=32, count=600_000, hmac_hash_module=SHA256)

# Criptografia AES-GCM
cipher = AES.new(chave, AES.MODE_GCM)         # nonce gerado automaticamente
ciphertext = cipher.encrypt(dados)
tag = cipher.digest()                          # obter DEPOIS do encrypt

# Descriptografia + verificação
cipher = AES.new(chave, AES.MODE_GCM, nonce=nonce)
dados = cipher.decrypt_and_verify(ciphertext, tag)  # falha se adulterado
```

> **Armadilha:** o `tag` deve ser obtido DEPOIS de `encrypt`. Guarde
> `nonce`, `tag` e `ciphertext` juntos no JSON.
