import sys
import importlib.metadata

def main():
    if "--version" in sys.argv or "-v" in sys.argv:
        try:
            version = importlib.metadata.version("vcsp-guard")
            print(f"vcsp-guard v{version}")
        except importlib.metadata.PackageNotFoundError:
            print("vcsp-guard (dev)")
    else:
        print("🛡️  Vibe Coding Security Protocol (VCSP)")
        print("\nComandos disponíveis:")
        print("  vcsp-init    -> Configurar hooks e IAs")
        print("  vcsp-scan    -> Varrer vulnerabilidades")
        print("  vcsp-stats   -> Gerar gráficos de bugs")
        print("  vcsp-guard --version -> Ver versão atual")

if __name__ == "__main__":
    main()