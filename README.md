# 🛡️ Vibe Coding Security Protocol (VCPS)

Template seguro para desenvolvimento ágil com IA (Vibe Coding).
Já vem configurado com **Contexto Automático**, **Análise de Vulnerabilidades (SAST)** e **Proteção de Commit**.

---

## 🚀 Como usar este Template

### 1. Iniciar um Novo Projeto
1. Clique no botão verde **"Use this template"**.
2. Selecione **"Create a new repository"**.

### 2. Instalar Dependências de Segurança (NOVO 🟢)
Para realizar a varredura profunda (Pentest Lógico), instale o Bandit:

```bash
pip install -r requirements-dev.txt
python install_hooks.py
```

### 3. Configurar Ambiente
```bash
cp .env.example .env
```

---

## 🕵️ Varredura de Pentest (Como testar)

Agora você tem dois níveis de verificação:

1.  **Scanner de Segredos (Básico):** Procura chaves vazadas.
2.  **Bandit (Avançado):** Procura falhas de lógica (SQL Injection, Eval, Criptografia fraca).

Para rodar ambos:
```bash
python scan_project.py
```

---

## 🤖 Automação de IA

| Ferramenta | Arquivo | Função |
| :--- | :--- | :--- |
| **Cursor** | `.cursorrules` | Lê regras de segurança automaticamente. |
| **Cline** | `.clinerules` | Agente de defesa ativo. |
| **Qodo Gen** | `.codiumai.toml` | Gera testes de invasão. |
| **Gemini/GPT** | `AUDITORIA_IA.md` | Copie o prompt "Red Team" deste arquivo. |

---

## 🚨 PROTOCOLO DE PÂNICO
Se vazou chave: **REVOGUE** no painel do fornecedor imediatamente. Não basta apagar do Git.

---

## 👨‍💻 Sobre o Mantenedor
Criado e mantido por **Giordano Alves**, especialista em Backend Python, Infra e Segurança.
> *"Codifique na velocidade da luz, mas com a segurança de um cofre."*