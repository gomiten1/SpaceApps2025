#Este archivo se utiliza para elegir el modelo
#Uso LazyPredict para comparar varios modelos de regresión
#y seleccionar el mejor según el performance
from lazypredict.Supervised import LazyRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

#Cargar datos
path = 'dataset_etiquetado.csv'
df = pd.read_csv(path)
quitar_columnas = ['habitatId','calificacionExperto','scoreMasa','scoreSostenibilidad','scoreProteccionRadiacion','scoreChecklist','scoreVolumenPorPersona']
X = df.drop(quitar_columnas, axis=1)

y = df['calificacionExperto']
#Normalizamos y, la mejor puntuación vale 1 y la peor puntuación vale 0
y = (y - y.min()) / (y.max() - y.min())

#Dividir datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

#Comparar modelos
reg = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None)
models, predictions = reg.fit(X_train, X_test, y_train, y_test)

#Mostrar resultados
print(models)

