"""
Pipeline de ingestão vetorial em lotes para ChromaDB.
"""
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "processed" / "chroma_db"


def ingest_data_in_batches(batch_size: int = 500):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="heat_exchanger_operations",
        embedding_function=embedding_func
    )
    
    print(f"Indexando dados na coleção... (Status atual: {collection.count()} registros)")

    # Exemplo sintético simulando telemetria se necessário re-indexar
    # ou caso você conecte ao seu dataframe original:
    total_registros = 1000
    ids = [f"hex_{i:05d}" for i in range(total_registros)]
    docs = [
        f"Operação industrial estável. Carga: {80 + (i % 60):.2f} kW. Temperatura de saída quente: {360 + (i % 30):.1f} K. Temperatura de saída fria: {310 + (i % 20):.1f} K."
        for i in range(total_registros)
    ]
    metas = [
        {
            "heat_load_kw": float(80 + (i % 60)),
            "hot_inlet_k": float(480 + (i % 40)),
            "lmtd_k": float(75 + (i % 35))
        }
        for i in range(total_registros)
    ]

    # Inserção controlada em lotes para evitar sobrecarga de memória
    for start_idx in tqdm(range(0, total_registros, batch_size), desc="Ingestão Vetorial"):
        end_idx = min(start_idx + batch_size, total_registros)
        collection.upsert(
            ids=ids[start_idx:end_idx],
            documents=docs[start_idx:end_idx],
            metadatas=metas[start_idx:end_idx]
        )

    print(f"Ingestão concluída com sucesso. Total armazenado: {collection.count()}")


if __name__ == "__main__":
    ingest_data_in_batches()