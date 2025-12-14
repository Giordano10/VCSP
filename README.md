# 🛡️ Vibe Coding Security Protocol (VCPS)

![CI Status](https://github.com/Giordano10/VCSP/actions/workflows/security_scan.yml/badge.svg)
![Latest Release](https://img.shields.io/github/v/release/Giordano10/VCSP)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Security](https://img.shields.io/badge/security-bandit%20%7C%20pip--audit-red)

Template seguro para desenvolvimento ágil com IA (Vibe Coding).
Já vem configurado com **Scanner de Segredos**, **Pentest Lógico**, **Auditoria de Dependências**, **Quality Gate** e **Histórico de Logs**.

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

✅ **Pronto!** Hooks ativados e ferramentas instaladas (Bandit, Pip-Audit, Ruff).

### 3. Configurar Ambiente
```bash
cp .env.example .env
# Edite o .env com suas chaves (ele já é ignorado pelo Git)
```

---

## 🤖 Automação de IA (Magic Files)

As configurações de IA e CI/CD estão organizadas na pasta **`.vibe/`** para manter a raiz limpa.
Para ativar uma ferramenta, copie seu arquivo para a raiz do projeto.

| Ferramenta | Arquivo (em .vibe/) | Função |
| :--- | :--- | :--- |
| **Cursor** | `.cursorrules` | Regras de segurança e estilo. |
| **Cline** | `.clinerules` | Agente autônomo com foco em qualidade. |
| **Qodo Gen** | `.codiumai.toml` | Testes focados em falhas e edge cases. |
| **Copilot** | `.github/...` | Instruções globais. |
| **GitHub** | `.github/workflows` | CI/CD Pipeline. |

---

## 🕵️ Varredura e Histórico (Scanner)

O script `scan_project.py` executa 4 camadas de verificação e **salva tudo na pasta `logs/`**:

1.  **🔐 Segredos:** Busca por chaves vazadas no código.
2.  **🔫 Pentest (Bandit):** Busca por falhas de lógica e injeção.
3.  **📦 SCA (Pip Audit):** Busca por bibliotecas desatualizadas/vulneráveis.
4.  **🧹 Linter (Ruff):** Busca por bugs, variáveis não usadas e código sujo.

Para rodar a auditoria:
```bash
python scan_project.py
```

📂 **Confira seu progresso:** Abra a pasta `logs/` para ver o histórico de correções e garantir que você não está repetindo erros antigos.

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