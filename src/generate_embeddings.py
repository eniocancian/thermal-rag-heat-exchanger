from pathlib import Path
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# Ancorar o caminho na raiz do projeto (uma pasta acima de 'src')
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Carregar os dados completos
csv_path = BASE_DIR / "data" / "raw" / "heat_exchanger_dataset.csv"
df = pd.read_csv(csv_path)

total_linhas = len(df)
print(f"Total de registos carregados: {total_linhas}")

# Selecionar apenas as colunas limpas/reais (sem ruído artificial)
colunas_uteis = [
    'hot_inlet_temperature_k',
    'hot_outlet_temperature_k',
    'cold_outlet_temperature_k',
    'cold_inlet_mass_flow_kg_s',
    'hot_outlet_mass_flow_kg_s',
    'cold_outlet_mass_flow_kg_s',
    'hx_1_heat_load_kw',
    'hx_1_logarithmic_mean_temperature_difference_lmtd_k'
]

df_clean = df[colunas_uteis].copy().reset_index(drop=True)

# 2. Função de conversão tabular -> textual
def row_to_text(row, idx):
    return (
        f"Registo Operacional #{idx}: "
        f"Temperatura de entrada quente: {row['hot_inlet_temperature_k']:.2f} K. "
        f"Temperatura de saída quente: {row['hot_outlet_temperature_k']:.2f} K. "
        f"Temperatura de saída fria: {row['cold_outlet_temperature_k']:.2f} K. "
        f"Vazão mássica fria na entrada: {row['cold_inlet_mass_flow_kg_s']:.3f} kg/s. "
        f"Vazão mássica quente na saída: {row['hot_outlet_mass_flow_kg_s']:.3f} kg/s. "
        f"Vazão mássica fria na saída: {row['cold_outlet_mass_flow_kg_s']:.3f} kg/s. "
        f"Carga térmica transferida (Heat Load): {row['hx_1_heat_load_kw']:.2f} kW. "
        f"LMTD (Média Logarítmica das Diferenças de Temperatura): {row['hx_1_logarithmic_mean_temperature_difference_lmtd_k']:.2f} K."
    )

print("A converter todas as linhas em documentos estruturados...")
documentos = [row_to_text(row, i) for i, row in df_clean.iterrows()]
ids = [f"hx_doc_{i}" for i in range(total_linhas)]
metadados = [
    {
        "heat_load_kw": float(row["hx_1_heat_load_kw"]),
        "lmtd_k": float(row["hx_1_logarithmic_mean_temperature_difference_lmtd_k"]),
        "hot_inlet_k": float(row["hot_inlet_temperature_k"])
    }
    for _, row in df_clean.iterrows()
]

# 3. Inicializar ChromaDB e recriar a coleção usando o caminho absoluto
chroma_dir = BASE_DIR / "data" / "processed" / "chroma_db"
client = chromadb.PersistentClient(path=str(chroma_dir))
embedding_func = embedding_functions.DefaultEmbeddingFunction()

# Elimina a coleção anterior para recriar com a base completa
try:
    client.delete_collection("heat_exchanger_operations")
    print("Coleção anterior removida com sucesso.")
except Exception:
    pass

collection = client.create_collection(
    name="heat_exchanger_operations",
    embedding_function=embedding_func
)

# 4. Inserção em lotes (batch processing de 1.000 em 1.000)
batch_size = 1000
print(f"\nA gerar embeddings e a gravar {total_linhas} registos no ChromaDB em lotes de {batch_size}...")

for start_idx in range(0, total_linhas, batch_size):
    end_idx = min(start_idx + batch_size, total_linhas)
    
    collection.add(
        documents=documentos[start_idx:end_idx],
        metadatas=metadados[start_idx:end_idx],
        ids=ids[start_idx:end_idx]
    )
    print(f"Progresso: {end_idx}/{total_linhas} registos indexados ({(end_idx/total_linhas)*100:.1f}%)")

print(f"\nConcluído com sucesso! Total no banco vetorial: {collection.count()} registos.")