# 🛡️ VCSP Guard (Vibe Coding Security Protocol)

![CI Status](https://github.com/Giordano10/VCSP/actions/workflows/security_scan.yml/badge.svg)
![Latest Release](https://img.shields.io/github/v/release/Giordano10/VCSP)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Security](https://img.shields.io/badge/security-bandit%20%7C%20pip--audit%20%7C%20semgrep-red)

**VCSP Guard** é a camada de segurança definitiva para o desenvolvimento ágil com IA ("Vibe Coding").
Ele atua como um **Engenheiro de Segurança Sênior automatizado**, auditando cada linha de código gerada por LLMs (como GPT-4, Claude, Copilot) em busca de vulnerabilidades, segredos expostos e falhas de infraestrutura. Já vem configurado com **Scanner de Segredos**, **Pentest Lógico**, **Auditoria de Dependências**, **Quality Gate**, **Análise de IaC** e **Histórico de Logs**.

---

## 🚀 Funcionalidades (Tech Stack)

No mundo de hoje, com a crescente adoção das Inteligências Artificiais, muitos projetos ganharam um boost na produção e no lançamento de features. Porém, nem todo mundo está preocupado com a manutenção e segurança do próprio código, podendo ficar vulnerável caso não haja um revisor experiente para encontrar brechas que podem ser exploradas por atacantes. O VCSP orquestra as melhores ferramentas de mercado em um fluxo unificado:

**Foi pensando nisso que criei essa ferramenta:** ela vai varrer seu código, seja ele criado por IA ou não, em busca dessas potenciais falhas, atuando como uma camada de segurança automatizada.

| Ferramenta         | Tipo         | O que ela protege? |
| :---               | :---         | :--- |
| **Ruff**           | Linter/SAST  | Qualidade de código, bugs e segurança lógica (substitui Bandit/Flake8). |
| **Pip-Audit**      | SCA          | Verifica se suas dependências possuem vulnerabilidades conhecidas (CVEs). |
| **Semgrep**        | IaC/SAST     | Varredura profunda em Dockerfiles, Terraform e padrões complexos. |
| **Secrets**        | Regex        | Bloqueia chaves de API, tokens e senhas antes do commit. |
| **Detect-secrets** | SAST/Secrets | Detecção avançada de segredos (entropia, padrões de chaves, tokens, falsos positivos reduzidos). |
| **CWE Top 25 (Semgrep)** | SAST      | Varredura de vulnerabilidades do tipo CWE Top 25 (as 25 falhas mais críticas de software segundo o padrão CWE, usando Semgrep). |

---

## 📦 Instalação e Uso

### 1. Instalação Via PyPI (Recomendado)
Instale a biblioteca oficial via pip em seu ambiente virtual:

```bash
pip install vcsp-guard
```

### 2. Inicialização (Ativar Proteção)
Na raiz do seu projeto, execute o comando de inicialização. Isso configurará os hooks do Git e copiará os arquivos de configuração de IA necessários.

```bash
vcsp-init
```

**Nota importante:**  
Se você selecionar a opção **4. Github Copilot/Action (.github)** durante a configuração, o VCSP irá instalar tanto os workflows do GitHub Actions para varredura automática do código (usando o `vcsp-scan`), quanto as regras de instrução para o Copilot (arquivo `copilot-instructions.md`).  
Caso você utilize outra IA para codificar, basta excluir o arquivo `copilot-instructions.md` e rodar novamente o comando `vcsp-init`, selecionando a IA desejada conforme a lista apresentada.

**O que o `vcsp-init` faz?**
1.  **Instala o Pre-Commit Hook:** Cria um arquivo oculto em `.git/hooks/` que intercepta todo comando `git commit`.
2.  **Configura o Ambiente:** Verifica se você tem as ferramentas de auditoria (Bandit, Ruff, Pip-Audit, Semgrep) e as instala se necessário.
3.  **Menu de Seleção de IA:** Pergunta qual IA você utiliza (Cursor, Cline, etc.) e aplica as regras de segurança correspondentes.

### 3. Configurar Ambiente
Crie um arquivo `.env` para suas variáveis de ambiente:

```bash
cp .env.example .env
# Edite o .env com suas chaves (ele já é ignorado pelo Git)
```

---

## 🤖 Automação de IA (Magic Files)

As configurações de IA e CI/CD estão organizadas na pasta **`.vibe/`** para manter a raiz limpa.
**Se você rodou o `vcsp-init` (Passo 2), a configuração da sua IA já foi aplicada automaticamente!**

Caso queira trocar de IA ou configurar manualmente, basta rodar novamente o `vcsp-init`, e selecionar a opção correspondente a IA que está usando. Caso queira excluir o arquivo de configuração da raiz, rode o `vcsp-init` e selecione a opção 99 para limpar os arquivos da raiz.

> **⚠️ Nota:** Lembre-se de adicionar o arquivo de configuração da sua IA (ex: `.cursorrules`, `.clinerules`) ao seu `.gitignore` caso não queira que ele suba para o GitHub junto com o projeto.

| Ferramenta | Arquivo (em .vibe/) | Função |
| :--- | :--- | :--- |
| **Cursor** | `.cursorrules` | Regras de segurança e estilo. |
| **Cline** | `.clinerules` | Agente autônomo com foco em qualidade. |
| **Qodo Gen** | `.codiumai.toml` | Testes focados em falhas e edge cases. |
| **Copilot** | `.github/...` | Instruções globais. |
| **Gemini** | `GEMINI.md` | Prompt otimizado para Google AI Studio / Vertex AI. |
| **GitHub** | `.github/workflows` | CI/CD Pipeline. |

### 🧠 ChatGPT, Perplexity & Claude
Para IAs de chat que não aceitam arquivos de configuração (como ChatGPT ou Perplexity), copie o conteúdo de **`.vibe/AUDITORIA_IA.md`** (System Prompt) e cole no início da conversa.

Isso garante que a IA siga as mesmas regras de segurança e estilo do restante do projeto.

---

## ⚡ O Fluxo de Trabalho (Vibe Coding)

Como este kit protege você enquanto a IA codifica?

1.  **Você pede:** "Crie uma conexão com o banco AWS." (no Cursor/Copilot/ChatGPT).
2.  **A IA gera:** Um código funcional, mas coloca a `AWS_ACCESS_KEY` direto no arquivo python.
3.  **Você commita:** `git commit -m "add db connection"`
4.  **O Guardião Atua:** O hook (instalado no passo 2) intercepta o commit **antes** dele ser salvo.
5.  **Bloqueio:** O terminal exibe: `❌ [BLOQUEADO] AWS Access Key encontrada`.
6.  **Correção:** Você move a chave para o `.env` (como deve ser) e tenta de novo.

**Resultado:** Você codifica na velocidade da IA, mas com a segurança de um sênior revisando cada linha em tempo real.

---

## 🕵️ Varredura e Histórico (Scanner)

**Para que serve o `vcsp-scan`?**
Enquanto o `vcsp-init` protege o futuro (novos commits), o `vcsp-scan` protege o passado. Ele serve para **varredura todo o código que já existe no projeto** em busca de vulnerabilidades antigas que passaram despercebidas.

O script `vcsp-scan` executa 7 camadas de verificação e **salva tudo na pasta `logs_scan_vcsp/`**:

1.  **Busca de Segredos:** Identifica chaves de API, tokens e senhas hardcoded (Regex).
2.  **Segurança Lógica (SAST):** Analisa vulnerabilidades no código Python usando **Ruff** (regras de segurança `S`).
3.  **Auditoria de Dependências (SCA):** Verifica vulnerabilidades conhecidas (CVEs) nas bibliotecas instaladas usando **Pip-Audit**.
4.  **Qualidade de Código:** Linting e padronização PEP 8 via **Ruff**.
5.  **Infraestrutura como Código (IaC):** Escaneia arquivos Docker, Kubernetes e Terraform usando **Semgrep**.
6.  **CWE Top 25:** Varredura de vulnerabilidades do tipo CWE Top 25 (as 25 falhas mais críticas de software segundo o padrão CWE, usando Semgrep).
7.  **Dependências Não Utilizadas:** Verifica se as libs do `requirements.txt` são realmente importadas no projeto.

**Como o Pip-Audit obtém os CVEs?**  
O Pip-Audit não carrega uma lista fixa dentro do VCSP. Ele consulta fontes oficiais de vulnerabilidades (como o **PyPI Advisory Database** e o serviço **OSV**) em tempo de execução, baixando os avisos e mantendo um cache local quando disponível. Em execuções seguintes, ele reaproveita o cache e atualiza os dados quando necessário.

> **⚠️ Usuários Windows:** Para a análise de infraestrutura (Docker/Terraform) e CWE Top 25, é necessário ter o **Docker Desktop** instalado e rodando. O VCSP detecta automaticamente e usa um container para realizar a varredura, já que o Semgrep não roda nativamente no Windows.

Para rodar a auditoria:
```bash
vcsp-scan
```

## MANUAL DE COMANDOS

### Comandos principais

- `vcsp-init`  
  Inicializa o ambiente de segurança, instala hooks de pré-commit e configurações de IA.

- `vcsp-scan`  
  Realiza uma varredura completa de segurança no projeto, incluindo busca de segredos, análise lógica, auditoria de dependências, qualidade de código, IaC e dependências não utilizadas.

- `vcsp-stats`  
  Gera gráficos e estatísticas de segurança com base nos logs de varredura.

### Flags do comando `vcsp-scan`

- `--all`  
  Varredura completa em todos os arquivos e pastas do projeto, incluindo arquivos ignorados e ocultos.
  ```bash
  vcsp-scan --all
  ```

- `--local`  
  Varredura apenas na pasta atual, sem considerar a raiz do projeto.
  ```bash
  vcsp-scan --local
  ```

- `--deps <arquivo>`  
  Permite informar um arquivo de dependências personalizado para auditoria, caso você utilize um nome diferente de `requirements.txt` ou `requirements-dev.txt`.
  ```bash
  vcsp-scan --deps minhas_dependencias.txt
  ```

- `--help`  
  Exibe a lista de comandos e flags disponíveis no terminal.

### 📊 Gráficos e Estatísticas

Para incluir a geração de gráficos (estatísticas):

```bash
pip install "vcsp-guard[stats]"
```

Para visualizar a evolução da segurança do seu projeto (Bug Trend), você pode gerar o gráfico localmente baseado nos logs de varredura.


```bash
vcsp-stats
```

Isso irá:
1. Ler o histórico da pasta `logs/`.
2. Gerar um gráfico em `.vibe/assets/bug_trend.png`.

� **Confira seu progresso:** Abra a pasta `logs/` para ver o histórico de correções e garantir que você não está repetindo erros antigos.

### 📅 Relatório Semanal Automático
O VCSP já vem configurado para rodar uma auditoria completa **toda segunda-feira às 08:00 UTC** via GitHub Actions.

*   **Objetivo:** Gerar um relatório de tudo que foi produzido na semana anterior.
*   **Benefício:** Permite que você revise e corrija dívidas técnicas ou de segurança antes de iniciar o novo ciclo de desenvolvimento.

## 📊 Auditorias e Gráficos de Segurança

O VCSP realiza as seguintes verificações automáticas em cada execução:

- **Busca de segredos via Regex** (chaves, tokens, senhas)
- **Detect-secrets** (detecção avançada de segredos, incluindo entropia e padrões de chaves)
- **Bandit (Logic)**: Análise de vulnerabilidades lógicas em Python.
- **Pip-Audit (Deps)**: Auditoria de vulnerabilidades em dependências (CVE).
- **Ruff (Lint)**: Linting e checagem de boas práticas.
- **Semgrep (IaC)**: Análise de infraestrutura como código (Dockerfile, Terraform, K8s).
- **CWE (Top 25)**: Varredura de vulnerabilidades do tipo CWE Top 25 (Semgrep).

O gráfico abaixo mostra a tendência das vulnerabilidades encontradas por cada ferramenta ao longo do tempo:


![Bug Trend](.vibe/assets/bug_trend.png?v=20260305001317)

---

## 🤖 Monitoramento de Dependências (Dependabot)

A segurança de um projeto não depende apenas do seu código, mas também das bibliotecas que você utiliza. O **Dependabot** atua como um vigia silencioso, monitorando constantemente o ecossistema Python em busca de atualizações de segurança para as dependências listadas no seu projeto.

O VCSP Guard já vem com workflows configurados para integrar o Dependabot, garantindo que você receba alertas e correções automáticas (Pull Requests) sempre que uma vulnerabilidade for descoberta em uma biblioteca externa.

👉 **Aprofunde-se:** [Leia nossa documentação sobre a estratégia do Dependabot](DEPENDABOT_NOTE.md)

## 🚨 PROTOCOLO DE PÂNICO (Vazamento de Credenciais)

Se você acidentalmente comitou uma chave de API ou senha:

1.  **REVOGUE** a chave imediatamente no painel do fornecedor (AWS, OpenAI, etc).
2.  **NÃO** tente apenas apagar o arquivo e comitar de novo (o histórico do Git mantém o segredo).
3.  Rotacione todas as credenciais que possam ter sido expostas.

## 🔓 Bypass (Ignorar Verificações)

Se o hook bloquear um arquivo legítimo (falso-positivo) ou você precisar forçar um commit urgente:

```bash
git commit -m "mensagem" --no-verify
```

> **Aviso:** Isso desativa todas as verificações de segurança para aquele commit.

---

## 🤝 Contribuições e Novas IAs

Caso queira sugerir arquivos de configuração para outras IAs, mande um email para **giordano.alves9@gmail.com**, ou submeta uma PR solicitando a criação de mais modelos de IA para esse projeto.

---

## 👨‍💻 Sobre o Mantenedor

Este projeto foi criado e é mantido por **Giordano Alves**, Desenvolvedor Backend Python especialista em Infraestrutura, Linux e Segurança.

O objetivo deste template é permitir que desenvolvedores usem o poder da IA ("Vibe Coding") sem sacrificar a solidez e a segurança da engenharia de software tradicional.

> *"Codifique na velocidade da luz, mas com a segurança de um cofre."*

> **Nota Importante:**  
> Como o **vcsp-guard** é uma biblioteca de varredura e segurança de código, **não é necessário listá-la nos arquivos de dependências** (`requirements.txt`, `pyproject.toml`, etc.), pois isso tornaria o projeto no GitHub desnecessariamente pesado.  
> O vcsp-guard é recomendado para uso local, durante o desenvolvimento.  
> Caso queira que seu projeto seja varrido automaticamente via CI/CD, basta rodar `vcsp-init` e escolher a opção correspondente aos **Actions do GitHub**. Assim, o `vcsp-scan` fará a varredura do seu projeto em uma máquina Linux via GitHub Actions, sem precisar incluir a biblioteca nas dependências do seu projeto.
