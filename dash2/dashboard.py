import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import random
from collections import deque
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Configurações de buffer
buffer_size = 100
time_buffer = deque(maxlen=buffer_size)
heart_rate_buffer = deque(maxlen=buffer_size)
oxygen_level_buffer = deque(maxlen=buffer_size)
body_temp_buffer = deque(maxlen=buffer_size)
acceleration_buffer = deque(maxlen=buffer_size)

# Buffers para anomalias
anomalies_heart_rate = deque(maxlen=buffer_size)
anomalies_oxygen_level = deque(maxlen=buffer_size)
anomalies_body_temp = deque(maxlen=buffer_size)
anomalies_acceleration = deque(maxlen=buffer_size)

# Função para simular dados
def generate_data():
    return {
        'time': pd.Timestamp.now(),
        'heart_rate': random.randint(50, 150),
        'oxygen_level': random.uniform(85, 100),
        'body_temp': random.uniform(35.5, 40.0),
        'acceleration': random.uniform(0, 10)
    }

# Função para identificar anomalias
def check_anomalies(data):
    anomalies = {
        'heart_rate': False,
        'oxygen_level': False,
        'body_temp': False,
        'acceleration': False
    }
    if data['heart_rate'] > 148 or data['heart_rate'] < 51:
        anomalies['heart_rate'] = True
    if data['oxygen_level'] < 86:
        anomalies['oxygen_level'] = True
    if data['body_temp'] > 39.9 or data['body_temp'] < 35.7:
        anomalies['body_temp'] = True
    if data['acceleration'] > 9.9:
        anomalies['acceleration'] = True
    return anomalies

# Informações do usuário
user_info = {
    'id': '001',
    'name': 'João da Silva',
    'age': 29,
    'history': 'Sem histórico cardiovascular significativo. Não fumante. Pratica exercícios regularmente.'
}

app.layout = html.Div([
    html.H1("Painel de Monitoramento de Sinais Vitais em Tempo Real 2", style={'textAlign': 'center', 'marginBottom': '20px', 'color': 'white'}),

    dbc.Card(
        dbc.CardBody([
            html.H4("Informações do Usuário", className="card-title"),
            html.P(f"ID: {user_info['id']}", className="card-text"),
            html.P(f"Nome: {user_info['name']}", className="card-text"),
            html.P(f"Idade: {user_info['age']}", className="card-text"),
            html.P(f"Histórico Cardiovascular: {user_info['history']}", className="card-text"),
        ]),
        style={"width": "18rem", "marginBottom": "20px"}
    ),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='heart-rate-graph', animate=True, style={'height': '400px'}), width=6),
        dbc.Col(dcc.Graph(id='oxygen-level-graph', animate=True, style={'height': '400px'}), width=6),
    ], style={'marginBottom': '20px'}),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='body-temp-graph', animate=True, style={'height': '400px'}), width=6),
        dbc.Col(dcc.Graph(id='acceleration-graph', animate=True, style={'height': '400px'}), width=6),
    ], style={'marginBottom': '20px'}),
    
    dbc.Alert(id='alert', is_open=False, duration=3000, style={'position': 'fixed', 'top': 10, 'right': 10, 'width': '30%'}),
    
    dcc.Interval(id='interval-component', interval=1*3000, n_intervals=0),
], style={'padding': '20px', 'backgroundColor': '#1e2130', 'height': '100vh', 'overflowY': 'scroll'})

