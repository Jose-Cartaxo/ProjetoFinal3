import gmaps
import gmaps.datasets

# Configure a chave da API do Google Maps
gmaps.configure(api_key='AIzaSyB_brs6KxO_ZbAzviY4L2pzlE1wgY0VaQg')

# Defina as coordenadas dos pontos
latitude = [37.774929, 34.052235, 40.712776, 38.889931, 41.878876]  # Exemplo de latitude dos pontos
longitude = [-122.419416, -118.243683, -74.005974, -77.009003, -87.635915]  # Exemplo de longitude dos pontos

# Crie uma camada de marcadores com as coordenadas dos pontos
fig = gmaps.figure()
camada_marcadores = gmaps.marker_layer(list(zip(latitude, longitude)))
fig.add_layer(camada_marcadores)

# Exiba o mapa
fig.open()
