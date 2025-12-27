import shutil
import importlib.util
import sys
from pathlib import Path
import pytest

def test_security_tools_installed():
    """
    Verifica se as ferramentas de segurança do VCSP estão disponíveis no ambiente.
    Isso evita falhas silenciosas no CI/CD ou localmente.
    """
    required_tools = ["bandit", "ruff", "pip-audit"]
    
    if sys.platform != "win32":
        required_tools.append("semgrep")
    
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    assert not missing, f"Ferramentas de segurança faltando no PATH: {', '.join(missing)}"

def test_project_structure_integrity():
    """
    Verifica se a estrutura crítica do Vibe Coding está intacta.
    """
    critical_files = [
        "pyproject.toml",
        ".gitignore"
    ]
    for file in critical_files:
        assert Path(file).exists(), f"Arquivo crítico ausente: {file}"

def test_scanner_module_integrity():
    """
    Verifica se o módulo de scan (vcsp_guard) é importável e se as novas funções existem.
    """
    scan_path = Path("src/vcsp_guard/scan_project.py")
    
    if scan_path.exists():
        spec = importlib.util.spec_from_file_location("scan_project", scan_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            pytest.fail(f"O script de scan contém erros de sintaxe ou importação: {e}")
        
        # Verifica se as funções principais existem
        assert hasattr(module, "main"), "O script de scan deve ter uma função main()"
        assert hasattr(module, "run_iac_scan"), "O scanner deve suportar IaC (Semgrep)"
        assert hasattr(module, "run_bandit"), "O scanner deve suportar Bandit"