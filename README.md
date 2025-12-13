# 🛡️ Vibe Coding Security Protocol (VCPS)

Template seguro para desenvolvimento ágil com IA (Vibe Coding).
Já vem configurado com **Scanner de Segredos**, **Pentest Lógico**, **Auditoria de Dependências** e **Controle de Qualidade**.

---

## 🚀 Como usar este Template

### 1. Iniciar um Novo Projeto
1. Clique no botão verde **"Use this template"** (topo da página).
2. Selecione **"Create a new repository"**.
3. Crie seu projeto.

### 2. Ativar a Proteção (Obrigatório)
O Git não baixa a proteção automaticamente. Assim que baixar seu novo projeto, rode:

```bash
python install_hooks.py
```

✅ **Pronto!** Hooks ativados e auditores instalados (Bandit, Pip-Audit, Ruff).

### 3. Configurar Ambiente
```bash
cp .env.example .env
# Edite o .env com suas chaves (ele já é ignorado pelo Git)
```

---

## 🤖 Automação de IA (Magic Files)

Este kit injeta regras de segurança e qualidade automaticamente na sua IA:

| Ferramenta | Arquivo | Função |
| :--- | :--- | :--- |
| **Cursor** | `.cursorrules` | Regras de segurança e estilo. |
| **Cline** | `.clinerules` | Agente autônomo com foco em qualidade. |
| **Qodo Gen** | `.codiumai.toml` | Testes focados em falhas e edge cases. |
| **Copilot** | `.github/...` | Instruções globais. |

---

## 🕵️ Varredura Completa (The Quality Gate)

O script `scan_project.py` executa 4 camadas de verificação:

1.  **🔐 Segredos:** Busca por chaves vazadas no código.
2.  **🔫 Pentest (Bandit):** Busca por falhas de lógica e injeção.
3.  **📦 SCA (Pip Audit):** Busca por bibliotecas desatualizadas/vulneráveis.
4.  **🧹 Linter (Ruff):** Busca por bugs, variáveis não usadas e código sujo.

Para rodar tudo:
```bash
python scan_project.py
```

---

## 🧪 Como testar se a segurança funciona?

Este kit gera automaticamente um arquivo chamado `vulnerable_test_DO_NOT_DEPLOY.py`.
Ele é um "arquivo armadilha" cheio de falhas propositais (Senhas, SQL Injection, Eval).

1.  Rode o scanner: `python scan_project.py`
2.  **Resultado Esperado:** O terminal deve ficar VERMELHO, apontando múltiplos erros neste arquivo. Isso prova que o sistema funciona.
3.  **Ação:** Após o teste, **APAGUE** esse arquivo imediatamente:
    ```bash
    rm vulnerable_test_DO_NOT_DEPLOY.py
    ```

---

## 🚨 PROTOCOLO DE PÂNICO
Se vazou chave: **REVOGUE** imediatamente no painel do fornecedor.

## 🚨 Bypass
Se o hook bloquear algo legítimo: `git commit -m "msg" --no-verify`

---

## 👨‍💻 Sobre o Mantenedor

Este projeto foi criado e é mantido por **Giordano Alves**, Desenvolvedor Backend Python especialista em Infraestrutura, Linux e Segurança.

O objetivo deste template é permitir que desenvolvedores usem o poder da IA ("Vibe Coding") sem sacrificar a solidez e a segurança da engenharia de software tradicional.

> *"Codifique na velocidade da luz, mas com a segurança de um cofre."*