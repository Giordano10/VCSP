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
    '.idea', '.vscode', 'build', 'dist', 'target', '.github', '.ruff_cache'
}

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

def ensure_package_installed(package):
    if shutil.which(package) is None:
        print(f"{YELLOW}⚠️  {package} não encontrado. Instalando...{RESET}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)
            print(f"{GREEN}✅ {package} instalado.{RESET}")
        except:
            print(f"{RED}❌ Erro ao instalar {package}.{RESET}")
            return False
    return True

def run_ruff_linter():
    print(f"\n{BOLD}🧹 Executando Linter (Ruff - Qualidade de Código)...{RESET}")
    if not ensure_package_installed("ruff"): return False
    
    try:
        # Roda o ruff no diretório atual
        result = subprocess.run(["ruff", "check", "."], text=True)
        
        if result.returncode != 0:
            print(f"\n{RED}⛔ O RUFF ENCONTROU PROBLEMAS DE QUALIDADE!{RESET}")
            print("☝️  Corrija os erros acima (variáveis não usadas, imports inúteis, sintaxe).")
            return False
            
        print(f"{GREEN}✅ Código limpo e organizado.{RESET}")
        return True
    except Exception as e:
        print(f"{RED}❌ Erro ao rodar Ruff: {e}{RESET}")
        return False

def run_pip_audit():
    print(f"\n{BOLD}📦 Executando Auditoria de Dependências (SCA)...{RESET}")
    if not os.path.exists("requirements.txt"):
        print(f"{YELLOW}ℹ️  requirements.txt não encontrado. Pulando.{RESET}")
        return True
    if not ensure_package_installed("pip-audit"): return False

    try:
        result = subprocess.run(["pip-audit", "-r", "requirements.txt"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"\n{RED}⛔ VULNERABILIDADE EM BIBLIOTECA ENCONTRADA!{RESET}")
            print(result.stdout)
            return False
        print(f"{GREEN}✅ Dependências seguras.{RESET}")
        return True
    except Exception as e:
        print(f"{RED}❌ Erro ao rodar pip-audit: {e}{RESET}")
        return False

def run_bandit():
    print(f"\n{BOLD}🔫 Executando Análise Lógica (Bandit)...{RESET}")
    if not ensure_package_installed("bandit"): return False
    try:
        exclusions = f"venv,.venv,.git,{IGNORED_FILES}"
        cmd = ["bandit", "-r", ".", "-x", exclusions, "-f", "screen"]
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            print(f"\n{RED}⛔ O BANDIT ENCONTROU VULNERABILIDADES!{RESET}")
            return False
        print(f"{GREEN}✅ Lógica segura.{RESET}")
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
    print(f"{BOLD}🔍 Vibe Security Scan (Secrets + Logic + Deps + Quality){RESET}")
    
    # 1. Regex (Segredos)
    root_dir = os.getcwd()
    files_with_issues = 0
    print(f"1️⃣  Buscando chaves (Regex)...")
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
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
    
    # 2. Bandit (Lógica)
    bandit_ok = run_bandit()
    
    # 3. Pip Audit (Dependências)
    audit_ok = run_pip_audit()

    # 4. Ruff (Qualidade)
    ruff_ok = run_ruff_linter()

    if not secrets_ok or not bandit_ok or not audit_ok or not ruff_ok:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()