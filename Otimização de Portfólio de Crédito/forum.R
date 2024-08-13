## ----- Bibliotecas do R
library(readxl)
library(lpSolve)

## Base de dados
input='../data/PortfolioCredito.v0.2.xlsm'

## -- Carga dos dados
## Leitura dos insumos
data=read_excel(path=input)

# Conversao para taxas pre
for(i in 1:nrow(data)){
  if (data[i,'Index'] == 'DI+'){
    data[i,'IndexPre'] = (1+data[i,'CurvaMercado'])*(1+data[i,'ValorIndex'])-1
  } else if (data[i,'Index'] == '%CDI'){
    data[i,'IndexPre'] = (((1+data[i,'CurvaMercado'])^(1/252)-1)*data[i,'ValorIndex']+1)^252-1
  } else {
    data[i,'IndexPre'] = data[i,'ValorIndex']
  }
}

## Direction
direction = "max"

## funcao objetivo
objective.in = data[['IndexPre']]

# Restricoes
r1 = rep(1,9)
r2 = c(0,0,1,0,1,0,1,0,0)
r3 = c(0,0,0,0,0,1,0,1,1)
r4 = c(0,0,1,0,0,0,0,1,1)
r5 = c(0,1,0,1,1,0,0,0,0)
r6 = c(1,0,0,0,0,0,0,0,0)
r7 = c(0,1,0,0,0,0,0,0,0)
r8 = c(0,0,1,0,0,0,0,0,0)
r9 = c(0,0,0,1,0,0,0,0,0)
r10 = c(0,0,0,0,1,0,0,0,0)
r11 = c(0,0,0,0,0,1,0,0,0)
r12 = c(0,0,0,0,0,0,1,0,0)
r13 = c(0,0,0,0,0,0,0,1,0)
r14 = c(0,0,0,0,0,0,0,0,1)
r15 = c(1,0,0,0,0,0,0,0,0)
r16 = c(0,1,0,0,0,0,0,0,0)
r17 = c(0,0,1,0,0,0,0,0,0)
r18 = c(0,0,0,1,0,0,0,0,0)
r19 = c(0,0,0,0,1,0,0,0,0)
r20 = c(0,0,0,0,0,1,0,0,0)
r21 = c(0,0,0,0,0,0,1,0,0)
r22 = c(0,0,0,0,0,0,0,1,0)
r23 = c(0,0,0,0,0,0,0,0,1)

## Matriz de restrições
const.mat = rbind(r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16,r17,r18,r19,r20,r21,r22,r23)

## Direção das restrições
const.dir = c("=", ">=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", "<=", ">=", ">=", ">=", ">=", ">=", ">=", ">=", ">=", ">=")

## Constantes
const.rhs = c(1, 0.3, 0.3, 0.4, 0.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.2, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0)

optim = lp(
  direction = direction,
  objective.in = objective.in,
  const.mat = const.mat,
  const.dir = const.dir,
  const.rhs = const.rhs,
  compute.sens = TRUE
)

## valor das variáveis
optim$solution

## valor do objetivo
optim$objval

# Validacao
for(i in 1:nrow(const.mat)){
  # cat(sprintf('Restricao: %s %f\n',rownames(const.mat)[i],sum(const.mat[i,]*optim$solution)))
  if(abs(sum(const.mat[i,]*optim$solution)-const.rhs[i])<=0.01){
    cat(sprintf('Restricao ativa: %s\n',rownames(const.mat)[i]))
  }
}