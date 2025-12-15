import os
import re
import sys
import subprocess
import shutil
import datetime

# --- CONFIGURAÇÃO DE LOGS ---
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"scan_{TIMESTAMP}.txt")

# Cores ANSI para o terminal
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def strip_ansi(text):
    """Remove códigos de cor para salvar no arquivo de log limpo."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class Logger:
    def __init__(self, filepath):
        self.filepath = filepath
        # Cria o arquivo e escreve o cabeçalho
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write("=== RELATÓRIO DE SEGURANÇA VCPS ===\n")
            f.write(f"Data: {datetime.datetime.now()}\n")
            f.write("===================================\n\n")

    def log(self, message, color=None):
        """Imprime colorido no terminal e limpo no arquivo."""
        # Terminal
        if color:
            print(f"{color}{message}{RESET}")
        else:
            print(message)
        
        # Arquivo
        clean_msg = strip_ansi(message)
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(clean_msg + "\n")

# Instancia o logger global
logger = Logger(LOG_FILE)

IGNORED_DIRS = {
    '.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules', 
    '.idea', '.vscode', 'build', 'dist', 'target', '.github', '.ruff_cache', 'logs'
}
IGNORED_FILES = "scan_project.py,install_hooks.py,setup_vibe_kit.py"

FORBIDDEN_PATTERNS = [
    (r"(?i)(api_key|apikey|access_token)\s*=['\"]", "Possível Chave de API (Variação de nome)"),
    (r"(?i)(password|passwd|pwd)\s*=['\"]", "Senha explícita"),
    (r"(?i)(secret|client_secret)\s*=['\"]", "Segredo explícito"),
    (r"sk-[a-zA-Z0-9]{20,}", "Chave OpenAI"),
    (r"ghp_[a-zA-Z0-9]{20,}", "Token GitHub"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"Bearer [a-zA-Z0-9_\-\.]{20,}", "Token de Autenticação Bearer"),
    (r"-----BEGIN [A-Z]+ PRIVATE KEY-----", "Chave Privada SSH/RSA"),
]

def is_git_ignored(filepath):
    """Verifica se o arquivo está no .gitignore usando o próprio git."""
    try:
        # Retorna 0 (True) se o arquivo for ignorado pelo git
        subprocess.check_call(["git", "check-ignore", "-q", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def ensure_package_installed(package):
    if shutil.which(package) is None:
        logger.log(f"⚠️  {package} não encontrado. Instalando...", YELLOW)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)
            logger.log(f"✅ {package} instalado.", GREEN)
        except Exception:
            logger.log(f"❌ Erro ao instalar {package}.", RED)
            return False
    return True

def run_ruff_linter():
    logger.log(f"\n{BOLD}🧹 Executando Linter (Ruff - Qualidade de Código)...{RESET}")
    if not ensure_package_installed("ruff"):
        return False
    
    try:
        # Captura output para salvar no log
        result = subprocess.run(["ruff", "check", "."], text=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        if result.returncode != 0:
            logger.log("\n⛔ O RUFF ENCONTROU PROBLEMAS DE QUALIDADE!", RED)
            logger.log(result.stdout) # Salva o erro detalhado no log
            logger.log("☝️  Corrija os erros acima.", RED)
            return False
            
        logger.log("✅ Código limpo e organizado.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Ruff: {e}", RED)
        return False

def run_pip_audit():
    logger.log(f"\n{BOLD}📦 Executando Auditoria de Dependências (SCA)...{RESET}")
    
    target_file = ""
    if os.path.exists("requirements.txt"):
        target_file = "-r requirements.txt"
    elif os.path.exists("pyproject.toml"):
        target_file = "." # pip-audit detecta pyproject.toml automaticamente no diretório
    else:
        logger.log("ℹ️  Nenhum arquivo de dependências (requirements.txt/pyproject.toml) encontrado. Pulando.", YELLOW)
        return True
        
    if not ensure_package_installed("pip-audit"):
        return False

    try:
        cmd = ["pip-audit"] + target_file.split()
        result = subprocess.run(cmd, text=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            logger.log("\n⛔ VULNERABILIDADE EM BIBLIOTECA ENCONTRADA!", RED)
            logger.log(result.stdout)
            return False
        logger.log("✅ Dependências seguras.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar pip-audit: {e}", RED)
        return False

def run_bandit():
    logger.log(f"\n{BOLD}🔫 Executando Análise Lógica (Bandit)...{RESET}")
    if not ensure_package_installed("bandit"):
        return False
    try:
        exclusions = f"venv,.venv,.git,tests,.\\tests,./tests,{IGNORED_FILES}"
        cmd = ["bandit", "-r", ".", "-x", exclusions, "-f", "txt"] # Formato texto para log
        
        result = subprocess.run(cmd, text=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        if result.returncode != 0:
            logger.log("\n⛔ O BANDIT ENCONTROU VULNERABILIDADES!", RED)
            logger.log(result.stdout)
            return False
        logger.log("✅ Lógica segura.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Bandit: {e}", RED)
        return False

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if len(line) > 500:
                    continue
                if "# nosec" in line: # Permite ignorar linhas específicas
                    continue
                for pattern, msg in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        issues.append((i, msg, line.strip()))
    except Exception:
        pass
    return issues

def main():
    logger.log(f"{BOLD}🔍 Vibe Security Scan (Secrets + Logic + Deps + Quality){RESET}")
    logger.log(f"📄 Log salvo em: {LOG_FILE}\n")
    
    # 1. Regex
    root_dir = os.getcwd()
    files_with_issues = 0
    
    check_gitignore = True
    if "--all" in sys.argv:
        check_gitignore = False
        logger.log("⚠️  Modo --all ativado: Verificando arquivos ignorados pelo Git.", YELLOW)

    logger.log("1️⃣  Buscando chaves (Regex)...")
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        if check_gitignore:
            # Otimização: Ignora pastas que o git também ignora
            dirs[:] = [d for d in dirs if not is_git_ignored(os.path.join(root, d))]

        for file in files:
            if file in IGNORED_FILES.split(","):
                continue
            filepath = os.path.join(root, file)
            
            if check_gitignore and is_git_ignored(filepath):
                continue

            issues = scan_file(filepath)
            if issues:
                files_with_issues += 1
                rel_path = os.path.relpath(filepath, root_dir)
                logger.log(f"❌ [SEGREDO] {rel_path}", RED)
                for line_num, msg, content in issues:
                    logger.log(f"   L.{line_num}: {msg}")

    secrets_ok = (files_with_issues == 0)
    if secrets_ok:
        logger.log("✅ Nenhuma chave encontrada.", GREEN)
    
    # 2. Bandit
    bandit_ok = run_bandit()
    
    # 3. Pip Audit
    audit_ok = run_pip_audit()

    # 4. Ruff
    ruff_ok = run_ruff_linter()

    if not secrets_ok or not bandit_ok or not audit_ok or not ruff_ok:
        logger.log("\n⛔ FALHA NA AUDITORIA. VERIFIQUE OS ERROS ACIMA.", RED)
        sys.exit(1)
    
    logger.log("\n🎉 SUCESSO! Código aprovado em todas as etapas.", GREEN)
    sys.exit(0)

if __name__ == "__main__":
    main()