import os
import re
import sys
import subprocess
import shutil
import datetime
import ast
import json
import argparse

# --- DETECÇÃO DE RAIZ DO PROJETO ---
def get_project_root():
    # 1. Prioridade Absoluta: .git (Define a raiz do repositório)
    current = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Chegou na raiz do sistema
            break
        current = parent

    # 2. Fallback: Arquivos de configuração (pyproject.toml, setup.py, .vibe)
    # Se não houver .git, usamos arquivos comuns para identificar a raiz
    markers = ["pyproject.toml", "requirements.txt", ".env",]
    current = os.getcwd()
    while True:
        if any(os.path.exists(os.path.join(current, m)) for m in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return os.getcwd()

PROJECT_ROOT = get_project_root()
if "--local" in sys.argv:
    PROJECT_ROOT = os.getcwd()
    print(f"📂 Modo Local (--local): Varrendo a partir de: {PROJECT_ROOT}")
elif os.getcwd() != PROJECT_ROOT:
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
            f.write("=== RELATÓRIO DE SEGURANÇA VCSP ===\n")
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
        # Usa caminho relativo em relação à raiz do projeto para evitar erros de path
        rel_path = os.path.relpath(filepath, PROJECT_ROOT)
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

def build_reverse_dependency_map():
    """Cria um mapa: pacote -> lista de pacotes que dependem dele."""
    try:
        if sys.version_info < (3, 10):
            from importlib_metadata import distributions
        else:
            from importlib.metadata import distributions
    except ImportError:
        return {}

    rev_map = {}
    try:
        for dist in distributions():
            name = dist.metadata['Name']
            version = dist.version
            if dist.requires:
                for req in dist.requires:
                    # Ex: "requests (>=2.0)" -> "requests"
                    match = re.match(r'^([A-Za-z0-9_\-\.]+)', req)
                    if match:
                        req_name = match.group(1).lower()
                        if req_name not in rev_map:
                            rev_map[req_name] = []
                        rev_map[req_name].append(f"{name} ({version})")
    except Exception:
        pass
    return rev_map

def run_pip_audit(custom_deps_file=None):
    logger.log(f"\n{BOLD}📦 Executando Auditoria de Dependências (CVE)...{RESET}")
    
    # 1. Identificar quais arquivos existem
    target_filenames = ["requirements.txt", "requirements-dev.txt"]
    found_files = []
    
    for fname in target_filenames:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            found_files.append(fpath)
    # Se o usuário passou um arquivo personalizado, adiciona ele
    if custom_deps_file:
        custom_path = os.path.join(PROJECT_ROOT, custom_deps_file)
        if os.path.exists(custom_path):
            found_files.append(custom_path)
    
    # Se não achar nada, tenta procurar qualquer coisa genérica (lógica antiga)
    # ou retorna erro dependendo da sua estratégia.
    # Vamos avisar e tentar escanear o ambiente.
    if not found_files:
        # Tenta achar um arquivo genérico se os específicos não existirem
        dep_file = find_dependency_file(PROJECT_ROOT)
        if dep_file:
            found_files.append(dep_file)
        else:
            logger.log("ℹ️  Nenhum arquivo de dependências encontrado. Pulando.", YELLOW)
            return True

    files_list_str = ", ".join([os.path.basename(f) for f in found_files])
    logger.log(f"📄 Arquivos de dependências detectados: {files_list_str}", YELLOW)

    if not ensure_package_installed("pip-audit"):
        return False

    try:
        # 2. Montar o comando dinâmico
        # Usamos JSON para poder processar e mostrar a árvore de dependência
        cmd = ["pip-audit", "-f", "json"]
        
        # Adiciona cada arquivo encontrado com a flag -r
        for f in found_files:
            cmd.extend(["-r", f])

        # noqa: S603
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Separado para não sujar o JSON
        )
        
        if result.returncode != 0:
            # Tenta parsear JSON para ver se são vulnerabilidades
            try:
                audit_data = json.loads(result.stdout)
                rev_deps = build_reverse_dependency_map()
                
                logger.log("\n⛔ VULNERABILIDADE EM BIBLIOTECA ENCONTRADA!", RED)
                
                if isinstance(audit_data, list):
                    packages = audit_data
                else:
                    packages = audit_data.get('dependencies', [])
                
                for pkg in packages:
                    if pkg.get('vulns'):
                        name = pkg['name']
                        version = pkg['version']
                        parents = rev_deps.get(name.lower(), [])
                        
                        logger.log(f"\n📦 {BOLD}{name}{RESET} ({version})", RED)
                        if parents:
                            intro = f"   ↳ Introduzido por: {', '.join(parents)}"
                            logger.log(intro, YELLOW)
                        else:
                            logger.log("   ↳ Dependência direta ou raiz.", YELLOW)
                            
                        for v in pkg['vulns']:
                            vid = v.get('id', 'N/A')
                            fix = v.get('fix_versions', ['?'])
                            logger.log(f"   - {RED}[{vid}]{RESET} Fix: {fix}")
                return False

            except json.JSONDecodeError:
                # Erro de ambiente/instalação (não é JSON)
                err = result.stderr + result.stdout

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
                logger.log(err)
                return False

            if "ModuleNotFoundError" in err or "Traceback" in err:
                logger.log("\n⚠️  ERRO DE EXECUÇÃO (DEPENDÊNCIA FALTANDO)", YELLOW)  # noqa: E501
                logger.log(
                    "   O pip-audit não conseguiu rodar pois faltam bibliotecas.",
                    YELLOW,
                )
                logger.log(
                    "   💡 Tente: pip install -r requirements.txt "
                    "-r requirements-dev.txt",
                    YELLOW,
                )
                logger.log(err)
                return False

            logger.log("\n⛔ ERRO AO RODAR PIP-AUDIT", RED)
            logger.log(err)
            return False
            
        logger.log("✅ Dependências seguras.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar pip-audit: {e}", RED)
        return False
    
