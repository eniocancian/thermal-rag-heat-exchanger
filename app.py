from pathlib import Path
from datetime import datetime
import re
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from google import genai
import plotly.graph_objects as go
from fpdf import FPDF

# Importação da camada de física modularizada
from src.physics import validar_registro_termodinamico

# Configuração da página
st.set_page_config(
    page_title="RAG - Eficiência em Trocadores de Calor",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Assistente Técnico: Trocadores de Calor & RAG Industrial")
st.caption("Consulta semântica com auditoria termodinâmica física prévia, gráficos e exportação executiva em PDF.")

BASE_DIR = Path(__file__).resolve().parent

@st.cache_resource
def carregar_colecao():
    chroma_dir = BASE_DIR / "data" / "processed" / "chroma_db"
    client = chromadb.PersistentClient(path=str(chroma_dir))
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    return client.get_collection(
        name="heat_exchanger_operations",
        embedding_function=embedding_func
    )

try:
    collection = carregar_colecao()
except Exception as e:
    st.error(f"Erro ao carregar o banco vetorial: {e}")
    st.stop()

# Sanitizador de texto técnico e fórmulas LaTeX para FPDF
def limpar_texto_para_pdf(texto: str) -> str:
    if not texto:
        return ""
    t = re.sub(r"\\text\{([^}]+)\}", r"\1", texto)
    t = re.sub(r"\\Delta", "Delta", t)
    t = re.sub(r"\\dot\{([^}]+)\}", r"\1", t)
    t = re.sub(r"\\circ", "o", t)
    t = re.sub(r"\$+", "", t)
    t = re.sub(r"\\", "", t)
    t = t.replace("**", "").replace("### ", "").replace("## ", "").replace("# ", "")
    t = t.replace("→", "->").replace("≈", "~").replace("Δ", "Delta ").replace("∘", "o").replace("˙", "")
    return t.encode("latin-1", "replace").decode("latin-1")

# Gerador de Relatório Técnico em PDF
def gerar_relatorio_pdf(query, filtros_str, analises, parecer_ia):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(12, 12, 12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cabeçalho Superior
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(0, 0, 210, 26, "F")
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(12, 6)
    pdf.cell(pdf.epw, 7, "RELATÓRIO TÉCNICO DE AUDITORIA E OPERAÇÃO TÉRMICA", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(203, 213, 225)
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    pdf.set_x(12)
    pdf.cell(pdf.epw, 5, f"Sistema RAG Termodinâmico Industrial | Emitido em: {data_emissao}", ln=True)
    
    pdf.ln(10)
    pdf.set_text_color(15, 23, 42)
    
    # Seção 1: Parâmetros da Solicitação
    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 6, "1. Parâmetros da Solicitação", ln=True)
    
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 8)
    query_limpa = limpar_texto_para_pdf(query)
    filtros_limpos = limpar_texto_para_pdf(filtros_str)
    pdf.multi_cell(w=pdf.epw, h=4.5, text=f"Consulta Operacional: {query_limpa}")
    pdf.set_x(12)
    pdf.multi_cell(w=pdf.epw, h=4.5, text=f"Filtros Aplicados: {filtros_limpos}")
    pdf.ln(3)
    
    # Seção 2: Tabela Comparativa
    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 6, "2. Avaliação Comparativa dos Registros Recuperados", ln=True)
    
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(226, 232, 240)
    
    col_w = [18, 25, 25, 28, 28, 60]
    cols = ["Opção", "Carga (kW)", "LMTD (K)", "T_in Quente", "Delta T Quente", "Status Físico"]
    
    pdf.set_x(12)
    for w, c in zip(col_w, cols):
        c_clean = c.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(w, 6.5, c_clean, border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 7.5)
    for idx, f in enumerate(analises):
        status_txt = "Validado" if f.fisicamente_valido else "Anomalia Telemetria"
        dt_str = f"{f.delta_t_q:.1f} K" if f.delta_t_q is not None else "N/D"
        
        pdf.set_x(12)
        pdf.cell(col_w[0], 5.5, f"Opção {idx+1}", border=1, align="C")
        pdf.cell(col_w[1], 5.5, f"{f.heat_load_kw:.2f}", border=1, align="C")
        pdf.cell(col_w[2], 5.5, f"{f.lmtd_k:.2f}", border=1, align="C")
        pdf.cell(col_w[3], 5.5, f"{f.t_hot_in:.1f} K", border=1, align="C")
        pdf.cell(col_w[4], 5.5, dt_str, border=1, align="C")
        pdf.cell(col_w[5], 5.5, status_txt, border=1, align="C")
        pdf.ln()
    
    pdf.ln(4)
    
    # Seção 3: Síntese Técnica
    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(pdf.epw, 6, "3. Síntese Técnica e Recomendações Operacionais", ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    texto_formatado = limpar_texto_para_pdf(parecer_ia)
    pdf.set_x(12)
    pdf.multi_cell(w=pdf.epw, h=4.5, text=texto_formatado)
    
    return bytes(pdf.output())

# Barra lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Gemini API Key:", type="password", help="Insira sua chave do Google AI Studio")
    top_k = st.slider("Registros a recuperar (Top-K):", min_value=1, max_value=5, value=3)
    
    st.markdown("---")
    st.header("🎯 Filtros por Metadados")
    usar_filtro_q = st.checkbox("Filtrar por Carga Térmica (kW)", value=False)
    rango_q = st.slider("Faixa de Carga Térmica (kW):", min_value=0.0, max_value=250.0, value=(50.0, 150.0), step=5.0)
    
    usar_filtro_t = st.checkbox("Filtrar por Temp. de Entrada Quente (K)", value=False)
    rango_t = st.slider("Faixa de Temp. Quente (K):", min_value=300.0, max_value=600.0, value=(350.0, 550.0), step=10.0)

    st.markdown("---")
    st.markdown("**Status do Banco:**")
    st.write(f"Total de amostras indexadas: `{collection.count()}`")

# Campo de consulta
query_usuario = st.text_input(
    "Digite sua consulta técnica operacional:",
    value="Qual condição de operação atinge cerca de 120 kW com carga térmica estável?"
)

if st.button("Consultar Base Operacional", type="primary"):
    condicoes = []
    if usar_filtro_q:
        condicoes.append({"heat_load_kw": {"$gte": rango_q[0]}})
        condicoes.append({"heat_load_kw": {"$lte": rango_q[1]}})
    if usar_filtro_t:
        condicoes.append({"hot_inlet_k": {"$gte": rango_t[0]}})
        condicoes.append({"hot_inlet_k": {"$lte": rango_t[1]}})
    
    where_filtro = None
    if len(condicoes) == 1:
        where_filtro = condicoes[0]
    elif len(condicoes) > 1:
        where_filtro = {"$and": condicoes}

    with st.spinner("Buscando no banco vetorial..."):
        try:
            resultados = collection.query(
                query_texts=[query_usuario],
                n_results=top_k,
                where=where_filtro
            )
            docs = resultados["documents"][0] if resultados["documents"] else []
            distancias = resultados["distances"][0] if "distances" in resultados and resultados["distances"] else [0.0] * len(docs)
            metadados = resultados["metadatas"][0] if "metadatas" in resultados and resultados["metadatas"] else [{}] * len(docs)
        except Exception as err:
            st.error(f"Erro na consulta com filtros: {err}")
            docs = []

    if not docs:
        st.warning("Nenhum registro encontrado que atenda à consulta e aos filtros selecionados.")
    else:
        analises_fisicas = [
            validar_registro_termodinamico(meta, doc)
            for meta, doc in zip(metadados, docs)
        ]

        col_docs, col_llm = st.columns([1.1, 1.3])
        
        with col_docs:
            st.subheader("🎯 Contexto & Validação Física Prévia")
            for i, (doc, dist, meta, fisica) in enumerate(zip(docs, distancias, metadados, analises_fisicas)):
                with st.expander(f"Registro #{i+1} — Distância: {dist:.4f}", expanded=(i == 0)):
                    st.write(doc)
                    if not fisica.fisicamente_valido:
                        for anomalia in fisica.anomalias:
                            st.warning(f"⚠️ {anomalia}")
                    else:
                        st.success("✅ Balanço e coerência física validados sem inconsistências.")
                    
                    if fisica.delta_t_q is not None:
                        st.info(f"**Delta T Lado Quente Calculado:** {fisica.delta_t_q:.2f} K")

                    st.json(meta)

        with col_llm:
            st.subheader("💡 Parecer Técnico da IA")
            if not api_key:
                st.warning("Insira sua Gemini API Key na barra lateral para sintetizar o diagnóstico com o LLM.")
            else:
                with st.spinner("Gerando análise técnica com auditoria física..."):
                    try:
                        contexto_enriquecido = []
                        for idx, (d, f) in enumerate(zip(docs, analises_fisicas)):
                            status_fisico = "SEM ANOMALIAS" if f.fisicamente_valido else f"ANOMALIA: {'; '.join(f.anomalias)}"
                            delta_info = f"Delta Tq Calculado: {f.delta_t_q:.2f} K" if f.delta_t_q else "Delta Tq: N/D"
                            contexto_enriquecido.append(
                                f"Opção {idx+1}:\n- Dados Brutos: {d}\n- Status Físico do Sistema: {status_fisico}\n- {delta_info}"
                            )
                        contexto_str = "\n\n".join(contexto_enriquecido)

                        prompt = f"""
Você é um engenheiro especialista em termodinâmica e eficiência energética em trocadores de calor industriais.
O pipeline de auditoria física pré-RAG calculou automaticamente consistências e inconsistências para os registros recuperados.

Pergunta do Operador:
"{query_usuario}"

Contexto Operacional com Pré-Auditoria Termodinâmica:
{contexto_str}

Instruções:
1. Avalie qual dos registros melhor atende à condição solicitada.
2. Analise os parâmetros-chave: Carga térmica (kW), LMTD (K), vazões e o gradiente térmico calculado (ΔTq).
3. Leve em consideração formalmente as anomalias detectadas pelo pré-processamento de física na sua recomendação de instrumentação/manutenção.
4. Forneça uma recomendação operacional concisa e os setpoints recomendados.
"""
                        client_ai = genai.Client(api_key=api_key)
                        resposta = client_ai.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=prompt
                        )
                        texto_parecer = resposta.text
                        st.markdown(texto_parecer)
                        
                        filtros_desc = f"Carga: {rango_q if usar_filtro_q else 'Sem filtro'} | Temp. Quente: {rango_t if usar_filtro_t else 'Sem filtro'}"
                        
                        pdf_bytes = gerar_relatorio_pdf(
                            query=query_usuario,
                            filtros_str=filtros_desc,
                            analises=analises_fisicas,
                            parecer_ia=texto_parecer
                        )

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            st.download_button(
                                label="📄 Baixar Relatório Executivo (.pdf)",
                                data=pdf_bytes,
                                file_name="relatorio_tecnico_trocador.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                        with col_btn2:
                            relatorio_txt = f"""====================================================
RELATÓRIO DE OPERAÇÃO E AVALIAÇÃO TÉRMICA (RAG)
====================================================
Consulta do Operador: {query_usuario}
Filtros: {filtros_desc}
----------------------------------------------------
{contexto_str}
----------------------------------------------------
PARECER:
{texto_parecer}
====================================================
"""
                            st.download_button(
                                label="📥 Baixar Registro Texto (.txt)",
                                data=relatorio_txt,
                                file_name="parecer_trocador_rag.txt",
                                mime="text/plain"
                            )
                    except Exception as err:
                        st.error(f"Erro ao processar o relatório ou IA: {err}")

        # Gráficos
        st.markdown("---")
        st.subheader("📊 Diagnóstico Gráfico das Opções Recuperadas")

        labels = [f"Opção {i+1}" for i in range(len(docs))]
        heat_loads = [m.get("heat_load_kw", 0.0) for m in metadados]
        lmtds = [m.get("lmtd_k", 0.0) for m in metadados]
        hot_inlets = [m.get("hot_inlet_k", 0.0) for m in metadados]

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=labels, 
                y=heat_loads, 
                name="Carga Térmica (kW)", 
                marker_color="#EF4444"
            ))
            fig_bar.add_trace(go.Bar(
                x=labels, 
                y=lmtds, 
                name="LMTD (K)", 
                marker_color="#3B82F6"
            ))
            fig_bar.add_hline(
                y=120.0, 
                line_dash="dot", 
                line_color="#10B981", 
                annotation_text="Meta (120 kW)", 
                annotation_position="top left"
            )
            fig_bar.update_layout(
                title="Carga Térmica vs. LMTD vs. Meta Operacional",
                barmode="group",
                template="plotly_dark",
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=labels,
                y=hot_inlets,
                mode="lines+markers+text",
                name="Temp. Entrada Quente (K)",
                text=[f"{t:.1f} K" for t in hot_inlets],
                textposition="top center",
                line=dict(color="#F59E0B", width=3),
                marker=dict(size=10)
            ))
            fig_temp.update_layout(
                title="Temperatura de Alimentação do Fluido Quente",
                yaxis_title="Temperatura (K)",
                template="plotly_dark",
                height=380
            )
            st.plotly_chart(fig_temp, use_container_width=True)