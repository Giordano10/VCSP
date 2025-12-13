# 🛡️ Vibe Coding Starter Kit (Template Oficial)

Template seguro para desenvolvimento ágil com IA (Vibe Coding).
Já vem configurado com **Contexto Automático para IA**, **Proteção de Commit** e **CI/CD**.

---

## 🚀 Como usar este Template

### 1. Iniciar um Novo Projeto
1. Clique no botão verde **"Use this template"** (topo da página).
2. Selecione **"Create a new repository"**.
3. Crie seu projeto.

### 2. Ativar a Proteção (Obrigatório)
O Git não baixa a proteção de senhas automaticamente.
Assim que baixar seu novo projeto, rode no terminal:

```bash
python install_hooks.py
```

✅ **Pronto!** Seu repositório agora bloqueia senhas localmente.

### 3. Configurar Ambiente
```bash
cp .env.example .env
# Edite o .env com suas chaves (ele já é ignorado pelo Git)
```

---

## 🤖 Automação de IA (Como funciona)

Este kit injeta regras de segurança automaticamente na sua IA. **Você NÃO precisa copiar textos manualmente** se usar as ferramentas suportadas:

| Ferramenta | Onde a mágica acontece | Como usar |
| :--- | :--- | :--- |
| **Cursor** | `.cursorrules` | **Automático.** O Cursor lê esse arquivo oculto antes de responder qualquer chat. |
| **GitHub Copilot** | `.github/copilot-instructions.md` | **Automático.** O Copilot usa esse arquivo como instrução de sistema em todo o projeto. |
| **Gemini Code Assist** | `GEMINI.md` | **Automático (Agent Mode).** Se ele não ler, cite `@GEMINI.md` no prompt inicial. |

### 🧠 Usando com IAs de Navegador (ChatGPT / Perplexity)
Como essas ferramentas não têm acesso direto aos arquivos do seu projeto:
1. Abra o arquivo `AUDITORIA_IA.md`.
2. Copie o conteúdo ou anexe o arquivo no chat.
3. Diga: *"Use estas regras de segurança para criar o código..."*

---

## 🛡️ Ferramentas de Defesa

| Ferramenta | Comando | Função |
| :--- | :--- | :--- |
| **Hook Local** | `git commit` | Bloqueia commits com chaves/senhas expostas. |
| **Scanner** | `python scan_project.py` | Varre todo o projeto em busca de falhas antigas. |
| **CI/CD** | (Automático) | Roda o scanner a cada `git push` no GitHub. |

---

## 🚨 PROTOCOLO DE PÂNICO: Vazou uma chave?

Se você (ou um colega) comitou uma chave e ela foi para o GitHub:

1.  🛑 **NÃO tente apenas apagar a linha no código.**
2.  🔥 **Considere a chave QUEIMADA.**
3.  **Ação Imediata:** Revogue (delete) a chave no painel do fornecedor e gere uma nova.

## 🚨 Bypass (Falsos Positivos)
Se o hook bloquear algo legítimo (ex: ID numérico longo):
```bash
git commit -m "mensagem" --no-verify
```