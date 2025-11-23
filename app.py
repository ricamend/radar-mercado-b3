import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Radar Pré-Abertura B3", layout="centered")

st.title("🇧🇷 Radar de Pré-Abertura - B3")
st.markdown("Análise automática do humor do mercado mundial para prever o IBOV.")
st.markdown("---")

# Dicionário de Ativos (Tickers do Yahoo Finance)
tickers = {
    'S&P 500 Futuro': 'ES=F',
    'Nasdaq Futuro': 'NQ=F',
    'Dólar (USD/BRL)': 'BRL=X',  # Adicionado
    'Petróleo Brent': 'BZ=F',
    'Ouro': 'GC=F',
    'EWZ (Brasil em NY)': 'EWZ',
    'Vale ADR (NY)': 'VALE'
}

def pegar_dados():
    dados_lista = []
    for nome, ticker in tickers.items():
        try:
            acao = yf.Ticker(ticker)
            # Pega dados de 5 dias para garantir histórico
            hist = acao.history(period="5d")
            
            if len(hist) > 0:
                preco_atual = hist['Close'].iloc[-1]
                # Pega o penúltimo fecho para calcular a variação
                fechamento_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
                
                variacao = ((preco_atual - fechamento_anterior) / fechamento_anterior) * 100
                
                # Formatação específica para moeda vs pontos
                simbolo = "R$" if "Dólar" in nome else "$"
                
                dados_lista.append({
                    "Ativo": nome,
                    "Preço": f"{simbolo} {preco_atual:.2f}",
                    "Variação (%)": variacao,
                    "Valor_Cru": variacao # Guardamos o valor numérico para a IA usar
                })
        except Exception as e:
            dados_lista.append({"Ativo": nome, "Preço": "Erro", "Variação (%)": 0.0, "Valor_Cru": 0.0})
            
    return dados_lista

# Botão de Atualizar
if st.button('Atualizar Dados Agora 🔄'):
    with st.spinner('A ligar aos mercados globais...'):
        dados = pegar_dados()
    
    # Criando colunas para exibir
    col1, col2 = st.columns(2)
    
    for i, item in enumerate(dados):
        variacao = item['Variação (%)']
        valor_formatado = f"{variacao:.2f}%"
        
        with (col1 if i % 2 == 0 else col2):
            st.metric(
                label=item['Ativo'],
                value=item['Preço'],
                delta=valor_formatado
            )

    st.markdown("---")
    st.caption("*Dados do Yahoo Finance (atraso de 15min).")

    # --- CÉREBRO DA ANÁLISE (IA Lógica) ---
    st.subheader("🤖 Análise do Cenário")
    
    # Extrair valores para análise
    def get_var(nome):
        item = next((x for x in dados if x["Ativo"] == nome), None)
        return item['Valor_Cru'] if item else 0.0

    sp500_var = get_var('S&P 500 Futuro')
    dolar_var = get_var('Dólar (USD/BRL)')
    ewz_var = get_var('EWZ (Brasil em NY)')
    petroleo_var = get_var('Petróleo Brent')

    # Lógica de Decisão
    st.write(f"**Resumo Técnico:** S&P 500 ({sp500_var:.2f}%) | Dólar ({dolar_var:.2f}%)")

    if sp500_var > 0.3 and dolar_var < -0.1:
        st.success("🚀 **Cenário MUITO OTIMISTA:** Bolsas lá fora sobem e o Dólar cai. O Ibovespa deve abrir com força compradora.")
    
    elif sp500_var < -0.3 and dolar_var > 0.1:
        st.error("🩸 **Cenário PESSIMISTA:** Aversão ao risco global. Bolsas caem e Dólar sobe. O Ibovespa deve sofrer na abertura.")
    
    elif petroleo_var < -1.0 and ewz_var < 0:
        st.warning("⚠️ **Alerta de Commodities:** O Petróleo está a cair forte. Mesmo que o resto esteja bem, a Petrobras pode segurar o índice.")
        
    elif dolar_var > 0.5:
        st.warning("💵 **Atenção ao Câmbio:** O Dólar está a subir forte. Isso costuma tirar liquidez da Bolsa.")
        
    else:
        st.info("⚖️ **Cenário Misto/Indefinido:** Sinais divergentes entre Dólar e Bolsas. O mercado deve abrir de lado à espera de notícias.")

else:
    st.info("Clique no botão acima para ver a tendência de abertura.")
