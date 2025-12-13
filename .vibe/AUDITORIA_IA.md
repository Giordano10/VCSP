# 🛡️ Playbook de Segurança & Qualidade

## 🏴‍☠️ O que os Scanners Procuram?

### 1. Bandit (Segurança)
* `exec()`, `eval()`, `os.system()`
* Senhas hardcoded
* Criptografia fraca (MD5)

### 2. Pip-Audit (Dependências)
* Bibliotecas com CVEs conhecidos (ex: Log4j, requests antigos).

### 3. Ruff (Qualidade/Bugs)
* **F841:** Variável local atribuída mas nunca usada.
* **F401:** Importado mas não usado.
* **E722:** `except:` vazio (sem especificar o erro).