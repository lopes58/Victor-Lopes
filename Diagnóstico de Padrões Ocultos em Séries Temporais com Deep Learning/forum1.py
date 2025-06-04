import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.optimizers import Adam

# 1. Carregamento e Pré-processamento de Dados
def load_data(path):
    df = pd.read_csv(path, index_col=0)
    # Transpor para shape (n_series, timesteps)
    return df.T.values

X = load_data("precos_forum.csv")
X_train, X_test = train_test_split(X, test_size=0.2, random_state=1)

# Normalização opcional (cada série já começa em 1)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Reshape para modelo RNN: (batch, timesteps, features)
timesteps = X_train_scaled.shape[1]
Xae_train = X_train_scaled.reshape(-1, timesteps, 1)
Xae_test = X_test_scaled.reshape(-1, timesteps, 1)

# 2. Construção de Autoencoder Sequencial via RNN (LSTM)
latent_dim = 50
input_seq = Input(shape=(timesteps, 1))
# Encoder LSTM
encoded = LSTM(latent_dim, activation='tanh')(input_seq)
# Vector latente repetido para decodificação
x = RepeatVector(timesteps)(encoded)
# Decoder LSTM retorna sequências completas
x = LSTM(latent_dim, activation='tanh', return_sequences=True)(x)
# Camada densa aplicada em cada timestep
decoded = TimeDistributed(Dense(1, activation='linear'))(x)

autoencoder = Model(input_seq, decoded)
encoder = Model(input_seq, encoded)

autoencoder.compile(optimizer=Adam(learning_rate=1e-3), loss='mse')

autoencoder.summary()

# 3. Treinamento do Autoencoder
history = autoencoder.fit(
    Xae_train, Xae_train,
    epochs=50,
    batch_size=15,
    validation_data=(Xae_test, Xae_test),
    verbose=2
)

# 4. Extração de Representação Latente
Z_train = encoder.predict(Xae_train)
Z_test = encoder.predict(Xae_test)

# 5. Clustering com KMeans
kmeans = KMeans(n_clusters=3, random_state=1)
labels_train = kmeans.fit_predict(Z_train)
labels_test = kmeans.predict(Z_test)

# 6. Avaliação de Métricas
sil_train = silhouette_score(Z_train, labels_train)
db_train = davies_bouldin_score(Z_train, labels_train)
print(f"Silhouette Score (train): {sil_train:.3f}")
print(f"Davies-Bouldin (train): {db_train:.3f}")

# 7. Visualização das Séries Médias por Cluster
mean_series = {c: X_train[labels_train == c].mean(axis=0) for c in range(3)}
plt.figure(figsize=(10,6))
for c, series in mean_series.items():
    plt.plot(series, label=f"Cluster {c}")
plt.title("Média Intradiária por Cluster")
plt.xlabel("Minuto do Dia")
plt.ylabel("Preço Normalizado")
plt.legend()
plt.show()

# 8. Robustez via Bootstrap
n_boot = 10
sil_scores = []
for i in range(n_boot):
    idx_boot = np.random.choice(len(Z_train), len(Z_train), replace=True)
    Zb = Z_train[idx_boot]
    labels_b = kmeans.fit_predict(Zb)
    sil_scores.append(silhouette_score(Zb, labels_b))
print(f"Silhouette bootstrap médio: {np.mean(sil_scores):.3f} ± {np.std(sil_scores):.3f}")
