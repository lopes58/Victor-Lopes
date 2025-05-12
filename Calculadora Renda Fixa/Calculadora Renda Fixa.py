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

    serie_cdi = sgs.get(CODIGO_CDI, start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'), end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))
    serie_ipca = sgs.get(CODIGO_IPCA, start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'), end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))

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

def converter_taxas(tx_input, idx_input, usar_projecao=False, ano_projecao=None):
    if usar_projecao:
        if ano_projecao is None:
            raise ValueError("Ano de projeção não especificado.")
        ipca_proj, selic_proj = obter_projecao_ano(ano_projecao)
        if ipca_proj is None or selic_proj is None:
            raise ValueError("Projeções não disponíveis para o ano especificado.")
        ipca_acumulado = ipca_proj / 100
        cdi_acumulado = (selic_proj - 0.10) / 100  # Aproximação do CDI a partir da Selic
    else:
        cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()

    txPREequiv = None

    if idx_input == "PRE":
        txPREequiv = tx_input
    elif idx_input == "%CDI":
        txPREequiv = (((1 + cdi_acumulado) ** (1 / 252) - 1) * tx_input + 1) ** 252 - 1
    elif idx_input == "DI+":
        txPREequiv = (1 + cdi_acumulado) * (1 + tx_input) - 1
    elif idx_input == "IPCA+":
        txPREequiv = (1 + ipca_acumulado) * (1 + tx_input) - 1
    else:
        raise ValueError("Erro idxInput não identificado")

    taxas_convertidas = {
        "PRE": txPREequiv,
        "%CDI": ((1 + txPREequiv) ** (1 / 252) - 1) / ((1 + cdi_acumulado) ** (1 / 252) - 1),
        "DI+": (1 + txPREequiv) / (1 + cdi_acumulado) - 1,
        "IPCA+": (1 + txPREequiv) / (1 + ipca_acumulado) - 1
    }

    return taxas_convertidas

def exibir_taxas(usar_projecao=False, ano_projecao=None):
    if usar_projecao:
        if ano_projecao is None:
            raise ValueError("Ano de projeção não especificado.")
        ipca_proj, selic_proj = obter_projecao_ano(ano_projecao)
        if ipca_proj is None or selic_proj is None:
            print("Projeções não disponíveis para o ano especificado.")
            return
        cdi_proj = selic_proj - 0.10  # Aproximação do CDI a partir da Selic
        print(f"Projeções para o ano {ano_projecao}:")
        print(f"IPCA: {ipca_proj:.4f}%")
        print(f"Selic: {selic_proj:.4f}%")
        print(f"CDI (aproximado): {cdi_proj:.4f}%")
    else:
        cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()
        print(f"Taxas acumuladas nos últimos 12 meses:")
        print(f"CDI: {cdi_acumulado:.4%}")
        print(f"IPCA: {ipca_acumulado:.4%}")

# Exemplo de uso
usar_projecao = True  # Defina como True para usar as projeções ou False para usar os dados históricos
ano_projecao = 2026   # Especifique o ano desejado para a projeção

exibir_taxas(usar_projecao, ano_projecao)

# Entrada: 110% do CDI
tx_input = 1.10
idx_input = "%CDI"
taxas = converter_taxas(tx_input, idx_input, usar_projecao, ano_projecao)
print(f"\nTaxas convertidas a partir de {tx_input:.2%} do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")

# Entrada: 1% acima do CDI
tx_input = 0.001138
idx_input = "DI+"
taxas = converter_taxas(tx_input, idx_input, usar_projecao, ano_projecao)
print(f"\nTaxas convertidas a partir de {tx_input:.4%} do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")

# Entrada: 6% acima do IPCA
tx_input = 0.0764
idx_input = "IPCA+"
taxas = converter_taxas(tx_input, idx_input, usar_projecao, ano_projecao)
print(f"\nTaxas convertidas a partir de {tx_input:.2%} do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")
