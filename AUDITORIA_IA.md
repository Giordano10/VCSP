# 🛡️ Playbook de Segurança & Auditoria (Python/Backend)

Este documento contém cenários de ataque reais e como preveni-los.

## 🏴‍☠️ Red Team: Cenários de Ataque Comuns

### 1. SQL Injection
**❌ Inseguro:** `f"SELECT * FROM users WHERE user = '{u}'"`
**✅ Correto:** `cursor.execute("SELECT... WHERE user = %s", (u,))`

### 2. OS Command Injection
**❌ Inseguro:** `os.system(f"ping {ip}")`
**✅ Correto:** `subprocess.run(["ping", ip])`

### 3. XSS (Cross-Site Scripting)
**Risco:** Renderizar input do usuário sem escape em HTML.
**Solução:** Usar autoescape do framework ou limpar input.

## 📋 Checklist
- [ ] Segredos removidos (Use `python scan_project.py`)?
- [ ] Inputs sanitizados?
- [ ] Dependências seguras?