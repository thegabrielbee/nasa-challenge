import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

df = pd.read_csv('data/data.csv')
df['date'] = pd.to_datetime(df['date']).dt.date

mapbox_access_token = "pk.eyJ1IjoiZ2FicmllbGJlZSIsImEiOiJjbDR6eGZ1NWEzN2ZuM2pzOHdyanYzdmNlIn0.N5vLKDGr4XcUuWkehDgLQQ"
px.set_mapbox_access_token(mapbox_access_token)

FLORIPA_CENTER = {"lat": -27.5969, "lon": -48.5489}
COLOR_MAP = {
    'Moderado': 'yellow',
    'Alto': 'orange',
    'Crítico': 'red'
}

SIZE_MAP = {
    'Baixo': 150,
    'Moderado': 150,
    'Alto': 30,
    'Crítico': 50
}

df['centroid_size'] = df['risk_classification'].map(SIZE_MAP)


available_dates = sorted(df['date'].unique())
min_date = available_dates[0]
max_date = available_dates[-1]

all_days_in_range = [min_date + timedelta(days=x) for x in range((max_date - min_date).days + 1)]
disabled_days = [day for day in all_days_in_range if day not in available_dates]

app = dash.Dash(__name__)
app.layout = html.Div(style={'display': 'flex', 'padding': '20px', 'fontFamily': 'sans-serif'}, children=[

    html.Div(style={'width': '25%', 'padding': '0 20px 0 0'}, children=[
        html.Div(style={'backgroundColor': '#f0f0f0', 'padding': '20px', 'borderRadius': '15px', 'height': '100%'}, children=[
            html.H3("Date Filter", style={'textAlign': 'center'}),
            html.P("(only available dates)", style={'textAlign': 'center', 'fontSize': '0.9em', 'color': '#666'}),
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                initial_visible_month=min_date,
                date=min_date,
                display_format='MM/DD/YYYY',
                disabled_days=disabled_days,
                style={'width': '100%'}
            )
        ])
    ]),

    html.Div(style={'width': '75%', 'backgroundColor': '#f0f0f0', 'padding': '20px', 'borderRadius': '15px'}, children=[
        dcc.Graph(
            id='map-graph',
            style={'height': '80vh'}
        )
    ])
])

@app.callback(
    Output('map-graph', 'figure'),
    Input('date-picker', 'date')
)
def update_map(selected_date_str):
    if not selected_date_str:
        return px.scatter_mapbox()

    selected_date = date.fromisoformat(selected_date_str)

    filtered_df = df[df['date'] == selected_date]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="lat",
        lon="lon",
        color="risk_classification",
        color_discrete_map=COLOR_MAP,
        size="centroid_size",
        size_max=30,
        zoom=11,
        center=FLORIPA_CENTER,
        hover_data=["srtm_score", "gpm_score", "smap_score", "recommended_action"],
        mapbox_style="streets", # Estilos: "streets", "satellite", "dark", "light"
        title=f"Ocurrences to date: {selected_date.strftime('%d/%m/%Y')}"
    )

    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        legend_title_text='Risk Level'
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)