"""
Módulo de Auditoria Termodinâmica e Validação Física Pré-RAG.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ResultadoAuditoriaTermica:
    t_hot_in: float
    t_hot_out: Optional[float]
    t_cold_out: Optional[float]
    delta_t_q: Optional[float]
    heat_load_kw: float
    lmtd_k: float
    anomalias: List[str]
    fisicamente_valido: bool


def extrair_temperaturas_saida(doc_text: str):
    """Extrai com segurança as temperaturas dos fluxos de saída do texto."""
    t_hot_out = None
    t_cold_out = None
    try:
        if "Temperatura de saída quente:" in doc_text:
            p_sq = doc_text.split("Temperatura de saída quente:")[1].split("K.")[0].strip()
            t_hot_out = float(p_sq)
        if "Temperatura de saída fria:" in doc_text:
            p_sf = doc_text.split("Temperatura de saída fria:")[1].split("K.")[0].strip()
            t_cold_out = float(p_sf)
    except (ValueError, IndexError):
        pass
    return t_hot_out, t_cold_out


def validar_registro_termodinamico(meta: dict, doc_text: str) -> ResultadoAuditoriaTermica:
    """
    Aplica validação determinística da 2ª Lei da Termodinâmica
    e calcula o gradiente térmico da fonte quente.
    """
    t_hot_in = float(meta.get("hot_inlet_k", 0.0))
    heat_load = float(meta.get("heat_load_kw", 0.0))
    lmtd = float(meta.get("lmtd_k", 0.0))

    t_hot_out, t_cold_out = extrair_temperaturas_saida(doc_text)
    anomalias = []

    # Verificação física: a saída fria não pode ultrapassar a entrada quente
    if t_cold_out is not None and t_hot_in > 0 and (t_cold_out > t_hot_in):
        anomalias.append(
            f"Anomalia de Telemetria: T_saída fria ({t_cold_out:.1f} K) excede T_entrada quente ({t_hot_in:.1f} K)."
        )

    delta_t_q = (t_hot_in - t_hot_out) if (t_hot_in and t_hot_out is not None) else None

    return ResultadoAuditoriaTermica(
        t_hot_in=t_hot_in,
        t_hot_out=t_hot_out,
        t_cold_out=t_cold_out,
        delta_t_q=delta_t_q,
        heat_load_kw=heat_load,
        lmtd_k=lmtd,
        anomalias=anomalias,
        fisicamente_valido=(len(anomalias) == 0)
    )