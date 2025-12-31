import shutil
import importlib.util
import sys
from pathlib import Path
import inspect

def test_security_tools_installed():
    """
    Verifica se as ferramentas de segurança esperadas estão no PATH.
    Bandit foi substituído por ruff.
    """
    required_tools = ["ruff", "pip-audit"]
    if sys.platform != "win32":
        required_tools.append("semgrep")
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    if missing:
        msg = "Ferramentas de segurança faltando no PATH: " + ", ".join(missing)
    else:
        msg = ""
    assert not missing, msg  # noqa: S101

def test_project_structure_integrity():
    """
    Verifica se arquivos críticos do projeto existem.
    """
    critical_files = [
        "pyproject.toml",
        ".gitignore"
    ]
    for file in critical_files:
        assert Path(file).exists(), f"Arquivo crítico ausente: {file}"  # noqa: S101

def _load_scan_module():
    scan_path = Path("src/vcsp_guard/scan_project.py")
    assert scan_path.exists(), "Arquivo src/vcsp_guard/scan_project.py não encontrado"  # noqa: S101
    spec = importlib.util.spec_from_file_location("scan_project", str(scan_path))
    assert spec is not None, "spec_from_file_location retornou None"  # noqa: S101
    assert spec.loader is not None, "spec.loader é None — loader ausente"  # noqa: S101
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_scanner_module_integrity():
    """
    Verifica se o módulo de scan é importável e exporta as funções principais esperadas.
    Atualizado para exigir run_ruff em vez de run_bandit.
    """
    module = _load_scan_module()
    assert hasattr(module, "main"), "O script deve expor main()"  # noqa: S101
    assert hasattr(module, "run_iac_scan"), "Deve expor run_iac_scan()"  # noqa: S101
    assert hasattr(module, "run_ruff"), "Deve expor run_ruff()"  # noqa: S101

    # Verifica existência de uma função de auditoria para pip-audit (nome flexível)
    has_pip_audit = (
        any(name in dir(module) for name in ("run_pip_audit", "run_audit"))
        or any("audit" in name for name in dir(module))
    )
    assert has_pip_audit, "Função para pip-audit ausente (ex: run_pip_audit)"  # noqa: S101

def test_function_signatures_and_callables():
    """Verifica se funções principais são chamáveis e têm assinaturas razoáveis."""
    module = _load_scan_module()
    candidates = (
        "run_ruff",
        "run_iac_scan",
        "run_pip_audit",
        "run_audit",
    )
    for name in candidates:
        if not hasattr(module, name):
            continue
        fn = getattr(module, name)
        assert callable(fn), f"{name} não é chamável"  # noqa: S101
        try:
            sig = inspect.signature(fn)
        except Exception:  # noqa: S112
            # sem assinatura disponível, ignora
            continue
        required = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            and p.default is p.empty
        ]
        assert len(required) <= 2, (  # noqa: S101
            f"{name} tem muitos parâmetros posicionais "
            f"({len(required)})"
        )

def test_no_unexpected_side_effects_on_import():
    """
    Importar o módulo não deve executar scanners imediatamente (evitar side effects).
    """
    scan_path = Path("src/vcsp_guard/scan_project.py")
    assert scan_path.exists(), "Arquivo src/vcsp_guard/scan_project.py não encontrado"  # noqa: S101
    # carregar o código em um novo namespace e garantir ausência de execução imediata
    module = _load_scan_module()
    # procura por variáveis que indicam execução imediata
    suspicious_globals = [
        name
        for name in ("last_scan_result", "scan_results", "FOUND_ISSUES")
        if name in vars(module)
    ]
    assert not suspicious_globals, "Módulo não deve executar scans na importação"  # noqa: S101