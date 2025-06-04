# Diagnóstico de Padrões Ocultos em Séries Temporais com Deep Learning (Python)

# Cenário
O objetivo é explorar, treinar e validar um modelo de Deep Learning RNN (Recurrent Neural Network) capaz de identificar e classificar as séries em questão em três grupos distintos, refletindo diferentes padrões de comportamento de mercado.

Os dados intradiários de variação de preços do ativo sintético XYZ estão contidos no arquivo precos_forum.csv, um dataframe cujas colunas representam os dias (a partir de 01/01/2016) e cujas linhas correspondem aos preços do ativo minuto a minuto, iniciando às 9:00:00 de cada dia. As séries foram normalizadas para iniciar todo dia com preço 1.
