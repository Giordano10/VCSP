import os
import sys
import stat
import subprocess

HOOKS_DIR = ".git/hooks"
PRE_COMMIT_FILE = os.path.join(HOOKS_DIR, "pre-commit")
CURRENT_PYTHON = sys.executable

HOOK_BODY = r"""
import sys
import re
import subprocess
import os

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
        result = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True)
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
    except: pass
    return issues

def main():
    print(f"{GREEN}🛡️  Vibe Security (Pre-commit): Checando Segredos...{RESET}")
    staged_files = get_staged_files()
    if not staged_files: sys.exit(0)
    if any(scan_file(f) for f in staged_files):
        print(f"\n{RED}❌ COMMIT ABORTADO.{RESET} Use --no-verify se necessário.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__": main()
"""

def install():
    if not os.path.exists(".git"):
        print("❌ Erro: Rode 'git init' primeiro.")
        return
    if not os.path.exists(HOOKS_DIR): os.makedirs(HOOKS_DIR)
    
    final_content = f"#!{CURRENT_PYTHON}\n{HOOK_BODY}"
    with open(PRE_COMMIT_FILE, "w", encoding="utf-8") as f: f.write(final_content)
    os.chmod(PRE_COMMIT_FILE, os.stat(PRE_COMMIT_FILE).st_mode | stat.S_IEXEC)
    
    print(f"✅ Vibe Security instalado usando: {CURRENT_PYTHON}")
    try:
        print("📦 Verificando dependências de auditoria (Bandit)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bandit"], stdout=subprocess.DEVNULL)
        print("✅ Bandit pronto para uso.")
    except:
        print("⚠️ Aviso: Não foi possível instalar o Bandit automaticamente. Rode 'pip install bandit'.")

if __name__ == "__main__": install()