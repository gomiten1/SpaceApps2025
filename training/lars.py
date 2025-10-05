from sklearn.linear_model import Lars
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import pandas as pd
import joblib


def cargarModeloLars(path='modelo_lars.pkl'):
    """
    Función opcional para cargar modelo ya entrenado
    """
    return joblib.load(path)

# Cargar datos
path = 'dataset_etiquetado.csv'
df = pd.read_csv(path)

# Columnas a quitar de las features
quitar_columnas = [
    'habitatId',
    'calificacionExperto',
    'scoreMasa',
    'scoreSostenibilidad',
    'scoreProteccionRadiacion',
    'scoreChecklist',
    'scoreVolumenPorPersona'
]

# Definir X e y
X = df.drop(quitar_columnas, axis=1)
y = df['calificacionExperto']

# Separar en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Crear y entrenar el modelo LARS
lars_model = Lars(n_nonzero_coefs=7)
lars_model.fit(X_train, y_train)

# Predecir en el set de prueba
predictions = lars_model.predict(X_test)

# Evaluar el rendimiento del modelo
r2 = r2_score(y_test, predictions)
mse = mean_squared_error(y_test, predictions)

print(f"Puntuación R-cuadrado: {r2:.4f}")
print(f"Error cuadrático medio: {mse:.4f}")

# Mostrar las características seleccionadas
selected_features = X.columns[lars_model.coef_ != 0]
print("Características seleccionadas por LARS:", list(selected_features))

# Guardar el modelo entrenado en un archivo
joblib.dump(lars_model, 'modelo_lars.pkl')
print("Modelo guardado en 'modelo_lars.pkl'")