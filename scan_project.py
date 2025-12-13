import os
import re
import sys
import subprocess
import shutil

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

IGNORED_DIRS = {
    '.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules', 
    '.idea', '.vscode', 'build', 'dist', 'target', '.github'
}

FORBIDDEN_PATTERNS = [
    (r"API_KEY\s*=", "Chave de API explícita"),
    (r"PASSWORD\s*=", "Senha explícita"),
    (r"SECRET\s*=", "Segredo explícito"),
    (r"sk-[a-zA-Z0-9]{20,}", "Chave OpenAI"),
    (r"ghp_[a-zA-Z0-9]{20,}", "Token GitHub"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"-----BEGIN [A-Z]+ PRIVATE KEY-----", "Chave Privada SSH/RSA"),
]

def check_bandit_installed():
    return shutil.which("bandit") is not None

def run_bandit():
    print(f"\n{BOLD}🔫 Executando Análise Lógica (Bandit)...{RESET}")
    if not check_bandit_installed():
        print(f"{YELLOW}⚠️  Bandit não encontrado.{RESET}")
        print("Para detectar falhas de lógica (eval, exec, crypto), instale:")
        print(f"{BOLD}pip install bandit{RESET}\n")
        return False
    
    # Roda o bandit recursivamente (-r) no diretório atual (.)
    # -ll: mostra severidade média e alta
    # -q: modo silencioso (só erros)
    # -f custom: formatação personalizada (opcional, aqui usaremos txt padrão)
    try:
        # Exclui pastas de teste e venv
        subprocess.run(
            ["bandit", "-r", ".", "-ll", "-x", "venv,.venv,tests,test"], 
            check=True
        )
        print(f"{GREEN}✅ Nenhum problema lógico grave encontrado pelo Bandit.{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"\n{RED}⛔ O BANDIT ENCONTROU VULNERABILIDADES DE CÓDIGO!{RESET}")
        print("Verifique o relatório acima e corrija as falhas de lógica.")
        return False

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if len(line) > 500: continue
                for pattern, msg in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        issues.append((i, msg, line.strip()))
    except: pass
    return issues

def main():
    print(f"{BOLD}🔍 Vibe Security Scan (Secrets + Pentest Logic){RESET}")
    
    # 1. Busca por Segredos (Regex)
    root_dir = os.getcwd()
    files_with_issues = 0
    print(f"1️⃣  Buscando chaves hardcoded...")

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            if file in ["scan_project.py", "install_hooks.py", "setup_vibe_kit.py"]: continue
            filepath = os.path.join(root, file)
            issues = scan_file(filepath)
            if issues:
                files_with_issues += 1
                rel_path = os.path.relpath(filepath, root_dir)
                print(f"{RED}❌ [SEGREDO] {rel_path}{RESET}")
                for line_num, msg, content in issues:
                    print(f"   L.{line_num}: {msg}")

    secrets_ok = (files_with_issues == 0)
    if secrets_ok:
        print(f"{GREEN}✅ Nenhuma chave encontrada.{RESET}")
    else:
        print(f"{RED}⛔ Foram encontradas chaves expostas.{RESET}")

    # 2. Busca por Vulnerabilidades de Lógica (Bandit)
    bandit_ok = run_bandit()

    if not secrets_ok or not bandit_ok:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()