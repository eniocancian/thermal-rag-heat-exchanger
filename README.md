Markdown
# ⚙️ Thermal-RAG: Industrial Heat Exchanger Optimization & Anomaly Detection

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange)](https://www.trychroma.com/)
[![LLM](https://img.shields.io/badge/Google%20GenAI-Gemini%20Flash-4285F4?logo=google)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-green?logo=pytest)](https://pytest.org)

Sistema RAG (Retrieval-Augmented Generation) com camada analítica de **auditoria termodinâmica prévia** para recomendação de setpoints e diagnóstico operacional em trocadores de calor industriais.

---

## 🎯 Visão Geral do Projeto

Aplicações tradicionais de IA Generativa na indústria frequentemente falham ao alucinar sobre telemetrias corrompidas por instrumentação defeituosa. Este projeto implementa uma **arquitetura híbrida e orientada à física**:

1. **Recuperação Semântica com Metadados:** Busca vetorial de condições operacionais via ChromaDB combinada com filtros térmicos de carga e temperatura.
2. **Auditoria Física Pré-RAG (2ª Lei da Termodinâmica):** Algoritmo determinístico que audita leituras termicamente impossíveis (ex.: fluido frio saindo a temperaturas superiores à entrada quente devido a circuito aberto/burnout de termopar) antes de acionar o LLM.
3. **Síntese Especializada via LLM:** O Google Gemini sintetiza pareceres técnicos de engenharia química/mecânica, balanceamento térmico ($Q$, $\Delta T_{lm}$, vazões) e recomendações de manutenção industrial.
4. **Exportação Técnica Executiva:** Geração dinâmica de relatórios em formato PDF estruturado via FPDF2 e visualização interativa com Plotly.

---

## 🏗️ Arquitetura da Solução

[ Consulta do Operador ]
│
▼
[ Filtros de Metadados ] ──▶ [ ChromaDB (Base Vetorial) ]
│
▼
[ Validação Termodinâmica Prévia ]
(Verificação de 2ª Lei & Gradientes ΔT)
│
▼
[ Prompt Enriquecido ]
│
▼
[ Google Gemini Flash ]
│
┌─────────────────────┴─────────────────────┐
▼                                           ▼
[ Interface Streamlit ]                     [ Relatório PDF Executivo ]
(Métricas, Alertas, Plotly)                     (FPDF2 / Auditoria)


---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.10+
* **Interface:** Streamlit
* **Banco Vetorial:** ChromaDB
* **Modelo de IA:** Google Gemini (Google GenAI SDK)
* **Visualização:** Plotly Graph Objects
* **Relatórios:** FPDF2
* **Validação & Testes:** Pytest

---

## 📁 Estrutura do Repositório

```text
├── src/
│   └── physics.py         # Módulo isolado de auditoria termodinâmica
├── tests/
│   └── test_physics.py    # Testes unitários automatizados (pytest)
├── scripts/
│   └── ingestion.py       # Pipeline de indexação vetorial em batches
├── app.py                 # Interface Streamlit e orquestrador RAG
├── requirements.txt       # Dependências do projeto
└── .gitignore             # Arquivos ignorados pelo controle de versão
