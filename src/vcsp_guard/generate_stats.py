import os
import glob
import re
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    print("📊 Gerando estatísticas de segurança (VCSP)...")
    
    # 1. Encontrar logs
    list_of_files = glob.glob('logs_scan_vcsp/scan_*.txt')
    if not list_of_files:
        print("⚠️  Nenhum log encontrado em logs_scan_vcsp/. Rode 'vcsp-scan' primeiro.")
        return

    # Ordenar por data (nome do arquivo contém timestamp)
    list_of_files.sort()

    # 2. Processar Histórico
    history = []
    
    print(f"📂 Processando {len(list_of_files)} logs...")

    for log_file in list_of_files:
        stats = {
            'date': '', 
            'secrets': 0, 
            'detect_secrets': 0,  # Novo campo para detect-secrets
            'bandit': 0, 
            'audit': 0, 
            'ruff': 0, 
            'semgrep': 0
        }
        
        # Extrair data do nome do arquivo: scan_2025-12-15_11-10-45.txt
        filename = os.path.basename(log_file)
        try:
            date_part = filename.replace("scan_", "").replace(".txt", "")
            dt = datetime.strptime(date_part, "%Y-%m-%d_%H-%M-%S")
            stats['date'] = dt.strftime('%d/%m %H:%M')
        except ValueError:
            stats['date'] = "Unknown"

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Regex baseados na saída do scan_project.py
            stats['secrets'] = len(re.findall(r'❌ \[SEGREDO\]', content))
            # Novo: detect-secrets
            stats['detect_secrets'] = len(re.findall(r'❌ Detect-secrets encontrou possíveis segredos!', content))
            
            bandit_match = re.search(r'Total issues: (\d+)', content)
            if bandit_match:
                stats['bandit'] = int(bandit_match.group(1))
            
            audit_match = re.search(r'Found (\d+) known vulnerabilit', content)
            if audit_match:
                stats['audit'] = int(audit_match.group(1))
            
            ruff_match = re.search(r'Found (\d+) error', content)
            if ruff_match:
                stats['ruff'] = int(ruff_match.group(1))
            
            semgrep_match = re.search(r'Found (\d+) infrastructure issues', content)
            if semgrep_match:
                stats['semgrep'] = int(semgrep_match.group(1))
        
        history.append(stats)

    # 3. Gerar Gráfico
    os.makedirs('.vibe/assets', exist_ok=True)
    output_img = '.vibe/assets/bug_trend.png'
    
    dates = [h['date'] for h in history]
    
    plt.figure(figsize=(12, 6))
    
    # Helper para plotar
    def plot_line(key, label, color):
        plt.plot(dates, [h[key] for h in history], label=label, marker='o', color=color)

    plot_line('secrets', 'Secrets', 'red')
    plot_line('detect_secrets', 'Detect-secrets', 'brown')
    plot_line('bandit', 'Bandit (Logic)', 'orange')
    plot_line('audit', 'Pip-Audit (Deps)', 'blue')
    plot_line('ruff', 'Ruff (Lint)', 'green')
    plot_line('semgrep', 'Semgrep (IaC)', 'purple')
    
    plt.title('Tendência de Vulnerabilidades (VCSP)')
    plt.xlabel('Execuções (Data/Hora)')
    plt.ylabel('Quantidade de Falhas')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_img)
    
    print(f"✅ Gráfico gerado com sucesso: {output_img}")

if __name__ == "__main__":
    main()