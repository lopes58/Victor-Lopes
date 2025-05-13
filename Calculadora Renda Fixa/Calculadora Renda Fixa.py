from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import holidays
from bcb import sgs, Expectativas

def ultimo_dia_util_mes_anterior(data_referencia):
    feriados = holidays.Brazil(years=[data_referencia.year, data_referencia.year - 1])
    primeiro_dia_mes_atual = data_referencia.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
    while ultimo_dia_mes_anterior.weekday() >= 5 or ultimo_dia_mes_anterior in feriados:
        ultimo_dia_mes_anterior -= timedelta(days=1)
    return ultimo_dia_mes_anterior


def obter_taxas_acumuladas_12_meses():
    CODIGO_CDI = 12
    CODIGO_IPCA = 433
    data_atual = date.today()
    ultimo_dia_mes_anterior = ultimo_dia_util_mes_anterior(data_atual)

    primeiro_dia_12_meses_atras = ultimo_dia_mes_anterior - relativedelta(months=12) + timedelta(days=1)

    serie_cdi = sgs.get(CODIGO_CDI,
                        start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'),
                        end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))
    serie_ipca = sgs.get(CODIGO_IPCA,
                         start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'),
                         end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))

    if serie_cdi.empty or serie_ipca.empty:
        raise ValueError("Dados não disponíveis para o período especificado.")

    cdi_acumulado = (1 + serie_cdi.iloc[:, 0] / 100).prod() - 1
    ipca_acumulado = (1 + serie_ipca.iloc[:, 0] / 100).prod() - 1

    return cdi_acumulado, ipca_acumulado


def obter_projecao_ano(ano_referencia):
    expec = Expectativas()
    ep = expec.get_endpoint('ExpectativasMercadoAnuais')

    def obter_mediana(indicador):
        df = (
            ep.query()
            .filter(ep.Indicador == indicador, ep.DataReferencia == ano_referencia)
            .collect()
        )
        if not df.empty:
            df = df.sort_values('Data', ascending=False)
            return df.iloc[0]['Mediana']
        else:
            return None

    mediana_ipca = obter_mediana('IPCA')
    mediana_selic = obter_mediana('Selic')

    return mediana_ipca, mediana_selic


def converter_taxas(tx_input, idx_input, usar_projecao=False, ano_projecao=None, usar_cdb=True):
    """
    Converte taxas de diferentes indexadores para equivalentes PRE, %CDI, DI+, IPCA+ e calcula o rendimento pré-fixado anual considerando CDB ou LCI/LCA.

    Parâmetros:
    - tx_input (float): taxa informada (ex: 1.10 para 110% CDI, 0.0764 para IPCA+ 6,14%).
    - idx_input (str): tipo de indexador ('PRE', '%CDI', 'DI+', 'IPCA+').
    - usar_projecao (bool): se True, usa projeções anuais; caso contrário, usa dados históricos de 12 meses.
    - ano_projecao (int): ano para projeção (se usar_projecao=True).
    - usar_cdb (bool): True para CDB (IR de 15% em 2 anos), False para LCI/LCA (isenção de IR).

    Retorna:
    - dicionário com taxas convertidas e rendimento pré-fixado anual.
    """
    # Obter CDI e IPCA acumulados
    if usar_projecao:
        if ano_projecao is None:
            raise ValueError("Ano de projeção não especificado.")
        ipca_proj, selic_proj = obter_projecao_ano(ano_projecao)
        if ipca_proj is None or selic_proj is None:
            raise ValueError("Projeções não disponíveis para o ano especificado.")
        ipca_acumulado = ipca_proj / 100
        cdi_acumulado = (selic_proj - 0.10) / 100
    else:
        cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()

    # Conversão para taxa pré-fixada acumulada em 2 anos
    if idx_input == "PRE":
        txPREequiv = tx_input
    elif idx_input == "%CDI":
        txPREequiv = (((1 + cdi_acumulado) ** (1 / 252) - 1) * tx_input + 1) ** 252 - 1
    elif idx_input == "DI+":
        txPREequiv = (1 + cdi_acumulado) * (1 + tx_input) - 1
    elif idx_input == "IPCA+":
        txPREequiv = (1 + ipca_acumulado) * (1 + tx_input) - 1
    else:
        raise ValueError("idx_input não identificado")

    # Ajuste de IR para CDB ou LCI/LCA
    ir_rate = 0.15 if usar_cdb else 0.0
    tx_liquida_2anos = txPREequiv * (1 - ir_rate)

    # Rendimento pré-fixado anual equivalente em 2 anos
    rendimento_pref_annual = (1 + tx_liquida_2anos) ** (1 / 2) - 1

    taxas_convertidas = {
        "PRE_acumulado": txPREequiv,
        "PRE_liquido": tx_liquida_2anos,
        "%CDI": ((1 + txPREequiv) ** (1 / 252) - 1) / ((1 + cdi_acumulado) ** (1 / 252) - 1),
        "DI+": (1 + txPREequiv) / (1 + cdi_acumulado) - 1,
        "IPCA+": (1 + txPREequiv) / (1 + ipca_acumulado) - 1,
    }

    return taxas_convertidas


