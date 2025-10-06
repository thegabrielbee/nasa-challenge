import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

df = pd.read_csv('data/data.csv')
df['date'] = pd.to_datetime(df['date']).dt.date

mapbox_access_token = "pk.eyJ1IjoiZ2FicmllbGJlZSIsImEiOiJjbDR6eGZ1NWEzN2ZuM2pzOHdyanYzdmNlIn0.N5vLKDGr4XcUuWkehDgLQQ"
px.set_mapbox_access_token(mapbox_access_token)

FLORIPA_CENTER = {"lat": -27.5969, "lon": -48.5489}
COLOR_MAP = {
    'Moderate': 'yellow',
    'High': 'orange',
    'Critical': 'red'
}

SIZE_MAP = {
    'Moderate': 10,
    'High': 20,
    'Critical': 30
}

MAP = {
    'Moderate': "Moderate",
    'High': "High",
    'Critical': "Critical"
}

df['centroid_size'] = df['risk_classification'].map(SIZE_MAP)

CHAT_QA = {
    "What action should I take NOW?": "[ACTION] (Monitor / Alert / Evacuate) within 48h.",
    "What is the EXACT reason for this risk?": "Explicit Logic: GPM + SMAP + SRTM.",
    "What is the Risk Level in the District?": "[LEVEL] (Moderate / High / Critical)."
}

df = df[df["risk_classification"] != "Baixo"]

available_dates = sorted(df['date'].unique())
min_date = available_dates[0]
max_date = available_dates[-1]

all_days_in_range = [min_date + timedelta(days=x) for x in range((max_date - min_date).days + 1)]
disabled_days = [day for day in all_days_in_range if day not in available_dates]

