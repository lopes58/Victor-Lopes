# 1. Carregar pacotes necessários
library(caret)
library(neuralnet)
library(dplyr)
library(ggplot2)
library(pROC)

# 2. Carregar e preparar dados
url <- "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data"
dados <- read.table(url, header = FALSE, sep = " ", stringsAsFactors = FALSE)

# 3. Pré-processamento completo
colnames(dados) <- c(
  "Status_conta", "Duracao_meses", "Hist_credito", "Proposito",
  "Credito", "Poupancas", "Tempo_emprego", "Taxa_pagamento",
  "Estado_civil", "Garantia", "Tempo_residencia", "Bens",
  "Idade", "Outros_planos", "Moradia", "Creditos_externos",
  "Trabalho", "Pessoas_mnt", "Telefone", "Estrangeiro", "Classe"
)

# Converter variável alvo para binária (0 = Inadimplente, 1 = Bom)
dados$Classe <- ifelse(dados$Classe == 1, 1, 0)

# Converter variáveis categóricas para numéricas
dados <- dados %>%
  mutate(across(-Classe, ~ as.numeric(factor(.x))))

# Normalização Min-Max
preproc <- preProcess(dados, method = "range")
dados_norm <- predict(preproc, dados)

# 4. Divisão treino-teste
set.seed(1)
trainIndex <- createDataPartition(dados_norm$Classe, p = 0.7, list = FALSE)
treino <- dados_norm[trainIndex, ]
teste <- dados_norm[-trainIndex, ]

# -------------------------------------------
# (a) Modelo Básico: 5 neurônios + ativação logística
# -------------------------------------------
modelo_basico <- neuralnet(
  Classe ~ .,
  data = treino,
  hidden = 5,
  act.fct = "logistic",
  linear.output = FALSE,
  threshold = 0.1
)

# Converter respostas para fatores
teste$Classe <- factor(
  ifelse(teste$Classe == 1, "Bom", "Inadimplente"),
  levels = c("Inadimplente", "Bom")
)

# Predições e matriz de confusão
pred_prob_basico <- as.numeric(compute(modelo_basico, teste[, -ncol(teste)])$net.result)
pred_class_basico <- factor(
  ifelse(pred_prob_basico > 0.5, "Bom", "Inadimplente"),
  levels = c("Inadimplente", "Bom")
)

conf_matrix_basico <- confusionMatrix(pred_class_basico, teste$Classe, positive = "Bom")
print("Matriz de Confusão (Modelo Básico):")
print(conf_matrix_basico)

# -------------------------------------------
# (b)-(d) Tuning de Hiperparâmetros
# -------------------------------------------

# Definir grid de hiperparâmetros
param_grid <- expand.grid(
  hidden = I(list(3, 5, 7, c(5,3), c(7,5))),  # Arquiteturas
  act.fct = c("logistic", "tanh"),            # Funções de ativação
  threshold = c(0.01, 0.05, 0.1),             # Limiares de erro
  stringsAsFactors = FALSE
)

# Configurar validação cruzada (5 folds)
folds <- createFolds(treino$Classe, k = 5)
results <- data.frame()

# Loop de treinamento
for(i in 1:nrow(param_grid)) {
  cat("\nTestando combinação", i, "/", nrow(param_grid), "\n")
  hidden <- param_grid$hidden[[i]]
  act <- param_grid$act.fct[i]
  thr <- param_grid$threshold[i]
  
  aucs <- numeric(5)
  accs <- numeric(5)
  
  for (j in seq_along(folds)) {
    validIdx <- folds[[j]]
    trainData <- treino[-validIdx, ]
    validData <- treino[validIdx, ]
    
    model <- neuralnet(
      Classe ~ .,
      data = trainData,
      hidden = hidden,
      act.fct = act,
      linear.output = FALSE,
      threshold = thr
    )
    
    prob <- as.numeric(compute(model, validData[, -ncol(validData)])$net.result)
    pred <- factor(ifelse(prob > 0.5, "Bom", "Inadimplente"),
                   levels = c("Inadimplente", "Bom"))
    
    aucs[j] <- auc(roc(validData$Classe, prob))
    accs[j] <- mean(pred == validData$Classe)
  }
  
  results <- rbind(results, data.frame(
    hidden = paste(hidden, collapse = "-"),
    act.fct = act,
    threshold = thr,
    AUC = mean(aucs),
    Acc = mean(accs)
  ))
}

# -------------------------------------------
# (e) Comparação dos Resultados
# -------------------------------------------
print("Resultados do Tuning:")
print(results[order(-results$AUC), ])

# -------------------------------------------
# (f) Melhor Modelo + Avaliação Final
# -------------------------------------------
best <- results[which.max(results$AUC), ]

# Treinar modelo final com todos os dados de treino
modelo_final <- neuralnet(
  Classe ~ .,
  data = treino,
  hidden = as.numeric(strsplit(best$hidden, "-")[[1]]),
  act.fct = best$act.fct,
  linear.output = FALSE,
  threshold = best$threshold
)

# Plotar arquitetura da rede
plot(modelo_final, main = "Arquitetura da Rede Neural")

# Avaliação no conjunto de teste
pred_prob_final <- as.numeric(compute(modelo_final, teste[, -ncol(teste)])$net.result)
pred_class_final <- factor(
  ifelse(pred_prob_final > 0.5, "Bom", "Inadimplente"),
  levels = c("Inadimplente", "Bom")
)

# Matriz de confusão
conf_matrix_final <- confusionMatrix(pred_class_final, teste$Classe, positive = "Bom")
print("Matriz de Confusão (Modelo Final):")
print(conf_matrix_final)

# Curva ROC e AUC
roc_final <- roc(response = teste$Classe, predictor = pred_prob_final)
plot(roc_final, main = "Curva ROC - Modelo Final")
cat("\nAUC do Modelo Final:", auc(roc_final), "\n")