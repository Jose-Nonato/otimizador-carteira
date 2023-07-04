from flask import Flask, request, render_template, redirect, session
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pypfopt as opt
from pypfopt import CLA, plotting
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "chavinha secreta"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tickers = request.form.get('ativos').split()
        session['tickers'] = tickers
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    tickers = session.get('tickers')
    # session.pop('tickers', None)

    dados = yf.download(tickers, start='2000-01-01')['Adj Close']
    colunas_removidas = []
    for coluna in dados.columns:
        if dados[coluna].isnull().all():
            colunas_removidas.append(coluna)
            dados.drop(coluna, axis=1, inplace=True)

    filtro_fechamento = dados[dados.index >= pd.to_datetime('2018-01-01')]
    fig_1 = go.Figure()
    for coluna in filtro_fechamento.columns:
        fig_1.add_trace(go.Scatter(x=filtro_fechamento.index, y=filtro_fechamento[coluna], name=coluna))
    fig_1.update_layout(
        title='Fechamento dos ativos no ultimos 5 anos',
        xaxis_title='Data',
        yaxis_title='Preço',
        legend_title='Ativos'
    )
    graph_1 = fig_1.to_html(full_html=False)

    retorno_estimado = opt.expected_returns.capm_return(dados)
    ativos = retorno_estimado.index
    retornos = retorno_estimado.values
    fig_2 = go.Figure(data=go.Bar(x=ativos, y=retornos))
    fig_2.update_layout(
        title='Retorno Estimado',
        xaxis_title='Ativo',
        yaxis_title='Porcentagem'
    )
    graph_2 = fig_2.to_html(full_html=False)

    matriz_cov = opt.risk_models.sample_cov(dados)
    estimativa_reducao = opt.risk_models.CovarianceShrinkage(dados).ledoit_wolf()

    fig_3 = go.Figure(data=go.Heatmap(z=matriz_cov, x=matriz_cov.columns, y=matriz_cov.index))
    fig_3.update_layout(
        title='Matriz de Covariância'
    )
    graph_3 = fig_3.to_html(full_html=False)

    fig_4 = go.Figure(data=go.Heatmap(z=estimativa_reducao, x=estimativa_reducao.columns, y=estimativa_reducao.index))
    fig_4.update_layout(
        title='Estimativa de Redução'
    )
    graph_4 = fig_4.to_html(full_html=False)

    ef = opt.EfficientFrontier(retorno_estimado, estimativa_reducao)
    pesos = ef.max_sharpe()
    
    fig_5 = go.Figure(data=[go.Bar(x=list(pesos.keys()), y=list(pesos.values() ))])
    fig_5.update_layout(
        title='Pesos Otimizados'
    )
    graph_5 = fig_5.to_html(full_html=False)

    expected_return, volatility, sharpe_ratio = ef.portfolio_performance(verbose=True)
    expected_return = "{:.2%}".format(expected_return)
    volatility = "{:.2%}".format(volatility)
    sharpe_ratio = "{:.2f}".format(sharpe_ratio)
    portfolio_performance = [expected_return, volatility, sharpe_ratio]

    retorno_esperado = dados.pct_change()
    retorno_esperado = retorno_esperado.dropna()
    volatibilidade = pd.DataFrame(retorno_esperado.std(), columns=['Volatibilidade'])
    retornos_medios = pd.DataFrame(retorno_estimado)
    retornos_medios = retornos_medios.rename({'mkt': 'Retornos'}, axis=1)
    risco_retorno = pd.concat([retornos_medios, volatibilidade], axis=1)

    fig_6 = go.Figure()
    fig_6.add_trace(go.Scatter(
        x=risco_retorno['Volatibilidade'],
        y=risco_retorno['Retornos'],
        mode='markers',
        text=risco_retorno.index,
        marker=dict(
            color='black',
            size=10,
            line=dict(
                color='white',
                width=1
            )
        )
    ))
    fig_6.update_layout(
        title={
            'text': 'Gráfico Volatilidade x Retorno',
            'pad': {'t': 10}
        },
        xaxis_title='Volatibilidade',
        yaxis_title='Retornos'
    )
    graph_6 = fig_6.to_html(full_html=False)

    cla = opt.CLA(retorno_estimado, estimativa_reducao)
    cla.max_sharpe()

    expected_return_2, volatility_2, sharpe_ratio_2 = cla.portfolio_performance(verbose=True)
    expected_return_2 = "{:.2%}".format(expected_return_2)
    volatility_2 = "{:.2f}".format(volatility_2)
    sharpe_ratio_2 = "{:.2f}".format(sharpe_ratio_2)
    optimal_point = [expected_return_2, volatility_2, sharpe_ratio_2]

    plt.figure()
    plotting.plot_efficient_frontier(cla)
    plt.savefig("./static/assets/fronteira_eficiencia.png")

    return render_template('dashboard.html', 
                           colunas_removidas=colunas_removidas, 
                           graph_1=graph_1, 
                           graph_2=graph_2, 
                           graph_3=graph_3,
                           graph_4=graph_4, 
                           graph_5=graph_5, 
                           portfolio_performance=portfolio_performance,
                           graph_6=graph_6,
                           optimal_point=optimal_point
                        )

if __name__ == "__main__":
    app.run(debug=True)
