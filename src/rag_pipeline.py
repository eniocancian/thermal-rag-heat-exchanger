from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# 1. Conectar ao banco vetorial ChromaDB persistido anteriormente
chroma_dir = Path("data/processed/chroma_db")
client = chromadb.PersistentClient(path=str(chroma_dir))

# Configurar a mesma função de embeddings utilizada na indexação
embedding_func = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(
    name="heat_exchanger_operations",
    embedding_function=embedding_func
)

# 2. Função de busca por similaridade semântica
def buscar_contexto(query_text: str, n_resultados: int = 3):
    """
    Recebe uma pergunta ou condição operacional em texto
    e retorna os n_resultados mais similares do banco vetorial.
    """
    resultados = collection.query(
        query_texts=[query_text],
        n_results=n_resultados
    )
    return resultados

# 3. Teste prático de busca
if __name__ == "__main__":
    pergunta_teste = "Qual a condição de operação para obter uma carga térmica próxima a 120 kW com temperatura de entrada de 373 K?"
    print(f"Consulta: {pergunta_teste}\n")
    
    res = buscar_contexto(pergunta_teste, n_resultados=3)
    
    print("--- Melhores Resultados Recuperados (Top Matches) ---")
    for i, doc in enumerate(res["documents"][0]):
        distancia = res["distances"][0][i] if "distances" in res else "N/A"
        print(f"\nResultado #{i+1} (Distância/Similaridade: {distancia:.4f}):")
        print(doc)