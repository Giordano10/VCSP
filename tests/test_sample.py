import shutil
import importlib.util
import sys
from pathlib import Path
import inspect
import pytest

def test_security_tools_installed():
    """
    Verifica se as ferramentas de segurança esperadas estão no PATH.
    Bandit foi substituído por ruff.
    """
    required_tools = ["ruff", "pip-audit"]
    if sys.platform != "win32":
        required_tools.append("semgrep")
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    assert not missing, f"Ferramentas de segurança faltando no PATH: {', '.join(missing)}"

def test_project_structure_integrity():
    """
    Verifica se arquivos críticos do projeto existem.
    """
    critical_files = [
        "pyproject.toml",
        ".gitignore"
    ]
    for file in critical_files:
        assert Path(file).exists(), f"Arquivo crítico ausente: {file}"

def _load_scan_module():
    scan_path = Path("src/vcsp_guard/scan_project.py")
    assert scan_path.exists(), "Arquivo src/vcsp_guard/scan_project.py não encontrado"
    spec = importlib.util.spec_from_file_location("scan_project", str(scan_path))
    assert spec is not None, "spec_from_file_location retornou None"
    assert spec.loader is not None, "spec.loader é None — não foi possível determinar um loader para o arquivo"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_scanner_module_integrity():
    """
    Verifica se o módulo de scan é importável e exporta as funções principais esperadas.
    Atualizado para exigir run_ruff em vez de run_bandit.
    """
    module = _load_scan_module()
    assert hasattr(module, "main"), "O script de scan deve ter uma função main()"
    assert hasattr(module, "run_iac_scan"), "O scanner deve suportar IaC (Semgrep) via run_iac_scan()"
    assert hasattr(module, "run_ruff"), "O scanner deve suportar ruff via run_ruff()"

    # Verifica existência de uma função de auditoria para pip-audit (nome flexível)
    has_pip_audit = any(name in dir(module) for name in ("run_pip_audit", "run_audit")) or any("audit" in name for name in dir(module))
    assert has_pip_audit, "Deve existir uma função para executar pip-audit (ex: run_pip_audit ou run_audit)"

def test_function_signatures_and_callables():
    """
    Verifica se as principais funções são chamáveis e expõem assinaturas razoáveis (sem execução de ferramentas externas).
    """
    module = _load_scan_module()
    for fname in ("main", "run_iac_scan", "run_ruff"):
        func = getattr(module, fname, None)
        assert callable(func), f"{fname} deve ser uma função chamável"
        sig = inspect.signature(func)
        # permite funções sem parâmetros ou com parâmetros opcionais; rejeita funções que exigem muitos argumentos posicionais obrigatórios (>2)
        required_positional = [p for p in sig.parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is p.empty]
        assert len(required_positional) <= 2, f"{fname} tem muitos parâmetros posicionais obrigatórios ({len(required_positional)}) — considere permitir parâmetros opcionais ou kwargs"

def test_no_unexpected_side_effects_on_import():
    """
    Importar o módulo não deve executar scanners imediatamente (evitar side effects).
    """
    scan_path = Path("src/vcsp_guard/scan_project.py")
    assert scan_path.exists(), "Arquivo src/vcsp_guard/scan_project.py não encontrado"
    # carregar o código em um novo namespace e garantir que não haja variáveis globais indicando execução imediata
    module = _load_scan_module()
    # procura por variáveis que normalmente indicam execução (ex.: resultados globais imediatamente preenchidos)
    suspicious_globals = [name for name in ("last_scan_result", "scan_results", "FOUND_ISSUES") if name in vars(module)]
    assert not suspicious_globals, f"O módulo não deve executar scans na importação; remova side-effects globais: {', '.join(suspicious_globals)}"