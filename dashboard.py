import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from plotly.colors import n_colors

# Annahme: Daten sind bereits geladen und bereinigt
data = pd.read_csv('house_prices_switzerland.csv')
data = data.dropna()
data = data.sort_values(by='Price', ascending=False)
data = data.iloc[5:]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Balkendiagramm: Durchschnittspreis nach Haustyp
avg_price_by_type = data.groupby('HouseType')['Price'].mean().reset_index()

# Sortieren des DataFrames nach 'Price' in absteigender Reihenfolge
avg_price_by_type = avg_price_by_type.sort_values(by='Price', ascending=False)

# Anzahl der einzigartigen Haustypen
num_house_types = avg_price_by_type['HouseType'].nunique()

# Erstellen einer Farbpalette mit unterschiedlichen Blautönen
colors = n_colors('rgb(0,0,139)', 'rgb(198,226,255)', num_house_types, colortype='rgb')

bar_fig = px.bar(
    avg_price_by_type,
    x='HouseType',
    y='Price',
    title='Durchschnittlicher Hauspreis nach Haustyp',
    labels={'Price': 'Durchschnittspreis (CHF)', 'HouseType': 'Haustyp'},
    color='HouseType',
    color_discrete_sequence=colors
)

# Aktualisieren der Achsenreihenfolge, um die Sortierung zu reflektieren
bar_fig.update_layout(xaxis={'categoryorder':'total descending'})

# Streudiagramm: Preis vs. Wohnfläche
scatter_fig = px.scatter(
    data,
    x='LivingSpace',
    y='Price',
    color='HouseType',
    hover_data=['Locality', 'PostalCode'],
    title='Preis vs. Wohnfläche',
    labels={'LivingSpace': 'Wohnfläche (qm)', 'Price': 'Preis (CHF)'}
)

# Karte: Teuerste Häuser
most_expensive = data.sort_values(by='Price', ascending=False).head(10)

# Dictionary mit Koordinaten der Ortschaften (wie zuvor definiert)
locality_coords = {
    'Grimentz': {'Latitude': 46.1806, 'Longitude': 7.5761},
    'Lugano': {'Latitude': 46.0037, 'Longitude': 8.9511},
    'Jouxtens-Mézery': {'Latitude': 46.5527, 'Longitude': 6.6007},
    'Pfeffingen': {'Latitude': 47.4882, 'Longitude': 7.5898},
    'Brione sopra Minusio': {'Latitude': 46.1858, 'Longitude': 8.8088},
    'Ronco sopra Ascona': {'Latitude': 46.1442, 'Longitude': 8.7318},
    'Grindelwald': {'Latitude': 46.6242, 'Longitude': 8.0365},
    'Blonay': {'Latitude': 46.4677, 'Longitude': 6.8942},
    'Stettfurt': {'Latitude': 47.5278, 'Longitude': 8.9731},
    'Uitikon Waldegg': {'Latitude': 47.3679, 'Longitude': 8.4661},
    # Weitere Ortschaften hinzufügen, falls erforderlich
}

# Funktion zur Zuordnung der Koordinaten
def get_coordinates(locality):
    coords = locality_coords.get(locality)
    if coords:
        return pd.Series(coords)
    else:
        return pd.Series({'Latitude': np.nan, 'Longitude': np.nan})

most_expensive[['Latitude', 'Longitude']] = most_expensive['Locality'].apply(get_coordinates)
most_expensive = most_expensive.dropna(subset=['Latitude', 'Longitude'])

map_fig = px.scatter_mapbox(
    most_expensive,
    lat='Latitude',
    lon='Longitude',
    hover_name='Locality',
    hover_data=['Price', 'LivingSpace', 'NumberRooms'],
    color='Price',
    size='Price',
    zoom=7,
    height=600,
    title='Teuerste Häuser in der Schweiz'
)

map_fig.update_layout(mapbox_style="open-street-map")
map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# App Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Hauspreise in der Schweiz"), width=15)
    ], style={'textAlign': 'center', 'marginTop': 20, 'marginBottom': 20}),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=bar_fig), width=6),
        dbc.Col(dcc.Graph(figure=scatter_fig), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=map_fig), width=12)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
