import plotly.express as px
import pypfopt as opt
import pandas as pd

def RentabilidadeTickers(dados):
    fig = px.line(dados, x=dados.index, y=dados.columns, title="Fechamento Ajustado")
    fig.update_xaxes(title="Data")
    fig.update_yaxes(title="Preço do Fechamento Ajustado")

    return fig

def RetornoDiarioTickers(dados):
    df_retorno = ((dados / dados.iloc[0]) - 1) * 100

    fig = px.line(df_retorno, x=df_retorno.index, y=df_retorno.columns)
    fig.update_layout(
        title="Retorno Diário dos Ativos",
        xaxis_title="Data",
        yaxis_title="Retorno (%)"
    )

    return fig

def MatrizCov(dados):
    matriz_cov = opt.risk_models.sample_cov(dados)
    estimativa_reducao = opt.risk_models.CovarianceShrinkage(dados).ledoit_wolf()
    retorno_estimado = opt.expected_returns.capm_return(dados)

    cov_matrix_df = pd.DataFrame(matriz_cov, columns=dados.columns, index=dados.columns)
    shrinkage_cov_df = pd.DataFrame(estimativa_reducao, columns=dados.columns, index=dados.columns)

    ef = opt.EfficientFrontier(retorno_estimado, estimativa_reducao)
    pesos = ef.max_sharpe()

    df_pesos = pd.DataFrame({'Ativo': list(pesos.keys()), 'Peso': list(pesos.values())})

    fig1 = px.imshow(cov_matrix_df, title='Matriz de Covariância')
    fig2 = px.imshow(shrinkage_cov_df, title='Estimativa de Redução de Covariância')
    fig3 = px.bar(retorno_estimado, x=retorno_estimado.index, y=retorno_estimado.values, title="Retorno Estimado")
    fig4 = px.bar(df_pesos, x='Ativo', y='Peso', title="Pesos Otimizados")

    # Salve os gráficos em arquivos temporários (opcional)
    # fig1.write_image('cov_matrix.png')
    # fig2.write_image('shrinkage_cov.png')

    return fig1, fig2, fig3, fig4

def VerboseCarteira(dados):
    estimativa_reducao = opt.risk_models.CovarianceShrinkage(dados).ledoit_wolf()
    retorno_estimado = opt.expected_returns.capm_return(dados)
    ef = opt.EfficientFrontier(retorno_estimado, estimativa_reducao)
    pesos = ef.max_sharpe()
    expected_return, volatility, sharpe_ratio = ef.portfolio_performance(verbose=True)

    frase = f"<p>Retorno Esperado da Carteira: {expected_return * 100:.2f}%</p><p>Volatibilidade: {volatility * 100:.2f}%</p><p>Índice Sharpe: {sharpe_ratio * 100:.2f}</p>"

    return frase

def RentabilidadeRetorno(dados):
    retorno_estimado = opt.expected_returns.capm_return(dados)
    # retorno_esperado = retorno_esperado.ffill()
    retorno_esperado = dados.pct_change()
    retorno_esperado = retorno_esperado.dropna()
    volatibilidade = pd.DataFrame(retorno_esperado.std(), columns=['Volatibilidade'])
    retornos_medios = pd.DataFrame(retorno_estimado)
    retornos_medios = retornos_medios.rename({'mkt': 'Retornos'}, axis=1)
    risco_retorno = pd.concat([retornos_medios, volatibilidade], axis=1)

    fig = px.scatter(x=risco_retorno['Volatibilidade'], y=risco_retorno['Retornos'], title="Volatibilidade x Retorno", text=risco_retorno.index)
    fig.update_xaxes(title="Volatibilidade")
    fig.update_yaxes(title="Retorno")

    return fig

def VerboseCarteiraEficiente(dados):
    estimativa_reducao = opt.risk_models.CovarianceShrinkage(dados).ledoit_wolf()
    retorno_estimado = opt.expected_returns.capm_return(dados)

    cla = opt.CLA(retorno_estimado, estimativa_reducao)
    cla.max_sharpe()

    expected_return, volatility, sharpe_ratio = cla.portfolio_performance(verbose=True)

    frase = f"<p>Retorno Esperado da Carteira: {expected_return * 100:.2f}%</p><p>Volatibilidade: {volatility * 100:.2f}%</p><p>Índice Sharpe: {sharpe_ratio * 100:.2f}%</p>"

    return frase