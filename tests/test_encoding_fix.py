"""
Testes para a correção de encoding em arquivos requirements.txt
"""
import tempfile
import os
from pathlib import Path
import importlib.util

def _load_scan_module():
    """Carrega o módulo scan_project.py"""
    root = Path(__file__).parent.parent
    scan_path = root / "src" / "vcsp_guard" / "scan_project.py"
    
    if not scan_path.exists():
        raise FileNotFoundError(f"scan_project.py não encontrado em {scan_path}")
    
    spec = importlib.util.spec_from_file_location("scan_project", str(scan_path))
    if spec is None or spec.loader is None:
        raise ImportError("Não foi possível carregar scan_project.py")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_read_file_utf8():
    """Testa leitura de arquivo UTF-8 normal"""
    module = _load_scan_module()
    
    # Cria um arquivo temporário com encoding UTF-8
    with tempfile.NamedTemporaryFile(
        mode='w', encoding='utf-8', delete=False, suffix='.txt'
    ) as f:
        f.write("requests==2.28.0\n")
        f.write("flask>=2.0.0\n")
        f.write("# comentário\n")
        temp_path = f.name
    
    try:
        content = module.read_file_with_encoding_fallback(temp_path)
        assert "requests" in content
        assert "flask" in content
        # fallback pode alterar caracteres
        assert "comentário" in content or "coment" in content
    finally:
        os.unlink(temp_path)

def test_read_file_latin1():
    """Testa leitura de arquivo com encoding Latin-1"""
    module = _load_scan_module()
    
    # Cria um arquivo temporário com encoding Latin-1
    with tempfile.NamedTemporaryFile(
        mode='w', encoding='latin-1', delete=False, suffix='.txt'
    ) as f:
        f.write("requests==2.28.0\n")
        f.write("flask>=2.0.0\n")
        f.write("# comentário com acentuação\n")
        temp_path = f.name
    
    try:
        content = module.read_file_with_encoding_fallback(temp_path)
        assert "requests" in content
        assert "flask" in content
        # Deve conseguir ler o arquivo mesmo com encoding diferente
        assert len(content) > 0
    finally:
        os.unlink(temp_path)

def test_read_file_with_bom():
    """Testa leitura de arquivo com UTF-8 BOM (Byte Order Mark)"""
    module = _load_scan_module()
    
    # Cria um arquivo com UTF-8 BOM (comum em Windows)
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        # UTF-8 BOM seguido de conteúdo normal
        f.write(b'\xef\xbb\xbf')  # UTF-8 BOM
        f.write(b"requests==2.28.0\n")
        f.write(b"flask>=2.0.0\n")
        temp_path = f.name
    
    try:
        content = module.read_file_with_encoding_fallback(temp_path)
        assert "requests" in content
        assert "flask" in content
    finally:
        os.unlink(temp_path)

def test_read_file_cp1252():
    """Testa leitura de arquivo com encoding CP1252 (Windows)"""
    module = _load_scan_module()
    
    # Cria um arquivo temporário com encoding CP1252
    with tempfile.NamedTemporaryFile(
        mode='w', encoding='cp1252', delete=False, suffix='.txt'
    ) as f:
        f.write("requests==2.28.0\n")
        f.write("numpy>=1.20.0\n")
        temp_path = f.name
    
    try:
        content = module.read_file_with_encoding_fallback(temp_path)
        assert "requests" in content
        assert "numpy" in content
    finally:
        os.unlink(temp_path)

def test_read_binary_file_with_fallback():
    """Testa que arquivos binários também são tratados (com errors='replace')"""
    module = _load_scan_module()
    
    # Cria um arquivo com bytes binários que não são texto válido
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        # Escreve alguns bytes válidos seguidos de bytes inválidos
        f.write(b"requests==2.28.0\n")
        f.write(b"\xff\xfe\x00invalid\x00")  # Bytes que causam erro em UTF-8
        temp_path = f.name
    
    try:
        # Deve conseguir ler sem causar exceção
        content = module.read_file_with_encoding_fallback(temp_path)
        # Pelo menos a primeira linha válida deve estar presente
        assert "requests" in content
    finally:
        os.unlink(temp_path)

def test_read_file_starting_with_0xff():
    """Testa o caso específico do erro relatado: arquivo começando com 0xFF"""
    module = _load_scan_module()
    
    # Simula o caso exato do erro: arquivo que começa com 0xFF
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        # Byte 0xFF no início (que causava o erro original)
        f.write(b"\xff")
        f.write(b"requests==2.28.0\n")
        f.write(b"flask>=2.0.0\n")
        f.write(b"django==4.0\n")
        temp_path = f.name
    
    try:
        # Deve conseguir ler sem causar exceção
        content = module.read_file_with_encoding_fallback(temp_path)
        # O conteúdo deve ser legível (pode ter caractere de substituição no início)
        assert len(content) > 0
        # As linhas de pacotes devem estar presentes
        assert "requests" in content or "flask" in content or "django" in content
    finally:
        os.unlink(temp_path)