@app.callback([Output('heart-rate-graph', 'figure'),
               Output('oxygen-level-graph', 'figure'),
               Output('body-temp-graph', 'figure'),
               Output('acceleration-graph', 'figure'),
               Output('alert', 'children'),
               Output('alert', 'is_open')],
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    new_data = generate_data()
    anomalies = check_anomalies(new_data)
    
    time_buffer.append(new_data['time'])
    heart_rate_buffer.append(new_data['heart_rate'])
    oxygen_level_buffer.append(new_data['oxygen_level'])
    body_temp_buffer.append(new_data['body_temp'])
    acceleration_buffer.append(new_data['acceleration'])
    
    anomalies_heart_rate.append(anomalies['heart_rate'])
    anomalies_oxygen_level.append(anomalies['oxygen_level'])
    anomalies_body_temp.append(anomalies['body_temp'])
    anomalies_acceleration.append(anomalies['acceleration'])

    data = pd.DataFrame({
        'time': list(time_buffer),
        'heart_rate': list(heart_rate_buffer),
        'oxygen_level': list(oxygen_level_buffer),
        'body_temp': list(body_temp_buffer),
        'acceleration': list(acceleration_buffer),
        'anomalies_heart_rate': list(anomalies_heart_rate),
        'anomalies_oxygen_level': list(anomalies_oxygen_level),
        'anomalies_body_temp': list(anomalies_body_temp),
        'anomalies_acceleration': list(anomalies_acceleration)
    })

    # Definir limites fixos de tempo e valores esperados
    x_range = [pd.Timestamp.now() - pd.Timedelta(seconds=buffer_size), pd.Timestamp.now()]
    y_range_heart_rate = [50, 150]
    y_range_oxygen_level = [85, 100]
    y_range_body_temp = [35, 40]
    y_range_acceleration = [0, 10]

    alert_message = ""
    alert_open = False
    if anomalies['heart_rate']:
        alert_message += "Anomalia de Frequência Cardíaca Detectada! "
        alert_open = True
    if anomalies['oxygen_level']:
        alert_message += "Anomalia de Nível de Oxigênio Detectada! "
        alert_open = True
    if anomalies['body_temp']:
        alert_message += "Anomalia de Temperatura Corporal Detectada! "
        alert_open = True
    if anomalies['acceleration']:
        alert_message += "Anomalia de Aceleração Detectada! "
        alert_open = True
    
    # Gráfico de Frequência Cardíaca
    heart_rate_fig = go.Figure()
    heart_rate_fig.add_trace(go.Scatter(
        x=data['time'], y=data['heart_rate'], mode='lines+markers', name='Frequência Cardíaca',
        line=dict(color='blue'),
        marker=dict(color=np.where(data['anomalies_heart_rate'], 'red', 'blue'))
    ))
    heart_rate_fig.update_layout(title='Frequência Cardíaca', xaxis_title='Tempo', yaxis_title='BPM', xaxis=dict(range=x_range), yaxis=dict(range=y_range_heart_rate), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Nível de Oxigênio
    oxygen_level_fig = go.Figure()
    oxygen_level_fig.add_trace(go.Scatter(
        x=data['time'], y=data['oxygen_level'], mode='lines+markers', name='Nível de Oxigênio',
        line=dict(color='green'),
        marker=dict(color=np.where(data['anomalies_oxygen_level'], 'red', 'green'))
    ))
    oxygen_level_fig.update_layout(title='Nível de Oxigênio', xaxis_title='Tempo', yaxis_title='Porcentagem', xaxis=dict(range=x_range), yaxis=dict(range=y_range_oxygen_level), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Temperatura Corporal
    body_temp_fig = go.Figure()
    body_temp_fig.add_trace(go.Scatter(
        x=data['time'], y=data['body_temp'], mode='lines+markers', name='Temperatura Corporal',
        line=dict(color='yellow'),
        marker=dict(color=np.where(data['anomalies_body_temp'], 'red', 'yellow'))
    ))
    body_temp_fig.update_layout(title='Temperatura Corporal', xaxis_title='Tempo', yaxis_title='Celsius', xaxis=dict(range=x_range), yaxis=dict(range=y_range_body_temp), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    # Gráfico de Aceleração
    acceleration_fig = go.Figure()
    acceleration_fig.add_trace(go.Scatter(
        x=data['time'], y=data['acceleration'], mode='lines+markers', name='Aceleração',
        line=dict(color='orange'),
        marker=dict(color=np.where(data['anomalies_acceleration'], 'red', 'orange'))
    ))
    acceleration_fig.update_layout(title='Aceleração', xaxis_title='Tempo', yaxis_title='m/s^2', xaxis=dict(range=x_range), yaxis=dict(range=y_range_acceleration), plot_bgcolor='#1e2130', paper_bgcolor='#1e2130', font=dict(color='white'))

    return heart_rate_fig, oxygen_level_fig, body_temp_fig, acceleration_fig, alert_message, alert_open

if __name__ == '__main__':
    app.run_server(debug=True)
