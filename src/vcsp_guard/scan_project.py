import os
import re
import sys
import subprocess
import shutil
import datetime
import ast

# --- DETECÇÃO DE RAIZ DO PROJETO ---
def get_project_root():
    # 1. Busca a partir do diretório atual (CWD) - Prioridade para quem roda o comando
    current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")) or \
           os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Chegou na raiz do sistema
            break
        current = parent

    # 2. Fallback: Busca a partir do local do script (__file__)
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current, ".git")) or \
           os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return os.getcwd()

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
    '.idea', '.vscode', 'build', 'dist', 'target', '.github', 
    '.ruff_cache', 'logs_scan_vcsp'
}
IGNORED_FILES = "scan_project.py,install_hooks.py,setup_vibe_kit.py"

FORBIDDEN_PATTERNS = [
    (r"(?i)(api_key|apikey|access_token)\s*=['\"]", "Possível Chave de API"),
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
        # noqa: S603, S607
        subprocess.check_call(
            ["git", "check-ignore", "-q", rel_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False

def ensure_package_installed(package):
    if shutil.which(package) is None:
        logger.log(f"⚠️  {package} não encontrado. Instalando...", YELLOW)
        try:
            # noqa: S603
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
            )
            logger.log(f"✅ {package} instalado.", GREEN)
        except Exception:
            logger.log(f"❌ Erro ao instalar {package}.", RED)
            return False
    return True

def find_dependency_file(start_dir):
    """Encontra requirements.txt ou pyproject.toml na raiz ou subpastas."""
    # 1. Prioridade: Raiz
    req_path = os.path.join(start_dir, "requirements.txt")
    if os.path.exists(req_path):
        return req_path
    
    toml_path = os.path.join(start_dir, "pyproject.toml")
    if os.path.exists(toml_path):
        return toml_path
        
    # 2. Busca Recursiva
    SEARCH_IGNORE = {
        '.git', 'venv', 'env', '.venv', '__pycache__', 'node_modules', 
        'site-packages', '.idea', '.vscode', 'dist', 'build'
    }
    
    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d not in SEARCH_IGNORE]
        if "requirements.txt" in files:
            return os.path.join(root, "requirements.txt")
        if "pyproject.toml" in files:
            return os.path.join(root, "pyproject.toml")
    return None

def run_ruff_linter():
    logger.log(f"\n{BOLD}🧹 Executando Linter (Ruff - Qualidade de Código)...{RESET}")
    if not ensure_package_installed("ruff"):
        return False

    try:
        # Captura output para salvar no log
        # Ignora S (Security) aqui pois já foi verificado no passo de segurança lógica
        cmd = ["ruff", "check", ".", "--ignore", "S"]
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )  # noqa: S603

        if result.returncode != 0:
            logger.log("\n⛔ O RUFF ENCONTROU PROBLEMAS DE QUALIDADE!", RED)
            logger.log(result.stdout)  # Salva o erro detalhado no log
            logger.log("☝️  Corrija os erros acima.", RED)
            return False

        logger.log("✅ Código limpo e organizado.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Ruff: {e}", RED)
        return False

def run_pip_audit():
    logger.log(f"\n{BOLD}📦 Executando Auditoria de Dependências (SCA)...{RESET}")
    
    dep_file = find_dependency_file(PROJECT_ROOT)
    
    if not dep_file:
        logger.log("ℹ️  Nenhum arquivo de dependências encontrado. Pulando.", YELLOW)
        return True
        
    logger.log(f"   📄 Arquivo de dependências detectado: {dep_file}", YELLOW)
    if not ensure_package_installed("pip-audit"):
        return False

    try:
        if dep_file.endswith("requirements.txt"):
            cmd = ["pip-audit", "-r", dep_file]
        else:
            cmd = ["pip-audit", os.path.dirname(dep_file)]
        
        # noqa: S603
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            # Tratamento de erro específico para falha de instalação
            # (comum em CI/CD Linux vs Windows)
            err = result.stdout
            if "No matching distribution found" in err or "internal pip failure" in err:
                logger.log("\n⚠️  ERRO DE AMBIENTE NO PIP-AUDIT", YELLOW)
                logger.log("   O pip-audit falhou ao instalar as dependências.", YELLOW)
                logger.log(
                    "   Isso ocorre com libs exclusivas de Windows no Linux.", YELLOW
                )
                logger.log(
                    "   📝 SOLUÇÃO: Adicione '; sys_platform == \"win32\"'",
                    YELLOW,
                )
                logger.log("   no requirements.txt para essas libs.", YELLOW)
                logger.log(result.stdout)
                return False

            if "ModuleNotFoundError" in result.stdout or "Traceback" in result.stdout:
                logger.log("\n⚠️  ERRO DE EXECUÇÃO (DEPENDÊNCIA FALTANDO)", YELLOW)  # noqa: E501
                logger.log(
                    "   O pip-audit não conseguiu rodar pois faltam bibliotecas.",
                    YELLOW,
                )
                logger.log(
                    "   💡 Tente: pip install -r requirements.txt --force",
                    YELLOW,
                )
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