app = dash.Dash(__name__)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>ORBISHIELD AI</title>
        {%favicon%}
        {%css%}
        <style>
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
            
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
                overflow: hidden;
                position: fixed;
                top: 0;
                left: 0;
            }
            
            #react-entry-point {
                height: 100vh;
                width: 100vw;
                overflow: hidden;
                position: fixed;
                top: 0;
                left: 0;
            }
            
            .dash-spreadsheet-container {
                overflow: hidden !important;
            }
            
            .js-plotly-plot {
                overflow: hidden !important;
            }
            
            /* Loading Screen Styles */
            .loading-screen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                animation: fadeOut 0.5s ease-in-out 2.5s forwards;
            }
            
            .loading-logo {
                font-size: 3rem;
                font-weight: bold;
                color: white;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                animation: fadeIn 1s ease-in-out;
            }
            
            .loading-subtitle {
                font-size: 1.2rem;
                color: #ecf0f1;
                margin-bottom: 2rem;
                text-align: center;
                animation: fadeIn 1s ease-in-out 0.5s both;
            }
            
            .loading-spinner {
                width: 60px;
                height: 60px;
                border: 4px solid rgba(255,255,255,0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }
            
            .loading-text {
                color: #ecf0f1;
                font-size: 1rem;
                animation: fadeIn 1s ease-in-out 1s both;
            }
            
            .loading-dots {
                display: inline-block;
                animation: blink 1.5s infinite;
            }
        </style>
    </head>
    <body>
        <!-- Loading Screen -->
        <div class="loading-screen" id="loading-screen">
            <div class="loading-logo">🛡️ ORBISHIELD AI</div>
            <div class="loading-subtitle">2025 NASA Space Apps Challenge</div>
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading Risk Analysis System<span class="loading-dots">...</span></div>
        </div>
        
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        
        <script>
            // Hide loading screen after page loads
            window.addEventListener('load', function() {
                setTimeout(function() {
                    const loadingScreen = document.getElementById('loading-screen');
                    if (loadingScreen) {
                        loadingScreen.style.display = 'none';
                    }
                }, 2500);
            });
        </script>
    </body>
</html>
'''

app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'width': '100vw', 'fontFamily': 'sans-serif', 'overflow': 'hidden', 'margin': '0', 'padding': '0', 'position': 'fixed', 'top': '0', 'left': '0'}, children=[
    
    # Título da página
    html.Div(style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '15px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flexShrink': '0'}, children=[
        html.H1("ORBISHIELD AI - 2025 NASA Space Apps Challenge", style={'margin': '0', 'fontSize': '24px', 'fontWeight': 'bold'})
    ]),
    
    # Container principal com flexbox horizontal
    html.Div(style={'display': 'flex', 'height': 'calc(100vh - 70px)', 'padding': '10px', 'overflow': 'hidden', 'minHeight': '0'}, children=[
        html.Div(style={'width': '25%', 'padding': '0 10px 0 0', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'}, children=[
        html.Div(style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '15px', 'height': '100%', 'overflow': 'hidden'}, children=[
            html.H3("Date Filter", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.P("(only available dates)", style={'textAlign': 'center', 'fontSize': '0.9em', 'color': '#666', 'marginBottom': '25px'}),
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

        html.Div(style={'width': '75%', 'padding': '0 0 0 10px', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'}, children=[
            html.Div(style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '15px', 'height': '100%', 'overflow': 'hidden'}, children=[
                dcc.Loading(
                    id="map-loading",
                    type="circle",
                    color="#007bff",
                    children=[
        dcc.Graph(
            id='map-graph',
                            style={'height': '100%', 'width': '100%', 'overflow': 'hidden'}
                        )
                    ],
                    style={'height': '100%', 'width': '100%'}
                )
            ])
        ])
    ]),  # Fecha o container principal flexbox horizontal

    # Botão do Chat (canto inferior esquerdo)
    html.Button(
        "💬 Chat",
        id="chat-button",
        n_clicks=0,
        style={
            'position': 'fixed',
            'bottom': '20px',
            'left': '20px',
            'zIndex': '1000',
            'backgroundColor': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '25px',
            'padding': '12px 20px',
            'fontSize': '16px',
            'fontWeight': 'bold',
            'cursor': 'pointer',
            'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
            'transition': 'all 0.3s ease'
        }
    ),

    # Modal do Chat
    html.Div(
        id="chat-modal",
        style={
            'position': 'fixed',
            'bottom': '80px',
            'left': '20px',
            'width': '350px',
            'height': '500px',
            'backgroundColor': 'white',
            'borderRadius': '15px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.3)',
            'zIndex': '1001',
            'display': 'none',
            'flexDirection': 'column',
            'border': '1px solid #ddd'
        },
        children=[
            # Header do Chat
            html.Div(
                style={
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'padding': '15px',
                    'borderRadius': '15px 15px 0 0',
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center'
                },
                children=[
                    html.H4("🤖 Risk Assistant", style={'margin': '0', 'fontSize': '18px'}),
                    html.Button("✕", id="close-chat", style={
                        'background': 'none',
                        'border': 'none',
                        'color': 'white',
                        'fontSize': '20px',
                        'cursor': 'pointer'
                    })
                ]
            ),
            
            # Área de Mensagens
            html.Div(
                id="chat-messages",
                style={
                    'flex': '1',
                    'padding': '15px',
                    'overflowY': 'auto',
                    'backgroundColor': '#f8f9fa'
                },
                children=[
                    html.Div(
                        "👋 Hello! I'm your risk analysis assistant. Choose a question:",
                        style={
                            'backgroundColor': '#e3f2fd',
                            'padding': '10px',
                            'borderRadius': '10px',
                            'marginBottom': '10px',
                            'fontSize': '14px'
                        }
                    )
                ]
            ),
            
            # Interval para controlar loading
            dcc.Interval(
                id='loading-interval',
                interval=2000,  # 2 segundos
                n_intervals=0,
                disabled=True
            ),
            
            # Botões de Perguntas
            html.Div(
                style={
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '0 0 15px 15px',
                    'borderTop': '1px solid #eee'
                },
                children=[
                    html.Button(
                        "What action should I take NOW?",
                        id="question-1",
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'marginBottom': '8px',
                            'backgroundColor': '#f8f9fa',
                            'border': '1px solid #ddd',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'textAlign': 'left'
                        }
                    ),
                    html.Button(
                        "What is the EXACT reason for this risk?",
                        id="question-2",
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'marginBottom': '8px',
                            'backgroundColor': '#f8f9fa',
                            'border': '1px solid #ddd',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'textAlign': 'left'
                        }
                    ),
                    html.Button(
                        "What is the Risk Level in the District?",
                        id="question-3",
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'border': '1px solid #ddd',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'textAlign': 'left'
                        }
                    )
                ]
            )
        ]
    )
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
        zoom=10,
        center=FLORIPA_CENTER,
        hover_data=["srtm_score", "gpm_score", "smap_score", "recommended_action"],
        mapbox_style="streets", # Estilos: "streets", "satellite", "dark", "light"
        title=f"Ocurrences to date: {selected_date.strftime('%d/%m/%Y')}"
    )

    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        legend_title_text='Risk Level'
    )
    
    # Melhorar a formatação do hover
    fig.update_traces(
        hovertemplate="<b>🔍 Risk Analysis</b><br>" +
                     "<b>Risk Level:</b> %{customdata[0]}<br>" +
                     "<b>SRTM Score:</b> %{customdata[1]}<br>" +
                     "<b>GPM Score:</b> %{customdata[2]}<br>" +
                     "<b>SMAP Score:</b> %{customdata[3]}<br>" +
                     "<b>Action:</b> %{customdata[4]}<br>" +
                     "<b>Coordinates:</b> %{lat:.5f}, %{lon:.5f}<br>" +
                     "<extra></extra>",
        customdata=filtered_df[["risk_classification", "srtm_score", "gpm_score", "smap_score", "recommended_action"]].values
    )

    return fig

@app.callback(
    Output('chat-modal', 'style'),
    [Input('chat-button', 'n_clicks'),
     Input('close-chat', 'n_clicks')],
    [State('chat-modal', 'style')]
)
def toggle_chat(chat_clicks, close_clicks, current_style):
    ctx = callback_context
    if not ctx.triggered:
        return current_style

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'chat-button' and chat_clicks > 0:
        new_style = current_style.copy()
        new_style['display'] = 'flex'
        return new_style
    elif button_id == 'close-chat' and close_clicks > 0:
        new_style = current_style.copy()
        new_style['display'] = 'none'
        return new_style

    return current_style

# Callback para as perguntas do chat com loading assíncrono
# Store para controlar o estado do loading
loading_state = {'is_loading': False, 'question': None}

@app.callback(
    [Output('chat-messages', 'children'),
     Output('loading-interval', 'disabled')],
    [Input('question-1', 'n_clicks'),
     Input('question-2', 'n_clicks'),
     Input('question-3', 'n_clicks')],
    [State('chat-messages', 'children')]
)
def handle_question(click1, click2, click3, current_messages):
    ctx = callback_context
    if not ctx.triggered or ctx.triggered[0]['value'] == 0:
        return current_messages, True

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    question_map = {
        'question-1': "What action should I take NOW?",
        'question-2': "What is the EXACT reason for this risk?",
        'question-3': "What is the Risk Level in the District?"
    }

    question = question_map.get(button_id)
    if question:
        # Adiciona pergunta do usuário
        user_message = html.Div(
            f"👤 {question}",
            style={
                'backgroundColor': '#007bff',
                'color': 'white',
                'padding': '10px',
                'borderRadius': '10px',
                'marginBottom': '10px',
                'fontSize': '14px',
                'textAlign': 'right'
            }
        )

        # Adiciona indicador de carregamento
        loading_message = html.Div(
            [
                html.Span("🤖 ", style={'fontSize': '16px'}),
                html.Span("Analyzing data", style={'fontSize': '14px', 'color': '#666'}),
                html.Span("...", style={'fontSize': '14px', 'color': '#666', 'animation': 'blink 1s infinite'})
            ],
            style={
                'backgroundColor': '#f8f9fa',
                'padding': '10px',
                'borderRadius': '10px',
                'marginBottom': '10px',
                'fontSize': '14px',
                'textAlign': 'left',
                'border': '1px solid #e9ecef',
                'fontStyle': 'italic'
            }
        )

        # Configura estado de loading
        loading_state['is_loading'] = True
        loading_state['question'] = question

        return current_messages + [user_message, loading_message], False

    return current_messages, True

@app.callback(
    Output('chat-messages', 'children', allow_duplicate=True),
    Input('loading-interval', 'n_intervals'),
    State('chat-messages', 'children'),
    prevent_initial_call=True
)
def update_loading(n_intervals, current_messages):
    if not loading_state['is_loading']:
        return current_messages
    
    # Remove loading e adiciona resposta
    question = loading_state['question']
    answer = CHAT_QA[question]
    
    # Remove a última mensagem (loading) e adiciona a resposta
    messages_without_loading = current_messages[:-1] if current_messages else []
    
    bot_message = html.Div(
        f"🤖 {answer}",
        style={
            'backgroundColor': '#e3f2fd',
            'padding': '10px',
            'borderRadius': '10px',
            'marginBottom': '10px',
            'fontSize': '14px',
            'textAlign': 'left'
        }
    )
    
    # Reset loading state
    loading_state['is_loading'] = False
    loading_state['question'] = None
    
    return messages_without_loading + [bot_message]

if __name__ == '__main__':
    app.run(debug=True)

# Para deploy com gunicorn
server = app.server