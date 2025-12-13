# 🛡️ Vibe Coding Security Protocol (VCPS)

Bem-vindo! Este é um **Template de Segurança** para quem desenvolve com ajuda de Inteligência Artificial (ChatGPT, Claude, Gemini, Cursor).

O objetivo deste projeto é garantir que, mesmo programando rápido com IA, seu código não tenha **senhas vazadas**, **falhas de segurança** ou **bugs críticos**.

---

## 🐣 Como começar (Passo a Passo para Iniciantes)

Siga estes passos exatos para criar seu projeto com segurança máxima.

### 1️⃣ Criar o Repositório no GitHub
Não clone este template diretamente! Use-o como base:
1.  Olhe para o topo desta página, no canto direito.
2.  Clique no botão verde **"Use this template"**.
3.  Escolha a opção **"Create a new repository"**.
4.  Dê um nome ao seu novo projeto (Ex: `meu-projeto-python`) e crie.

### 2️⃣ Baixar para seu Computador
Agora, no **seu** novo repositório que acabou de criar:
1.  Clique no botão verde **Code**.
2.  Copie o link HTTPS.
3.  Abra seu terminal (ou Git Bash) e digite:
    ```bash
    git clone SEU_LINK_AQUI
    cd nome-do-seu-projeto
    ```

### 3️⃣ Configurar o Ambiente Python (Opcional, mas Recomendado)
Para não bagunçar seu computador, crie um ambiente isolado:

**No Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

*(Se aparecer `(venv)` no começo da linha do terminal, funcionou!)*

### 4️⃣ Ativar a Segurança (MUITO IMPORTANTE 🚨)
O Git não baixa a proteção de senhas automaticamente. Você precisa ativá-la uma única vez.
Rode este comando na raiz do projeto:

```bash
python install_hooks.py
```

✅ **Se aparecer "Vibe Security instalado":** Parabéns! Agora, se você tentar salvar (commitar) um código com senha exposta, o sistema vai te bloquear automaticamente.

### 5️⃣ Configurar suas Senhas
Nunca coloque senhas no código. Use o arquivo `.env`.
1.  Copie o exemplo:
    ```bash
    cp .env.example .env
    # No Windows: copy .env.example .env
    ```
2.  Abra o arquivo `.env` no seu editor (VS Code).
3.  Coloque suas chaves reais lá.
    * *Nota:* O arquivo `.env` é ignorado pelo Git, então suas senhas nunca subirão para a internet.

---

## 🤖 Como usar com a IA?

Este kit já vem configurado para "ensinar" a IA a ser segura.

* **Se usa Cursor:** Ele lerá automaticamente o arquivo `.cursorrules`.
* **Se usa Gemini/ChatGPT/Perplexity:**
    Copie o conteúdo do arquivo `AUDITORIA_IA.md` e cole no chat antes de pedir código. Exemplo:
    > "Estou começando um projeto. Use as regras abaixo para garantir segurança: [Cole o texto aqui]"

---

## 🚨 O que fazer se o Git bloquear meu Commit?

Se você tentar dar `git commit` e aparecer uma mensagem **VERMELHA** dizendo `COMMIT ABORTADO`, o "guardião" funcionou!

1.  Leia a mensagem de erro. Ela vai dizer em qual arquivo e linha está a senha.
2.  Remova a senha do código e coloque no `.env`.
3.  Tente commitar de novo.

**"Mas é um alarme falso!"**
Se o bloqueio for em um número que *parece* cartão de crédito mas não é, force o envio:
```bash
git commit -m "mensagem" --no-verify
```

---

## 🗑️ Auditoria: "Será que já vazei algo?"

Se você está usando este template em um código que já existia, rode o scanner para procurar falhas antigas:

```bash
python scan_project.py
```

Se ele encontrar algo vermelho:
1.  **Não apague apenas.** A senha já está no histórico.
2.  Vá no site do serviço (AWS, OpenAI) e **cancele (revogue)** a chave.
3.  Gere uma nova.

---
*Template criado para garantir Vibe Coding seguro.*