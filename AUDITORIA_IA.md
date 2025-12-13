# 🛡️ Playbook de Segurança & Pentest

Este documento ensina como simular ataques no seu próprio código.

## 🧠 Prompt para Simulação de Pentest (Copie e cole na IA)

> "Atue como um Pentester Sênior. Analise o código abaixo procurando vulnerabilidades OWASP Top 10 (Injection, Broken Access Control, SSRF). Não apenas corrija, mas me explique como um atacante exploraria essa falha específica. Tente 'quebrar' minha lógica."

## 🏴‍☠️ Cenários de Ataque Comuns (O que o Bandit procura)

### 1. Execução de Código Arbitrário (RCE)
**❌ Vulnerável:**
```python
import os
user_input = input()
os.system("echo " + user_input) # Perigo! Se digitar "; rm -rf /"
```
**✅ Seguro:** `subprocess.run(["echo", user_input])`

### 2. Uso de Criptografia Fraca
**❌ Vulnerável:** `hashlib.md5(b"senha")` (MD5 é quebrado)
**✅ Seguro:** `hashlib.sha256(b"senha")` ou `bcrypt`

### 3. Bind para todas as interfaces
**❌ Vulnerável:** `app.run(host='0.0.0.0')` (Expõe para a rede toda em dev)
**✅ Seguro:** `app.run(host='127.0.0.1')`

## 📋 Checklist Manual
- [ ] Rodei o `python scan_project.py` (Bandit)?
- [ ] Testei inputs com caracteres especiais (`'`, `"`, `;`, `--`)?