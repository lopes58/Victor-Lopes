import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Previsão de Cancelamento de Clientes", layout="wide")

# Título e introdução do aplicativo
st.title("Previsão de Subscrição ao Produto de Depósito a Prazo")
st.write(
    """
    A instituição financeira **FGVPython** busca melhorar sua estratégia de marketing para o novo produto de empréstimo da empresa. 
    O objetivo é prever com precisão se um cliente irá subscrever ("sim") ou não ("não") ao novo produto de depósito a prazo.

    Devido às relações não lineares e à diversidade de tipos de variáveis no conjunto de dados (tanto categóricas quanto numéricas), 
    um modelo simples pode não ter um bom desempenho. Portanto, utilizou-se o **Random Forest**, um método de aprendizado de conjunto 
    que pode capturar interações complexas e lidar com diferentes tipos de dados.

    O conjunto de dados contém uma coleção de variáveis que descrevem os clientes e fatores externos. 
    Abaixo está uma visão geral das principais variáveis disponíveis:

    | Campo           | Descrição                                                                 |
    |------------------|--------------------------------------------------------------------------|
    | **age**          | Idade do cliente.                                                       |
    | **job**          | Tipo de emprego do cliente (ex: administrativo, operário, empreendedor). |
    | **marital**      | Estado civil (ex: casado, solteiro, divorciado).                         |
    | **education**    | Nível de educação (ex: básico, ensino médio, ensino superior).           |
    | **default**      | Se o cliente tem crédito em inadimplência (sim ou não).                  |
    | **housing**      | Se o cliente tem empréstimo habitacional (sim ou não).                   |
    | **loan**         | Se o cliente tem empréstimo pessoal (sim ou não).                        |
    | **contact**      | Tipo de contato de comunicação (ex: celular, telefone).                  |
    | **month**        | Mês do último contato do ano.                                            |
    | **day_of_week**  | Dia da semana do último contato.                                         |
    | **duration**     | Duração do último contato em segundos.                                   |
    | **campaign**     | Número de contatos realizados durante esta campanha.                     |
    | **previous**     | Número de contatos realizados antes desta campanha.                      |
    | **poutcome**     | Resultado da campanha de marketing anterior.                             |
    | **emp.var.rate** | Taxa de variação do emprego, um indicador líder da economia.             |
    | **cons.price.idx** | Índice de preços ao consumidor.                                        |
    | **cons.conf.idx** | Índice de confiança do consumidor.                                      |
    | **euribor3m**    | Taxa Euribor de 3 meses.                                                 |
    | **nr.employed**  | Número de empregados na empresa.                                         |
    | **y**            | Se o cliente subscreveu um depósito a prazo (sim ou não). (variável alvo)|
    """
)

# 1. Carregar dados
st.header("1. Carregar Dados")
uploaded_file = st.file_uploader("Faça o upload do arquivo de treinamento (CSV):", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Visualização inicial dos dados:")
    st.write(data.head())

    # 2. Análise Univariada
    st.header("2. Análise Univariada")
    st.write("Distribuição das variáveis no dataset:")
    selected_column = st.selectbox("Selecione uma variável para visualizar a distribuição:", data.columns)
    if data[selected_column].dtype in ['int64', 'float64']:
        fig, ax = plt.subplots()
        sns.histplot(data[selected_column], kde=True, ax=ax, bins=20)
        ax.set_title(f"Distribuição da variável {selected_column}")
        st.pyplot(fig)
    else:
        fig, ax = plt.subplots()
        sns.countplot(x=selected_column, data=data, ax=ax)
        ax.set_title(f"Distribuição da variável {selected_column}")
        st.pyplot(fig)

    # Preprocessamento
    st.header("3. Preprocessamento")
    st.write("Codificação de variáveis categóricas e substituição de valores 'yes'/'no' por 1/0.")
    categorical_columns = [
        'job', 'marital', 'education', 'default', 'housing', 'loan',
        'contact', 'month', 'day_of_week', 'poutcome'
    ]
    label_encoders = {}
    for col in categorical_columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])
        label_encoders[col] = le

    data['y'] = data['y'].map({'yes': 1, 'no': 0})

    st.write("Dados após preprocessamento:")
    st.write(data.head())

    # 4. Análise Bivariada
    st.header("4. Análise Bivariada")
    st.write("Relação entre a variável resposta (`y`) e as variáveis preditoras.")
    selected_bivariate_col = st.selectbox("Selecione uma variável para análise bivariada:", data.columns[:-1])
    fig, ax = plt.subplots()
    sns.boxplot(x='y', y=selected_bivariate_col, data=data, ax=ax)
    ax.set_title(f"Relação entre `y` e {selected_bivariate_col}")
    st.pyplot(fig)

    # Divisão do dataset
    X = data.drop(columns=['y'])
    y = data['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # 5. Interatividade para configuração do modelo
    st.header("5. Treinamento do Modelo")
    st.write("Ajuste os parâmetros do modelo Random Forest:")
    n_estimators = st.slider("Número de árvores na floresta:", min_value=50, max_value=500, step=50, value=100)
    max_depth = st.slider("Profundidade máxima de cada árvore:", min_value=5, max_value=50, step=5, value=10)

    # Treinamento do modelo
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=1)
    model.fit(X_train, y_train)

    # Previsões
    y_pred = model.predict(X_test)

    # Avaliação do modelo
    st.header("6. Avaliação do Modelo")
    metric = st.selectbox("Selecione a métrica de avaliação:", ["Acurácia", "Precisão", "Recall", "F1-Score"])
    if metric == "Acurácia":
        score = accuracy_score(y_test, y_pred)
    elif metric == "Precisão":
        score = precision_score(y_test, y_pred)
    elif metric == "Recall":
        score = recall_score(y_test, y_pred)
    elif metric == "F1-Score":
        score = f1_score(y_test, y_pred)

    st.write(f"**{metric} do modelo na base de teste:** {score:.2f}")

    # Previsões com novos dados
    st.header("7. Previsão com Novos Dados")
    new_file = st.file_uploader("Faça o upload de um arquivo de novos dados (CSV):", type=["csv"])

    if new_file:
        new_data = pd.read_csv(new_file)
        st.write("Visualização dos novos dados:")
        st.write(new_data.head())

        # Preprocessamento dos novos dados
        for col in categorical_columns:
            if col in new_data.columns:
                le = label_encoders.get(col)
                if le:  # Garantir que o LabelEncoder existe para a coluna
                    new_data[col] = le.transform(new_data[col])

        # Seleção das mesmas colunas utilizadas no treinamento
        X_new = new_data[X.columns]

        # Realizar previsões
        new_predictions = model.predict(X_new)

        # Adicionar previsões como nova coluna na base
        new_data['Predicted_y'] = new_predictions
        st.write("Novos dados com previsões:")
        st.write(new_data.head())

        # Opção para download do arquivo com previsões
        csv = new_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Dados com Previsões",
            data=csv,
            file_name="New_BankData_with_predictions.csv",
            mime="text/csv"
        )
