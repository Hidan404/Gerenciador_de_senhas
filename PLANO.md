# Gerenciador de Senhas CLI — Plano do Projeto (MVC)

Projeto pessoal de gerenciador de senhas em linha de comando, instalável em
qualquer PC, seguindo o padrão **MVC**. Este documento é o guia completo de
implementação. O código será escrito pelo próprio desenvolvedor, com este
documento servindo como especificação e material de estudo.

---

## 1. Visão Geral

- **Linguagem:** Python 3.13+
- **Interface:** CLI (linha de comando)
- **Persistência:** SQLite (arquivo local, zero configuração)
- **Segurança:** Senha mestra + PBKDF2 + AES-GCM
- **Arquitetura:** MVC (Model / View / Controller)
- **Dependências obrigatórias:** apenas `pycryptodome`
- **Dependências opcionais:** `rich` (tabelas bonitas no terminal)

### Por que estas escolhas?

| Decisão | Motivo |
|---|---|
| **CLI em vez de GUI** | Funciona em qualquer PC com Python, leve, scriptável |
| **SQLite em vez de MySQL** | Zero configuração, arquivo local, portátil — ideal para uso pessoal em máquinas diferentes |
| **Senha mestra em vez de chave fixa** | A chave nunca fica salva em disco; só existe na memória durante o uso |
| **AES-GCM em vez de AES-CBC** | Modo autenticado: detecta adulteração/corrupção dos dados |
| **`secrets` em vez de `random`** | `random` é determinístico/prevísivel e NUNCA deve ser usado para criptografia |

---

## 2. Arquitetura MVC

O padrão **MVC** separa o programa em três camadas com responsabilidades bem
definidas. Essa separação permite testar cada parte isoladamente e trocar a
interface (ex.: por GUI) sem tocar na lógica.

| Camada | Responsabilidade | Proibido fazer |
|---|---|---|
| **Model** | Regras de negócio + dados: criptografia, banco SQLite, gerador de senha | Não sabe que existe terminal |
| **View** | Tudo que o usuário vê/digita: `print`, `input`, `getpass`, tabelas | Não contém lógica de negócio |
| **Controller** | Orquestra: lê o comando (`argparse`), chama o Model, manda a View exibir | Não implementa criptografia nem SQL |

```
┌────────────┐   comando    ┌──────────────┐   chama    ┌──────────┐
│    View    │  <────────── │  Controller  │ ─────────> │  Model   │
│  (terminal)│   exibe      └──────────────┘   retorna  └──────────┘
└────────────┘
```

### Estrutura de pastas

```
.
├── app.py                      # entry point: parse args → controller.dispatch()
├── gerenciador/
│   ├── __init__.py
│   ├── controller.py           # Controller: comandos init/add/list/get/edit/delete/generate
│   ├── model/
│   │   ├── __init__.py
│   │   ├── crypto.py           # PBKDF2 (senha mestra → chave) + AES-GCM
│   │   ├── database.py         # SQLite: schema, CRUD, metadados (salt)
│   │   └── generator.py        # gerador de senha forte
│   └── view/
│       ├── __init__.py
│       └── cli.py              # View: prompts, getpass, tabelas, mensagens
├── tests/
│   ├── test_crypto.py
│   ├── test_database.py
│   └── test_generator.py
├── pyproject.toml
└── .gitignore
```

---

## 3. Segurança (a parte mais importante)

### 3.1 Derivação de chave — nunca guarde a chave

```
senha_mestra (digitada a cada uso, não fica salva)
      │
      └── PBKDF2-HMAC-SHA256(senha_mestra, salt, 600_000 iterações)
                              │
                              └── chave AES de 32 bytes (só existe em memória)
```

- O **salt** (16 bytes aleatórios) é gerado no primeiro uso (`init`) e guardado
  na tabela `metadata`. Não é segredo — pode ficar no banco. Sua função é
  garantir que duas instalações iguais gerem chaves diferentes e dificultar
  ataques com tabelas pré-computadas (rainbow tables).
- O número de iterações (600.000) torna o *brute force* da senha mestra caro
  para o atacante. É o padrão recomendado pelo OWASP para PBKDF2.
- **Validação implícita:** se a senha mestra estiver errada, o PBKDF2 deriva
  uma chave diferente e o AES-GCM falha na autenticação. Não é preciso
  armazenar hash da senha mestra — a própria criptografia valida.

### 3.2 Criptografia — AES-GCM (modo autenticado)

- **Confidencialidade** + **integridade** + **autenticidade** num único modo.
- Cada senha cifrada armazena: `nonce (12 bytes) + tag (16 bytes) + ciphertext`.
- O **nonce** deve ser único por criptografia (gerado com `get_random_bytes`).
- CBC (usado no projeto antigo) criptografa mas NÃO autentica: um atacante
  pode alterar os dados sem detecção. GCM elimina esse problema.

### 3.3 Regras de segurança

- Senha mestra solicitada via `getpass.getpass()` (não ecoa no terminal).
- `list` NUNCA descriptografa — exibe só os sites (segurança e velocidade).
- Descriptografia acontece apenas no `get` e `edit`.
- Nunca logar senha mestra, chave ou senhas descriptografadas.

---

## 4. Schema do Banco de Dados (SQLite)

