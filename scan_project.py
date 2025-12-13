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

# Ignorar APENAS ambientes virtuais e git. 
IGNORED_DIRS = {
    '.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules', 
    '.idea', '.vscode', 'build', 'dist', 'target', '.github'
}

# Arquivos que o Bandit deve ignorar para não dar falso positivo neles mesmos
IGNORED_FILES = "scan_project.py,install_hooks.py,setup_vibe_kit.py"

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

def ensure_bandit_installed():
    if shutil.which("bandit") is None:
        print(f"{YELLOW}⚠️  Bandit não encontrado. Instalando automaticamente...{RESET}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "bandit"])
            print(f"{GREEN}✅ Bandit instalado!{RESET}\n")
        except:
            print(f"{RED}❌ Erro ao instalar Bandit. Rode 'pip install bandit' manualmente.{RESET}")
            return False
    return True

def run_bandit():
    print(f"\n{BOLD}🔫 Executando Análise Lógica (Bandit - Modo Paranoico)...{RESET}")
    
    if not ensure_bandit_installed():
        return False
    
    try:
        # Exclui também os scripts do kit da análise do Bandit
        exclusions = f"venv,.venv,.git,{IGNORED_FILES}"
        
        # -r . : Recursivo
        # -x ... : Exclusões
        # -f screen : Formato de saída
        cmd = ["bandit", "-r", ".", "-x", exclusions, "-f", "screen"]
        
        result = subprocess.run(cmd, text=True)
        
        if result.returncode != 0:
            print(f"\n{RED}⛔ O BANDIT ENCONTROU VULNERABILIDADES!{RESET}")
            print("☝️  Veja o relatório acima e corrija o código.")
            return False
        
        print(f"{GREEN}✅ Código limpo. Nenhuma falha lógica encontrada.{RESET}")
        return True
        
    except Exception as e:
        print(f"{RED}❌ Erro ao rodar Bandit: {e}{RESET}")
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
    print(f"{BOLD}🔍 Vibe Security Scan{RESET}")
    
    # 1. Busca por Segredos (Regex)
    root_dir = os.getcwd()
    files_with_issues = 0
    print(f"1️⃣  Buscando chaves (Regex)...")

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            # Ignora os scripts na busca regex também para evitar duplicidade
            if file in IGNORED_FILES.split(","): continue
            
            filepath = os.path.join(root, file)
            issues = scan_file(filepath)
            if issues:
                files_with_issues += 1
                rel_path = os.path.relpath(filepath, root_dir)
                print(f"{RED}❌ [SEGREDO] {rel_path}{RESET}")
                for line_num, msg, content in issues:
                    print(f"   L.{line_num}: {msg}")

    secrets_ok = (files_with_issues == 0)
    if secrets_ok: print(f"{GREEN}✅ Nenhuma chave encontrada.{RESET}")
    
    # 2. Busca por Vulnerabilidades de Lógica (Bandit)
    bandit_ok = run_bandit()

    if not secrets_ok or not bandit_ok:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()