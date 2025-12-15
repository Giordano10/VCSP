# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - Lançamento Oficial

### 🚀 Novidades
- **Automação de Release:** Workflow configurado para gerar releases e changelogs automáticos com Git Cliff.
- **Relatório Semanal:** Scan de segurança agendado (CRON) com gráfico de tendência de bugs (`bug_trend.png`).
- **Instalação Inteligente:** `install_hooks.py` agora possui menu interativo para seleção de IA e resolução de conflitos.
- **Gráficos:** Geração automática de histórico de vulnerabilidades na pasta `.vibe/assets`.

### 📚 Documentação
- **README Completo:** Novas seções sobre "Protocolo de Pânico", "Bypass", "Fluxo Vibe Coding" e "Menu de Seleção".
- **Badges:** Adicionado indicador de Latest Release.
- **Guias:** Instruções claras para uso com ChatGPT, Perplexity e Claude.

### ⚙️ Configuração & Segurança
- **System Prompts:** Regras de segurança reforçadas para Cursor, Gemini e Copilot (Secrets, Bandit, Ruff).
- **Testes (CodiumAI):** Configuração otimizada para Pytest com foco em injeção de SQL e XSS.
- **Auditoria:** `AUDITORIA_IA.md` atualizado com checklist técnico de AppSec.