```sql
CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),   -- só uma linha: a da nossa instalação
    salt BLOB NOT NULL,                      -- salt do PBKDF2
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS senhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT NOT NULL,
    usuario TEXT,                            -- email/usuário opcional
    senha_cifrada BLOB NOT NULL,             -- nonce + tag + ciphertext (AES-GCM)
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_site_usuario ON senhas(site, usuario);
```

- **Índice único `(site, usuario)`**: impede duplicatas. O projeto antigo não
  tinha `id` na hora de apagar e removia **todas** as entradas do site.
- **Localização do arquivo:** `~/.config/gerenciador_senhas/gerenciador.db`
  (padrão de diretórios de configuração do sistema). Assim funciona em
  qualquer PC sem configuração.

---

## 5. Comandos da CLI

Interface via `argparse` (stdlib).

```
python app.py init                      # primeira vez: define senha mestra, cria salt + DB
python app.py add site -u usuario       # salva senha (pede no prompt ou --generate)
python app.py list                      # lista sites (só os nomes)
python app.py get site                  # mostra credencial descriptografada
python app.py edit site -u usuario      # altera senha existente
python app.py delete site -u usuario    # apaga por id
python app.py generate [tamanho]        # gera senha forte e imprime
```

---

## 6. Plano de Implementação (fases)

### Fase 1 — Setup
- Estrutura de pastas, `pyproject.toml`, `.gitignore`, commit inicial.

### Fase 2 — Model crypto
- Implementar PBKDF2 (senha → chave) e AES-GCM (cifrar/decifrar).
- Testes: cifra→decifra ok; senha errada falha; dado adulterado falha.

### Fase 3 — Model database
- Conexão SQLite, criação do schema, CRUD genérico.
- Testes com banco em memória (`:memory:`).

### Fase 4 — Model generator
- Gerador de senha forte (16–64 chars, `secrets`).
- Teste: comprimento, variedade de caracteres.

### Fase 5 — View cli
- Prompts, `getpass`, formatação de tabela (opcional: `rich`).

### Fase 6 — Controller
- `argparse`, `dispatch()` ligando Model + View, erros amigáveis.

### Fase 7 — Integração + instalação
- `pip install -e .` criando o comando global `gsenha`; README.

---

## 7. Material de Estudo (conceitos)

### Por que PBKDF2 e não um hash simples?
Hashs (MD5/SHA256) são rápidos demais — um atacante testa bilhões de senhas
por segundo. PBKDF2 repete a função 600.000 vezes, tornando cada tentativa
cara. Senhas de usuário (mestras) têm pouca entropia; por isso precisam de
funções de derivação **lentas** como PBKDF2, scrypt ou argon2.

### Por que o nonce precisa ser único?
No AES-GCM, reutilizar o mesmo nonce com a mesma chave permite que um
atacante recupere a chave. Por isso cada criptografia gera um nonce novo
via `get_random_bytes(12)`.

### Por que `secrets` e não `random`?
O módulo `random` usa um gerador pseudo-aleatório **previsível** (ótimo para
jogos, péssimo para segurança). `secrets` usa entropia do sistema operacional
e é próprio para criptografia e geração de senhas.

### Por que GCM em vez de CBC?
CBC é um modo de cifra em bloco sem autenticação — o conteúdo pode ser
alterado sem detecção (e historicamente sofreu ataques de "padding oracle").
GCM combina criptografia + autenticação: qualquer alteração/corrupção é
detectada na hora do `decrypt_and_verify`.

---

## 8. Checklist de cada fase

### Fase 2 (crypto)
- [ ] Deriva a mesma chave quando mesma senha + mesmo salt + mesmo nº iterações
- [ ] Chave diferente quando o salt muda
- [ ] `decifrar(cifrar(x)) == x`
- [ ] Senha mestra errada → exceção de autenticação
- [ ] Ciphertext adulterado (mudar 1 byte) → exceção de autenticação

### Fase 3 (database)
- [ ] Cria tabelas se não existirem
- [ ] Inserir, listar, atualizar, deletar funcionam
- [ ] Duplicata (site, usuario) é rejeitada
- [ ] Testes rodam com `:memory:` sem criar arquivos

### Fase 4 (generator)
- [ ] Comprimento respeitado
- [ ] Contém letras, números e símbolos
- [ ] Gerado com `secrets` (nunca `random`)

### Fase 5–6 (view/controller)
- [ ] `getpass` usado (senha não ecoa)
- [ ] `list` não descriptografa nada
- [ ] Comandos inválidos retornam mensagem amigável

---

## 9. Referência rápida de APIs (pycryptodome)

```python
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Derivação de chave
chave = PBKDF2(senha_mestra, salt, dkLen=32, count=600_000, hmac_hash_module=SHA256)

# Criptografia AES-GCM
cipher = AES.new(chave, AES.MODE_GCM)          # nonce gerado automaticamente
nonce, tag = cipher.nonce, cipher.digest        # cuidado: digest antes do encrypt
ciphertext = cipher.encrypt(dados)

# Descriptografia + verificação
cipher = AES.new(chave, AES.MODE_GCM, nonce=nonce)
dados = cipher.decrypt_and_verify(ciphertext, tag)   # falha se adulterado
```

> **Armadilha comum:** o `tag` deve ser obtido do cipher ANTES de fechar o
> objeto (ou após `encrypt`), pois o objeto mantém estado. Guarde
> `nonce`, `tag` e `ciphertext` juntos (nesta ordem) no BLOB.