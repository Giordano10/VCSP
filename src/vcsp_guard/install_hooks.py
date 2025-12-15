import os
import sys
import stat
import subprocess
import shutil

HOOKS_DIR = ".git/hooks"
PRE_COMMIT_FILE = os.path.join(HOOKS_DIR, "pre-commit")
VIBE_CHECK_FILE = os.path.join(HOOKS_DIR, "vibe_check.py")
CURRENT_PYTHON = sys.executable.replace('\\', '/')

HOOK_BODY = r"""
import sys
import re
import subprocess  # nosec
import os

# Força UTF-8 no Windows para evitar erro de emoji (cp1252)
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

FORBIDDEN_PATTERNS = [
    (r"API_KEY\s*=", "Chave de API explícita"),
    (r"PASSWORD\s*=", "Senha explícita"),
    (r"SECRET\s*=", "Segredo explícito"),
    (r"sk-[a-zA-Z0-9]{20,}", "Chave OpenAI"),
    (r"ghp_[a-zA-Z0-9]{20,}", "Token GitHub"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"-----BEGIN [A-Z]+ PRIVATE KEY-----", "Chave Privada SSH/RSA"),
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "IP Interno (192.168.x.x) hardcoded"),
    (r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "IP Interno (10.x.x.x) hardcoded"),
]

def get_staged_files():
    try:
        result = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True)  # nosec
        return [f for f in result.splitlines() if os.path.exists(f)]
    except subprocess.CalledProcessError: return []

def scan_file(filepath):
    if "env.example" in filepath or "install_hooks.py" in filepath or "scan_project.py" in filepath: return False
    issues = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for pattern, msg in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        print(f"{RED}[BLOQUEADO] {filepath}:{i} -> {msg}{RESET}")
                        issues = True
    except Exception: pass  # nosec
    return issues

def main():
    print("{GREEN}🛡️  Vibe Security (Pre-commit): Checando Segredos...{RESET}")
    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)
    if any(scan_file(f) for f in staged_files):
        print("\n{RED}❌ COMMIT ABORTADO.{RESET} Use --no-verify se necessário.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__": main()
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def activate_ai_configs():
    vibe_path = os.path.join(BASE_DIR, ".vibe")
    if not os.path.exists(vibe_path):
        return

    print("\n🤖 Configuração de IA detectada (.vibe/).")
    print("Escolha quais ferramentas deseja ativar na raiz do projeto:")

    options = [
        ("Cursor (.cursorrules)", ".cursorrules"),
        ("Cline (.clinerules)", ".clinerules"),
        ("Qodo Gen (.codiumai.toml)", ".codiumai.toml"),
        ("GitHub Copilot/Actions (.github)", ".github"),
        ("Gemini (GEMINI.md)", "GEMINI.md"),
        ("Auditoria Geral (AUDITORIA_IA.md)", "AUDITORIA_IA.md")
    ]

    available = []
    for label, fname in options:
        if os.path.exists(os.path.join(vibe_path, fname)):
            available.append((label, fname))

    if not available:
        return

    for i, (label, _) in enumerate(available, 1):
        print("  {i}. {label}")
    print("  99. Limpar configurações (Remover da raiz)")
    print("  0. Sair")

    selection = input("\nDigite os números (ex: 1,3 (separe por virgulas caso queira mais de uma)): ").strip()
    if not selection or selection == '0':
        return

    if selection == '99':
        print("🧹 Limpando configurações da raiz...")
        for _, fname in options:
            if os.path.exists(fname):
                try:
                    if os.path.isdir(fname):
                        shutil.rmtree(fname)
                    else:
                        os.remove(fname)
                    print("🗑️  Removido: {fname}")
                except Exception as e:
                    print(f"❌ Erro ao remover {fname}: {e}")
        return

    print("🔄 Copiando...")
    for idx in [s.strip() for s in selection.split(',') if s.strip().isdigit()]:
        i = int(idx) - 1
        if 0 <= i < len(available):
            lbl, fname = available[i]
            src, dst = os.path.join(vibe_path, fname), fname
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                print("✅ Ativado: {lbl}")
            except Exception as e:
                print(f"❌ Erro: {e}")

def check_conflicts():
    if os.path.exists("test_sample.py") and os.path.exists("tests/test_sample.py"):
        try:
            os.remove("test_sample.py")
            print("🗑️  Conflito resolvido: test_sample.py removido da raiz.")
        except Exception:
            pass

def install():
    if not os.path.exists(".git"):
        print("❌ Erro: Rode 'git init' primeiro.")
        return
    if not os.path.exists(HOOKS_DIR):
        os.makedirs(HOOKS_DIR)
    
    with open(VIBE_CHECK_FILE, "w", encoding="utf-8") as f:
        f.write(HOOK_BODY)
    
    shell_content = '#!/bin/sh\n"{CURRENT_PYTHON}" "{VIBE_CHECK_FILE}" "$@"\n'
    with open(PRE_COMMIT_FILE, "w", encoding="utf-8", newline='\n') as f:
        f.write(shell_content)
    os.chmod(PRE_COMMIT_FILE, os.stat(PRE_COMMIT_FILE).st_mode | stat.S_IEXEC)
    
    print("✅ Vibe Security instalado usando: {CURRENT_PYTHON}")
    activate_ai_configs()
    check_conflicts()
    
    try:
        print("📦 Verificando ferramentas (Bandit, Pip-Audit, Ruff)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bandit", "pip-audit", "ruff"], stdout=subprocess.DEVNULL)
        print("✅ Todas as ferramentas de auditoria instaladas.")
    except Exception:
        print("⚠️ Aviso: Instale manualmente: pip install bandit pip-audit ruff")

if __name__ == "__main__":
    install()