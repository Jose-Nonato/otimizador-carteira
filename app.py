from flask import Flask, render_template, request, redirect, session
import yfinance as yf
from functions import RentabilidadeTickers, RetornoDiarioTickers, MatrizCov, VerboseCarteira, RentabilidadeRetorno, VerboseCarteiraEficiente

app = Flask(__name__)
app.secret_key = "secret key"

@app.route("/", methods=["GET", "POST"])
def initial():
    if request.method == "POST":
        tickers = request.form.get("tickers").split()
        session["tickers"] = tickers
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/dashboard")
def dash():
    tickers = session.get("tickers")
    # session.pop('tickers', None)

    dados = yf.download(tickers, start='2018-01-01', progress=False)['Adj Close']
    colunas_removidas = []
    for coluna in dados.columns:
        if dados[coluna].isnull().all():
            colunas_removidas.append(coluna)
            dados.drop(coluna, axis=1, inplace=True)
    
    fig_fechamento = RentabilidadeTickers(dados) # Criação do gráfico de fechamento

    fig_retorno = RetornoDiarioTickers(dados) # Retorno diário dos tickers

    fig_matriz_cov, fig_estimativa_reducao, fig_retorno_estimado, fig_pesos_otimizados = MatrizCov(dados)

    frase = VerboseCarteira(dados)

    fig_rentabilidade = RentabilidadeRetorno(dados)

    frase_eficiente = VerboseCarteiraEficiente(dados)

    return render_template('dash.html', colunas_removidas=colunas_removidas, 
                           plot_fechamento=fig_fechamento.to_html(full_html=False),
                           plot_retorno=fig_retorno.to_html(full_html=False),
                           plot_matriz_cov=fig_matriz_cov.to_html(full_html=False),
                           plot_estimativa_reducao=fig_estimativa_reducao.to_html(full_html=False),
                           plot_retorno_estimado=fig_retorno_estimado.to_html(full_html=False),
                           plot_pesos_otimizados=fig_pesos_otimizados.to_html(full_html=False),
                           frase=frase,
                           plot_rentabilidade=fig_rentabilidade.to_html(full_html=False),
                           frase_eficiente=frase_eficiente
                           )

if __name__ == "__main__":
    app.run(debug=True)
