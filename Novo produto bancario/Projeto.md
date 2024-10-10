# Novo produto bancario (linguagem R)

# CONTEXTO

Uma instituição financeira busca melhorar sua estratégia de marketing para o novo produto de empréstimo da empresa. O objetivo é construir um modelo que possa prever com precisão se um cliente irá subscrever ("sim") ou não ("não") ao novo produto de depósito a prazo.

No entanto, um dos desafios a serem superados é a complexidade inerente dos dados. Devido às relações não lineares e à diversidade de tipos de variáveis no conjunto de dados (tanto categóricas quanto numéricas), um modelo simples pode não ter um bom desempenho. O Random Forest é um método de aprendizado de conjunto que pode capturar interações complexas e lidar com diferentes tipos de dados.


# DESAFIO

Desenvolver um modelo de Classificação que utiliza Floresta Aleatória (Random Forest Classifier) usando o conjunto de dados fornecido. A avaliação de performance será dada pela acurácia do modelo seguindo a formula:

Acc=(TP+TN)/(TP+TN+FP+FN)

Onde: Acc é a acurácia do modelo; TP é os casos em que o modelo previu a classe positiva corretamente; TN é os casos em que o modelo previu a classe negativa corretamente; FP é os casos em que o modelo previu a classe positiva incorretamente; FN é os casos em que o modelo previu a classe negativa incorretamente.

Algumas restrições devem ser impostas no modelo:
	O numero de arvores da floresta deve ser entre 200 e 400
 
	A profundidade de cada arvore não pode ultrapassar 20 nós
