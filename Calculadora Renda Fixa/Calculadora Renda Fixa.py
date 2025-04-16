from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import holidays
from bcb import sgs

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

    # Calcula o primeiro dia útil de 12 meses atrás
    primeiro_dia_12_meses_atras = ultimo_dia_util_mes_anterior(ultimo_dia_mes_anterior - relativedelta(months=10)).replace(day=1)

    # Obtém as séries temporais para o período de 12 meses
    serie_cdi = sgs.get(CODIGO_CDI, start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'), end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))
    serie_ipca = sgs.get(CODIGO_IPCA, start=primeiro_dia_12_meses_atras.strftime('%Y-%m-%d'), end=ultimo_dia_mes_anterior.strftime('%Y-%m-%d'))

    if serie_cdi.empty or serie_ipca.empty:
        raise ValueError("Dados não disponíveis para o período especificado.")

    cdi_acumulado = (1 + serie_cdi.iloc[:, 0] / 100).prod() - 1
    ipca_acumulado = (1 + serie_ipca.iloc[:, 0] / 100).prod() - 1

    return cdi_acumulado, ipca_acumulado

def converter_taxas(tx_input, idx_input):
    cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()
    txPREequiv = None

    # X => PRE
    if idx_input == "PRE":
        txPREequiv = tx_input
    elif idx_input == "%CDI":
        txPREequiv = (((1 + cdi_acumulado) ** (1 / 252) - 1) * tx_input + 1) ** 252 - 1
    elif idx_input == "DI+":
        txPREequiv = (1 + cdi_acumulado) * (1 + tx_input) - 1
    elif idx_input == "IPCA+":
        txPREequiv = (1 + ipca_acumulado) * (1 + tx_input) - 1
    else:
        raise ValueError("Erro idxInput nao identificado")

    # PRE => Y
    taxas_convertidas = {
        "PRE": txPREequiv,
        "%CDI": ((1 + txPREequiv) ** (1 / 252) - 1) / ((1 + cdi_acumulado) ** (1 / 252) - 1),
        "DI+": (1 + txPREequiv) / (1 + cdi_acumulado) - 1,
        "IPCA+": (1 + txPREequiv) / (1 + ipca_acumulado) - 1
    }

    return taxas_convertidas

# Exemplos de uso
cdi_acumulado, ipca_acumulado = obter_taxas_acumuladas_12_meses()
print(f"CDI Acumulado (12 Meses): {cdi_acumulado:.4%}")
print(f"IPCA Acumulado (12 Meses): {ipca_acumulado:.4%}")

# Entrada: 110% do CDI
tx_input = 1.10
idx_input = "%CDI"
taxas = converter_taxas(tx_input, idx_input)
print(f"\nTaxas convertidas a partir de {tx_input:.2%} do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")

# Entrada: 1% acima do CDI
tx_input = 0.0075
idx_input = "DI+"
taxas = converter_taxas(tx_input, idx_input)
print(f"\nTaxas convertidas a partir de {tx_input:.2%} acima do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")

# Entrada: 6% acima do IPCA
tx_input = 0.0885
idx_input = "IPCA+"
taxas = converter_taxas(tx_input, idx_input)
print(f"\nTaxas convertidas a partir de {tx_input:.2%} acima do {idx_input}:")
for idx, tx in taxas.items():
    print(f"{idx}: {tx:.4%}")