def exibir_taxas(usar_projecao=False, ano_projecao=None, usar_cdb=True):
    """
    Exibe no console as taxas CDI/IPCA históricas ou projetadas e compara CDB vs LCI/LCA.
    """
    # Mostrar CDI/IPCA
    if usar_projecao:
        if ano_projecao is None:
            raise ValueError("Ano de projeção não especificado.")
        ipca_proj, selic_proj = obter_projecao_ano(ano_projecao)
        if ipca_proj is None or selic_proj is None:
            print("Projeções não disponíveis para o ano especificado.")
            return
        cdi_proj = selic_proj - 0.10
        print(f"Projeções para o ano {ano_projecao}:")
        print(f"IPCA: {ipca_proj:.4f}%")
        print(f"Selic: {selic_proj:.4f}%")
        print(f"CDI (aproximado): {cdi_proj:.4f}%")
    else:
        cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()
        print("Taxas acumuladas nos últimos 12 meses:")
        print(f"CDI: {cdi_acumulado:.4%}")
        print(f"IPCA: {ipca_acumulado:.4%}")

    tipo = "CDB (15% IR, 2 anos)" if usar_cdb else "LCI/LCA (isentos de IR)"
    print(f"\nComparando para: {tipo}\n")

# Exemplo de uso
usar_projecao = True  # True para usar projeções, False para histórico
ano_projecao = 2026    # Ano para projeção
usar_cdb = True        # True para CDB, False para LCI/LCA

# Exibir taxas básicas
exibir_taxas(usar_projecao, ano_projecao, usar_cdb)

# Teste das conversões
entradas = [
    (0.1486, "PRE"),    # PRE
    (1.08, "%CDI"),    # 110% CDI
    (0.007, "DI+"),  # 0,1138% acima do CDI
    (0.0875, "IPCA+"),  # 7,64% acima do IPCA
]

for tx_input, idx_input in entradas:
    taxas = converter_taxas(tx_input, idx_input, usar_projecao, ano_projecao, usar_cdb)
    print(f"Resultados para {tx_input:.4%} de {idx_input}:")
    for nome, valor in taxas.items():
        print(f"{nome}: {valor:.4%}")
    print()

# Exemplo de uso
usar_projecao = True  # True para usar projeções, False para histórico
ano_projecao = 2026    # Ano para projeção
usar_cdb = False        # True para CDB, False para LCI/LCA

# Exibir taxas básicas
exibir_taxas(usar_projecao, ano_projecao, usar_cdb)

# Teste das conversões
entradas = [
    (0.9175, "%CDI"),
    (0.0663, "IPCA+")
]
for tx_input, idx_input in entradas:
    taxas = converter_taxas(tx_input, idx_input, usar_projecao, ano_projecao, usar_cdb)
    print(f"Resultados para {tx_input:.4%} de {idx_input}:")
    for nome, valor in taxas.items():
        print(f"{nome}: {valor:.4%}")
    print()
