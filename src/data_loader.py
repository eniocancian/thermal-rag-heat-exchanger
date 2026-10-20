import os
from pathlib import Path
import pandas as pd

# Caminhos base
raw_dir = Path("data/raw")

# Listar todos os arquivos presentes na pasta raw
arquivos_encontrados = list(raw_dir.glob("*"))
print("Arquivos encontrados em data/raw:")
for arq in arquivos_encontrados:
    print(f" - {arq.name} ({arq.stat().st_size / (1024 * 1024):.2f} MB)")

# Localizar o arquivo CSV
csv_files = list(raw_dir.glob("*.csv"))

if not csv_files:
    print("\nNenhum arquivo .csv encontrado em data/raw.")
else:
    target_csv = csv_files[0]
    print(f"\nCarregando dados de: {target_csv.name}...")
    df = pd.read_csv(target_csv)
    
    print("\n--- Informações do Dataset ---")
    print(f"Total de linhas: {df.shape[0]:,}")
    print(f"Total de colunas: {df.shape[1]}")
    
    print("\n--- Colunas disponíveis ---")
    for col in df.columns:
        print(f" • {col}")
        
    print("\n--- Primeiras 3 linhas ---")
    print(df.head(3))