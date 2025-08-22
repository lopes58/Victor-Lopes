## Construção de um produto de dados (Python)
# CONTEXTO
No CRISP-DM já se identificam diversos fatores que influenciam em um bom produto de dados, a começar pelo próprio problema, os dados disponíveis, as transformações realizadas, a modelagem construída, a avaliação desse modelo e finalmente a implantação. Uma forma popular de implantar um modelo é através de uma interface web, que muitas vezes é transformada em um app.
# DESAFIO
O objetivo deste projeto é a construção de um modelo de machine learning do início ao fim, com ênfase na etapa final, a implementação em uma interface web, explorando diversos recursos disponíveis.
# Requisitos de projeto:
•	Explicação do problema: A aplicação deve abordar um problema oferecendo uma solução baseada em aprendizado de máquina. Deve apresentar texto descritivo do problema em questão e da base de dados utilizada (ou do formato necessário da base para o uso da aplicação). Devem ser identificadas as variáveis e seus papéis na análise, identificando-se a variável resposta sempre que for necessário bem como variáveis preditoras.

•	Deve se utilizar de uma ou mais bases de dados disponíveis para o autor do projeto, públicas ou a que o autor tenha acesso.

•	Carga de dados: os dados devem ser carregados da internet (via API, download ou scrapping) ou de forma ativa pelo usuário utilizando os recursos da ferramenta.

•	Entendimento dos dados: Os dados devem estar suficientemente claros para o usuário. Se necessário for, deve haver uma descrição dos dados utilizados. A aplicação deve apresentar análise univariada mostrando a qualidade dos dados e característica da população.

•	Análise descritiva bivariada: Deve ser realizada análise descritiva descrevendo a relação da variável resposta com as variáveis utilizadas na modelagem desenvolvida.

•	Modelagem de aprendizado de máquina: Deve ser desenvolvido um modelo, o modelo deve ser descrito de acordo com sua natureza. Deve constar a avaliação de qualidade desse modelo.

•	A aplicação deve utilizar recursos interativos como inserção de dados e parâmetros pelo usuário como caixas de seleção, botões de deslizamento, inserção direta de dados numéricos ou em forma de texto, barras laterais, gráficos interativos ou abas que organizem as visualizações da aplicação.

•	Deve haver interação do usuário via insersão de parâmetros de análise como filtros, seleção de variáveis, visões, períodos, parâmetros de modelagem, janelas de médias móveis etc.

# Resumo da aplicação:

A instituição financeira FGVPython busca melhorar sua estratégia de marketing para o novo produto de empréstimo da empresa. O objetivo é prever com precisão se um cliente irá subscrever ("sim") ou não ("não") ao novo produto de depósito a prazo.

Devido às relações não lineares e à diversidade de tipos de variáveis no conjunto de dados (tanto categóricas quanto numéricas), um modelo simples pode não ter um bom desempenho. Portanto, utilizou-se o Random Forest, um método de aprendizado de conjunto que pode capturar interações complexas e lidar com diferentes tipos de dados.

# Execução da aplicação

Para executar a aplicação execute o arquivo app.bat, para criação do ambiente Conda e ativação, além da instalação das dependências.