def run_security_logic():
    logger.log(f"\n{BOLD}🔫 Executando Análise Lógica (Ruff Security)...{RESET}")
    if not ensure_package_installed("ruff"):
        return False
    try:
        # Usa regras 'S' (flake8-bandit) do Ruff
        cmd = ["ruff", "check", ".", "--select", "S", "--extend-exclude", IGNORED_FILES]
        
        # noqa: S603
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        
        if result.returncode != 0:
            logger.log("\n⛔ O RUFF (SECURITY) ENCONTROU VULNERABILIDADES!", RED)
            logger.log(result.stdout)
            return False
        logger.log("✅ Lógica segura.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Ruff Security: {e}", RED)
        return False

def run_iac_scan():
    logger.log(f"\n{BOLD}🏗️  Executando Análise de Infraestrutura (Semgrep)...{RESET}")
    
    # Verifica se existem arquivos de infraestrutura para evitar
    # instalação pesada desnecessária
    IAC_IGNORE = {
        ".git",
        "venv",
        "env",
        ".venv",
        "__pycache__",
        "node_modules",
        ".idea",
        ".vscode",
        ".ruff_cache",
        "logs_scan_vcsp",
    }
    
    iac_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Modifica dirs in-place para pular pastas ignoradas (Otimização)
        dirs[:] = [d for d in dirs if d not in IAC_IGNORE]
        
        for file in files:
            exts = (".dockerfile", ".tf", ".yaml", ".yml")
            if "Dockerfile" in file or file.endswith(exts):
                # Verifica se é docker-compose ou k8s no caso de yaml
                if file.endswith(".yaml") or file.endswith(".yml"):
                    if "docker-compose" not in file and "k8s" not in file:
                        continue
                path = os.path.join(root, file)
                iac_files.append(path)
                logger.log(f"   📄 Arquivo de infraestrutura detectado: {path}", YELLOW)
            
    if not iac_files:
        logger.log("ℹ️  Nenhum arquivo de infraestrutura encontrado. Pulando.", YELLOW)
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
            logger.log("   Semgrep no Windows requer Docker Desktop.", YELLOW)
            logger.log("   Instale: https://www.docker.com/products/docker-desktop/", YELLOW) # noqa: E501
            logger.log("   (Pulando verificação de IaC por enquanto...)", YELLOW)
            return True
        
        logger.log("🐳 Windows detectado: Rodando Semgrep via Docker...", YELLOW)
        # Converte caminhos absolutos para relativos
        # (para funcionar dentro do container montado em /src)
        # E força barras normais (/) pois o container é Linux
        rel_files = [
            os.path.relpath(f, PROJECT_ROOT).replace("\\", "/") for f in iac_files
        ]
        
        base_cmd = [
            "docker", "run", "--rm", "-v", f"{PROJECT_ROOT}:/src",
            "semgrep/semgrep", "semgrep", "scan"
        ]
        flags = ["--error", "--metrics=off", "--quiet", "--no-git-ignore"]
        cmd = base_cmd + flags + configs + rel_files
    else:
        if not ensure_package_installed("semgrep"):
            return False
        logger.log("⏳ Rodando Semgrep (Nativo)...", YELLOW)
        flags = ["--error", "--metrics=off", "--quiet", "--no-git-ignore"]
        cmd = ["semgrep", "scan"] + flags + configs + iac_files

    try:
        # noqa: S603
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        
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

def get_project_imports(root_dir):
    """Varre arquivos .py e retorna um conjunto de nomes de módulos importados."""
    imports = set()
    for dirpath, _, filenames in os.walk(root_dir):
        # Ignora pastas virtuais e de cache
        ignored = [
            "venv", ".git", "__pycache__", "site-packages",
            "node_modules", ".venv", "env"
        ]
        if any(x in dirpath for x in ignored):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
                except Exception:
                    continue
    return imports

