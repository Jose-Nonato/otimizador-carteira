import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Exemplo de Gráfico'),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Categoria 1'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Categoria 2'},
            ],
            'layout': {
                'title': 'Gráfico de Barras'
            }
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)