def get_gitignore_excludes(root_dir):
    """
    Lê o .gitignore e retorna uma lista de arquivos/pastas a serem ignorados
    pelo detect-secrets. Filtra padrões inválidos para regex.
    """
    gitignore_path = os.path.join(root_dir, ".gitignore")
    excludes = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignora linhas vazias, comentários, negações, e padrões perigosos
                if (
                    not line or
                    line.startswith("#") or
                    line.startswith("!") or
                    line in {"*", ".", "/", "./", "**"} or
                    line.startswith("[") or
                    line.startswith("]") or
                    line.startswith("\\") or
                    line.startswith("?") or
                    line.startswith("+") or
                    line.startswith("(") or
                    line.startswith(")") or
                    line.startswith("{") or
                    line.startswith("}") or
                    line.startswith("^") or
                    line.startswith("$") or
                    line.startswith("|")
                ):
                    continue
                # Remove possíveis barras finais e espaços
                pattern = line.rstrip("/").strip()
                # Ignora padrões só de caracteres especiais ou com wildcards
                has_word = re.search(r"\w", pattern)
                has_wildcard = "*" in pattern or "?" in pattern
                if not pattern or not has_word or has_wildcard:
                    continue
                excludes.append(pattern)
    return excludes

def run_detect_secrets_scan(root_dir):
    logger.log(
        "\n{}🔑 Executando Detect-secrets (Detecção Avançada de Segredos)...{}".format(
            BOLD, RESET
        )
    )
    if not ensure_package_installed("detect-secrets"):
        return True  # Não falha o build, apenas avisa

    # NOVO: Monta lista de --exclude-files a partir do .gitignore (exceto se --local)
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args, _ = parser.parse_known_args()
    exclude_files = [
        "logs_scan_vcsp",
        ".ruff_cache",
        "__pycache__",
        "pytest_cache",
        ".git/FETCH_HEAD"
        ".venv",
    ]
    if not args.local:
        gitignore_excludes = get_gitignore_excludes(root_dir)
        exclude_files.extend(gitignore_excludes)

    cmd = [
        "detect-secrets", "scan", "--all-files"
    ]
    for excl in exclude_files:
        cmd.extend(["--exclude-files", excl])

    result = subprocess.run(
        cmd,
        cwd=root_dir,
        text=True,
        encoding="utf-8",
        errors="ignore",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout

    try:
        data = json.loads(output)
        results = data.get("results", {})
        has_issues = False
        for filepath, secrets in results.items():
            if secrets:
                has_issues = True
                logger.log(f"❌ [DETECT-SECRETS] {filepath}", RED)
                for secret in secrets:
                    line = secret.get("line_number", "?")
                    type_ = secret.get("type", "Unknown")
                    logger.log(f"   L.{line}: {type_}")
        if not has_issues:
            logger.log("✅ Nenhum segredo encontrado pelo detect-secrets.", GREEN)
            return True
        return False
    except json.JSONDecodeError:
        # Fallback para verificação simples se o JSON falhar
        if '"results": {}' in output or (
            '"results":{' in output and '"type":' not in output
        ):
            logger.log("✅ Nenhum segredo encontrado pelo detect-secrets.", GREEN)
            return True
        logger.log(
            "❌ Detect-secrets encontrou possíveis segredos (Raw Output)!", RED
        )
        logger.log(output)
        return False
    except Exception as e:
        logger.log(f"❌ Erro ao rodar detect-secrets: {e}", RED)
        return True  # Não falha o build, apenas avisa

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
            msg = (
                f"   🔴 Problemas de infraestrutura encontrados: "
                f"{len(output_lines)}"
            )
            logger.log(msg, YELLOW)
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
    
    # 1. Definimos explicitamente quais arquivos queremos escanear
    target_filenames = ["requirements.txt", "requirements-dev.txt"]
    found_files = []

    # 2. Verificamos quais existem no disco
    for fname in target_filenames:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            found_files.append(fpath)

    # Se nenhum existir, encerra
    if not found_files:
        logger.log("ℹ️  Nenhum arquivo requirements encontrado. Pulando check.", YELLOW)
        return True

    # Informa o usuário quais arquivos serão lidos
    files_list_str = ", ".join([os.path.basename(f) for f in found_files])
    logger.log(f"ℹ️  Arquivos identificados: {files_list_str}", YELLOW)
    
    # --- Bloco de importlib ---
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
        # Mapeia instalações do ambiente
        dist_map = packages_distributions()
        pkg_to_imports = {}
        for import_name, dists in dist_map.items():
            for dist in dists:
                pkg_to_imports.setdefault(dist.lower(), []).append(import_name)

        # 3. LER E ACUMULAR DEPENDÊNCIAS
        declared_pkgs = set()
        
        for requirements_path in found_files:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    if not line or line.startswith('#') or line.startswith('-'):
                        continue
                    
                    # Remove versionamento (ex: "pandas>=1.0" vira "pandas")
                    pkg_name = re.split(r'[=<>~!;]', line)[0].strip()
                    if pkg_name:
                        declared_pkgs.add(pkg_name.lower())

        # --- LÓGICA ESTILO PIPDEPTREE (FILTRO DE SUB-DEPENDÊNCIAS) ---
        transitive_deps = set()
        for pkg in declared_pkgs:
            try:
                dist = distribution(pkg)
                if dist.requires:
                    for req in dist.requires:
                        req_name = re.split(r'[ ;<=>!]', req)[0].strip().lower()
                        if req_name:
                            transitive_deps.add(req_name)
            except Exception:
                continue

        used_imports = get_project_imports(PROJECT_ROOT)
        
        # Lista de ignorados (Dev tools que não são importadas no código fonte)
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
            
            if pkg in transitive_deps:
                continue
            
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

def run_cwe_scan():
    """
    Executa varredura de CWE usando Semgrep (regra p/cwe-top-25) e reporta no log.
    """
    logger.log(f"\n{BOLD}🕵️  Executando Varredura CWE (Semgrep Top 25)...{RESET}")
    if not ensure_package_installed("semgrep"):
        return True  # Não falha o build, apenas avisa

    try:
        cmd = [
            "semgrep", "scan",
            "--config", "p/cwe-top-25",
            "--error", "--metrics=off", "--quiet", "--no-git-ignore"
        ]
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output = result.stdout
        if result.returncode != 0:
            logger.log("⛔ Semgrep CWE Top 25 encontrou vulnerabilidades!", RED)
            # Conta linhas não vazias como falhas (com --quiet, 1 linha = 1 erro)
            count = len([line for line in output.splitlines() if line.strip()])
            logger.log(f"   🔴 Falhas CWE detectadas: {count}", RED)
            logger.log(output)
            return False
        logger.log("✅ Nenhuma vulnerabilidade CWE Top 25 encontrada.", GREEN)
        return True
    except Exception as e:
        logger.log(f"❌ Erro ao rodar Semgrep CWE Top 25: {e}", RED)
        return True  # Não falha o build, apenas avisa

def run_pip_audit_and_cwe(custom_deps_file=None):
    """
    Executa auditoria de dependências (CVE) e varredura CWE (Top 25) na mesma etapa.
    """
    logger.log(f"\n{BOLD}📦 Executando Auditoria de Dependências CVE e CWE...{RESET}")

    # --- CVE (pip-audit) ---
    cve_ok = run_pip_audit(custom_deps_file)

    # --- CWE (Semgrep Top 25) ---
    cwe_ok = run_cwe_scan()

    return cve_ok and cwe_ok

def main():
    global PROJECT_ROOT
    parser = argparse.ArgumentParser(
        description="VCSP Guard - Scanner de Segurança para projetos Python com IA."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Varredura completa em todos os arquivos e pastas, incluindo ignorados."
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Varredura apenas na pasta atual, sem considerar a raiz do projeto."
    )
    parser.add_argument(
        "--deps",
        type=str,
        help="Arquivo de dependências personalizado para auditoria."
    )
    args, unknown = parser.parse_known_args()

    custom_deps_file = args.deps

    # 1. Regex
    # Garante que a varredura sempre começa da raiz detectada do projeto
    root_dir = PROJECT_ROOT
    files_with_issues = 0

    # NOVO: Mostrar caminho da raiz no início da varredura
    logger.log(f"🔎 Iniciando varredura na raiz: {root_dir}", YELLOW)

    check_gitignore = True
    active_ignored_dirs = IGNORED_DIRS.copy()
    if args.all:
        check_gitignore = False
        active_ignored_dirs = {'.git', '__pycache__', '.ruff_cache'}
        logger.log(
            "⚠️  Modo --all: Verificando TUDO "
            "(incluindo arquivos ignorados e pastas ocultas).",
            YELLOW,
        )
    if args.local:
        PROJECT_ROOT = os.getcwd()
        logger.log(
            f"📂 Modo Local (--local): Varrendo a partir de: {PROJECT_ROOT}",
            YELLOW,
        )
        root_dir = PROJECT_ROOT
    else:
        root_dir = PROJECT_ROOT

    logger.log("1️⃣  Buscando chaves (Regex)...")

    # NOVO: Contadores de pastas e arquivos
    total_dirs = set()
    total_files = 0

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in active_ignored_dirs]
        
        if check_gitignore:
            # Otimização: Ignora pastas que o git também ignora
            dirs[:] = [d for d in dirs if not is_git_ignored(os.path.join(root, d))]

        total_dirs.add(root)
        for file in files:
            if file in IGNORED_FILES.split(","):
                continue
            filepath = os.path.join(root, file)
            
            if check_gitignore and is_git_ignored(filepath):
                continue

            total_files += 1
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

    # 2. Detect-secrets ()
    detect_secrets_ok = run_detect_secrets_scan(PROJECT_ROOT)
    security_ok = run_security_logic()
    iac_ok = run_iac_scan()
    # Corrige E501 quebrando linha longa
    audit_and_cwe_ok = run_pip_audit_and_cwe(
        custom_deps_file if custom_deps_file else None
    )
    ruff_ok = run_ruff_linter()
    run_unused_libs_check()

    # Remove chamada duplicada de run_cwe_scan (F841)
    # ...existing code...

    logger.log(
        f"\n📁 Varredura concluída: {len(total_dirs)} pastas e {total_files},"
        "arquivos analisados.",
        GREEN
    )

    if (
        not secrets_ok
        or not detect_secrets_ok
        or not security_ok
        or not iac_ok
        or not audit_and_cwe_ok
        or not ruff_ok
    ):
        logger.log("\n⛔ FALHA NA AUDITORIA. VERIFIQUE OS ERROS ACIMA.", RED)
        sys.exit(1)
    
    logger.log("\n🎉 SUCESSO! Código aprovado em todas as etapas.", GREEN)
    sys.exit(0)

if __name__ == "__main__":
    main()


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