def run_unused_libs_check():
    logger.log(f"\n{BOLD}🗑️  Verificando Dependências Não Utilizadas...{RESET}")
    
    dep_file = find_dependency_file(PROJECT_ROOT)
    
    if not dep_file or not dep_file.endswith("requirements.txt"):
        if dep_file:
             logger.log(f"ℹ️  Arquivo: {dep_file}. Check limita-se a requirements.txt.", YELLOW) # noqa: E501
        else:
             logger.log("ℹ️  requirements.txt não encontrado. Pulando.", YELLOW)
        return True
    
    requirements_path = dep_file

    try:
        if sys.version_info < (3, 10):
            from importlib_metadata import packages_distributions
            from importlib_metadata import distribution
        else:
            from importlib.metadata import packages_distributions
            from importlib.metadata import distribution
    except ImportError:
        logger.log("⚠️  'importlib-metadata' não encontrado (Python < 3.10).", YELLOW)
        return True

    try:
        dist_map = packages_distributions()
        pkg_to_imports = {}
        for import_name, dists in dist_map.items():
            for dist in dists:
                pkg_to_imports.setdefault(dist.lower(), []).append(import_name)

        declared_pkgs = set()
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('-'):
                    continue
                pkg_name = re.split(r'[=<>~!;]', line)[0].strip()
                if pkg_name:
                    declared_pkgs.add(pkg_name.lower())

        # --- LÓGICA ESTILO PIPDEPTREE (FILTRO DE SUB-DEPENDÊNCIAS) ---
        # Identifica quais pacotes são apenas dependências de outros pacotes listados
        # para evitar cobrar importação explícita deles (ex: rich, que vem com bandit).
        transitive_deps = set()
        for pkg in declared_pkgs:
            try:
                # Obtém os metadados do pacote instalado
                dist = distribution(pkg)
                if dist.requires:
                    for req in dist.requires:
                        # O formato vem como 'requests (>=2.0)' ou
                        # 'requests; extra == "dev"'
                        # Pegamos apenas o nome base
                        req_name = re.split(r'[ ;<=>!]', req)[0].strip().lower()
                        if req_name:
                            transitive_deps.add(req_name)
            except Exception:
                # Se o pacote não estiver instalado no ambiente, ignoramos
                continue

        used_imports = get_project_imports(PROJECT_ROOT)
        
        # Lista de ferramentas e libs de sistema que não são importadas diretamente
        ignored_pkgs = {
            'pip', 'setuptools', 'wheel', 'gunicorn', 'uvicorn', 
            'bandit', 'pip-audit', 'ruff', 'semgrep', 'pytest', 
            'black', 'flake8', 'coverage', 'pylint', 'mypy', 'tox',
            'pipdeptree', 'pip-tools'
        }

        unused_pkgs = []
        for pkg in declared_pkgs:
            if pkg in ignored_pkgs:
                continue
            
            # Se o pacote é sub-dependência de outro listado, ele é "usado"
            if pkg in transitive_deps:
                continue
            
            # Verifica se algum módulo provido pelo pacote está sendo importado
            possible_imports = pkg_to_imports.get(pkg, []) or [pkg]
            if not any(mod in used_imports for mod in possible_imports):
                unused_pkgs.append(pkg)

        if unused_pkgs:
            logger.log("⚠️  ATENÇÃO: Bibliotecas listadas mas NÃO importadas:", YELLOW)
            for p in unused_pkgs:
                logger.log(f"   ❌ {p}")
            logger.log(f"💡 Para limpar: pip uninstall {' '.join(unused_pkgs)}")
        else:
            logger.log(
                f"✅ Todas as dependências ({len(declared_pkgs)}) em uso.",
                GREEN,
            )
    except Exception as e:
        logger.log(f"❌ Erro ao verificar libs: {e}", RED)
    return True

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
        logger.log("⚠️  Modo --all: Verificando arquivos ignorados pelo Git.", YELLOW)

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
                for line_num, msg, _ in issues:
                    logger.log(f"   L.{line_num}: {msg}")

    secrets_ok = (files_with_issues == 0)
    if secrets_ok:
        logger.log("✅ Nenhuma chave encontrada.", GREEN)
    
    # 2. Security Logic (Ruff)
    security_ok = run_security_logic()
    
    # 3. Checkov (Infraestrutura)
    iac_ok = run_iac_scan()
    
    # 4. Pip Audit
    audit_ok = run_pip_audit()

    # 5. Ruff
    ruff_ok = run_ruff_linter()

    # 6. Unused Libs (Apenas informativo, não falha o build)
    run_unused_libs_check()

    if not secrets_ok or not security_ok or not iac_ok or not audit_ok or not ruff_ok:
        logger.log("\n⛔ FALHA NA AUDITORIA. VERIFIQUE OS ERROS ACIMA.", RED)
        sys.exit(1)
    
    logger.log("\n🎉 SUCESSO! Código aprovado em todas as etapas.", GREEN)
    sys.exit(0)

if __name__ == "__main__":
    main()

# Compatibility shims: export expected entrypoints without overwriting existing
# implementations
if "run_ruff" not in globals():
    def run_ruff(*args, **kwargs):
        """
        Compat shim for run_ruff. Delegates to any available implementation found
        in the module.
        """
        candidates = (
            "run_ruff_impl",
            "run_security_scan",
            "run_lint",
            "run_scan",
            "run_bandit",
        )
        for candidate in candidates:
            fn = globals().get(candidate)
            if callable(fn):
                return fn(*args, **kwargs)
        raise NotImplementedError(
            "run_ruff not implemented: provide run_ruff_impl or equivalent"
        )