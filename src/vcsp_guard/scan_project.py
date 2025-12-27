import os
import re
import sys
import subprocess
import shutil
import datetime

# --- DETECÇÃO DE RAIZ DO PROJETO ---
def get_project_root():
    # Começa a busca a partir do diretório onde este script está localizado
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current, ".git")) or os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current: # Chegou na raiz do sistema
            return os.getcwd()
        current = parent

PROJECT_ROOT = get_project_root()
if os.getcwd() != PROJECT_ROOT:
    print(f"🔄 Mudando diretório de trabalho para a raiz do projeto: {PROJECT_ROOT}")
    os.chdir(PROJECT_ROOT)
else:
    print(f"📂 Diretório de trabalho (Raiz): {PROJECT_ROOT}")

# --- CONFIGURAÇÃO DE LOGS ---
LOG_DIR = "logs_scan_vcsp"
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
    '.idea', '.vscode', 'build', 'dist', 'target', '.github', '.ruff_cache', 'logs_scan_vcsp'
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
        # Usa caminho relativo para evitar erros de path no Windows/Git
        rel_path = os.path.relpath(filepath, os.getcwd())
        # Retorna 0 (True) se o arquivo for ignorado pelo git
        subprocess.check_call(["git", "check-ignore", "-q", rel_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # nosec
        return True
    except Exception:
        return False

def ensure_package_installed(package):
    if shutil.which(package) is None:
        logger.log(f"⚠️  {package} não encontrado. Instalando...", YELLOW)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL) # nosec
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
        result = subprocess.run(["ruff", "check", "."], text=True, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # nosec
        
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
    # Suporte para execução em subpastas (ex: src/ ou src/vcsp_guard/)
    elif os.path.exists("../requirements.txt"):
        target_file = "-r ../requirements.txt"
    elif os.path.exists("../pyproject.toml"):
        target_file = "../"
    elif os.path.exists("../../pyproject.toml"):
        target_file = "../../"
    else:
        logger.log("ℹ️  Nenhum arquivo de dependências (requirements.txt/pyproject.toml) encontrado. Pulando.", YELLOW)
        return True
        
    if not ensure_package_installed("pip-audit"):
        return False

    try:
        cmd = ["pip-audit"] + target_file.split()
        result = subprocess.run(cmd, text=True, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # nosec
        if result.returncode != 0:
            # Tratamento de erro específico para falha de instalação (comum em CI/CD Linux vs Windows)
            if "No matching distribution found" in result.stdout or "internal pip failure" in result.stdout:
                logger.log("\n⚠️  ERRO DE AMBIENTE NO PIP-AUDIT", YELLOW)
                logger.log("   O pip-audit falhou ao instalar as dependências. Isso geralmente ocorre", YELLOW)
                logger.log("   quando há bibliotecas exclusivas de Windows (ex: pywin32) rodando no Linux.", YELLOW)
                logger.log("   📝 SOLUÇÃO: Adicione '; sys_platform == \"win32\"' no requirements.txt para essas libs.", YELLOW)
                logger.log(result.stdout)
                return False

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
        
        result = subprocess.run(cmd, text=True, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # nosec
        
        if result.returncode != 0:
            logger.log("\n⛔ O BANDIT ENCONTROU VULNERABILIDADES!", RED)
            logger.log(result.stdout)
            return False
        logger.log("✅ Lógica segura.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Bandit: {e}", RED)
        return False

def run_iac_scan():
    logger.log(f"\n{BOLD}🏗️  Executando Análise de Infraestrutura (Semgrep)...{RESET}")
    
    # Verifica se existem arquivos de infraestrutura para evitar instalação pesada desnecessária
    # Pastas de sistema/libs que devem ser ignoradas (mas permitimos build/dist/etc para IaC)
    IAC_IGNORE = {'.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules', '.idea', '.vscode', '.ruff_cache', 'logs_scan_vcsp'}
    
    iac_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Modifica dirs in-place para pular pastas ignoradas (Otimização)
        dirs[:] = [d for d in dirs if d not in IAC_IGNORE]
        
        for file in files:
            if "Dockerfile" in file or file.endswith(".dockerfile") or file.endswith(".tf") or file.endswith(".yaml") or file.endswith(".yml"):
                # Verifica se é docker-compose ou k8s no caso de yaml
                if file.endswith(".yaml") or file.endswith(".yml"):
                    if "docker-compose" not in file and "k8s" not in file:
                        continue
                path = os.path.join(root, file)
                iac_files.append(path)
                logger.log(f"   📄 Arquivo de infraestrutura detectado: {path}", YELLOW)
            
    if not iac_files:
        logger.log("ℹ️  Nenhum arquivo de infraestrutura (Docker/Terraform) encontrado. Pulando.", YELLOW)
        return True

    # Configs do Semgrep
    configs = []
    if any("Dockerfile" in f or f.endswith(".dockerfile") for f in iac_files):
        configs.extend(["--config", "p/dockerfile"])
    if any(f.endswith(".tf") for f in iac_files):
        configs.extend(["--config", "p/terraform"])
    if any(f.endswith(".yaml") or f.endswith(".yml") for f in iac_files):
        configs.extend(["--config", "p/kubernetes"])
    
    if not configs:
        configs.extend(["--config", "p/security-audit"])

    cmd = []
    
    if sys.platform == "win32":
        if shutil.which("docker") is None:
            logger.log("\n⚠️  DOCKER NÃO ENCONTRADO!", YELLOW)
            logger.log("   Para escanear arquivos de infraestrutura no Windows, o Semgrep requer o Docker Desktop.", YELLOW)
            logger.log("   Instale em: https://www.docker.com/products/docker-desktop/", YELLOW)
            logger.log("   (Pulando verificação de IaC por enquanto...)", YELLOW)
            return True
        
        logger.log("🐳 Windows detectado: Rodando Semgrep via Docker...", YELLOW)
        # Converte caminhos absolutos para relativos (para funcionar dentro do container montado em /src)
        # E força barras normais (/) pois o container é Linux
        rel_files = [os.path.relpath(f, PROJECT_ROOT).replace("\\", "/") for f in iac_files]
        
        cmd = ["docker", "run", "--rm", "-v", f"{PROJECT_ROOT}:/src", "semgrep/semgrep", "semgrep", "scan", "--error", "--metrics=off", "--quiet", "--no-git-ignore"] + configs + rel_files
    else:
        if not ensure_package_installed("semgrep"):
            return False
        logger.log("⏳ Rodando Semgrep (Nativo)...", YELLOW)
        cmd = ["semgrep", "scan", "--error", "--metrics=off", "--quiet", "--no-git-ignore"] + configs + iac_files

    try:
        result = subprocess.run(cmd, text=True, encoding='utf-8', errors='ignore', stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # nosec
        
        if result.returncode != 0:
            logger.log("\n⛔ O SEMGREP ENCONTROU PROBLEMAS DE INFRAESTRUTURA!", RED)
            # Limita o output para não poluir demais se for gigante
            output_lines = result.stdout.splitlines()
            logger.log(f"Found {len(output_lines)} infrastructure issues.")
            if len(output_lines) > 50:
                logger.log("\n".join(output_lines[:50]))
                logger.log(f"... e mais {len(output_lines)-50} linhas.", YELLOW)
            else:
                logger.log(result.stdout)
            return False
        
        logger.log("✅ Infraestrutura segura.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Semgrep: {e}", RED)
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
    
    # 3. Checkov (Infraestrutura)
    iac_ok = run_iac_scan()
    
    # 4. Pip Audit
    audit_ok = run_pip_audit()

    # 5. Ruff
    ruff_ok = run_ruff_linter()

    if not secrets_ok or not bandit_ok or not iac_ok or not audit_ok or not ruff_ok:
        logger.log("\n⛔ FALHA NA AUDITORIA. VERIFIQUE OS ERROS ACIMA.", RED)
        sys.exit(1)
    
    logger.log("\n🎉 SUCESSO! Código aprovado em todas as etapas.", GREEN)
    sys.exit(0)

if __name__ == "__main__":
    main()