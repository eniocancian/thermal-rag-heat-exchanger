import pytest
from src.physics import validar_registro_termodinamico


def test_cenario_operacional_fisicamente_valido():
    """Valida um registro com temperaturas consistentes (dentro da 2ª Lei)."""
    meta = {
        "hot_inlet_k": 450.0,
        "heat_load_kw": 110.0,
        "lmtd_k": 85.0
    }
    doc = "Temperatura de saída quente: 380.0 K. Temperatura de saída fria: 320.0 K."
    
    resultado = validar_registro_termodinamico(meta, doc)
    
    assert resultado.fisicamente_valido is True
    assert len(resultado.anomalias) == 0
    assert resultado.delta_t_q == pytest.approx(70.0, rel=1e-3)


def test_cenario_anomalia_segunda_lei():
    """Valida a detecção de telemetria defeituosa (T_saída fria > T_entrada quente)."""
    meta = {
        "hot_inlet_k": 510.52,
        "heat_load_kw": 120.62,
        "lmtd_k": 120.62
    }
    # T_cold_out marcando 2011.51 K (falha típica de sensor/overflow)
    doc = "Temperatura de saída quente: 364.5 K. Temperatura de saída fria: 2011.51 K."
    
    resultado = validar_registro_termodinamico(meta, doc)
    
    assert resultado.fisicamente_valido is False
    assert len(resultado.anomalias) == 1
    assert "excede T_entrada quente" in resultado.anomalias[0]


def test_calculo_gradiente_termico_lado_quente():
    """Garante cálculo exato do gradiente térmico Delta T."""
    meta = {"hot_inlet_k": 500.0, "heat_load_kw": 90.0, "lmtd_k": 60.0}
    doc = "Temperatura de saída quente: 350.0 K. Temperatura de saída fria: 310.0 K."
    
    resultado = validar_registro_termodinamico(meta, doc)
    assert resultado.delta_t_q == pytest.approx(150.0)