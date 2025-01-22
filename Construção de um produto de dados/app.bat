@echo off
:: Criação do ambiente Conda
call conda create --name streamlit_env python -y

:: Ativação do ambiente Conda
call conda activate streamlit_env

:: Instalação das dependências
call pip install pandas numpy seaborn matplotlib scikit-learn streamlit

:: Executar o aplicativo Streamlit
call streamlit run app.py
