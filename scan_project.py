import os
import re
import sys

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
    (r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "IP Interno (192.168.x.x) hardcoded"),
    (r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "IP Interno (10.x.x.x) hardcoded"),
]

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
    print(f"{BOLD}🔍 Vibe Security Scan (Retroactive){RESET}")
    root_dir = os.getcwd()
    files_with_issues = 0

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            if file in ["scan_project.py", "install_hooks.py", "setup_vibe_kit.py"]: continue
            filepath = os.path.join(root, file)
            issues = scan_file(filepath)
            if issues:
                files_with_issues += 1
                rel_path = os.path.relpath(filepath, root_dir)
                print(f"{RED}❌ [FALHA] {rel_path}{RESET}")
                for line_num, msg, content in issues:
                    print(f"   L.{line_num}: {msg}")
    
    if files_with_issues > 0:
        print(f"\n{RED}⛔ FALHA CRÍTICA: Segredos encontrados.{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}✅ Projeto limpo.{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()