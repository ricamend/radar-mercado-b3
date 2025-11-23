import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Radar Pré-Abertura B3", layout="centered")

st.title("🇧🇷 Radar de Pré-Abertura - B3")
st.markdown("Análise automática do humor do mercado mundial para prever o IBOV.")
st.markdown("---")

# Dicionário de Ativos (Tickers do Yahoo Finance)
# ES=F: S&P 500 Futuro
# NQ=F: Nasdaq Futuro
# BZ=F: Petróleo Brent
# GC=F: Ouro
# EWZ: ETF do Brasil em NY
# VALE: Vale ADR (Reflete Minério/China)
tickers = {
    'S&P 500 Futuro': 'ES=F',
    'Nasdaq Futuro': 'NQ=F',
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
            # Pega dados do dia
            hist = acao.history(period="5d")
            
            if len(hist) > 0:
                preco_atual = hist['Close'].iloc[-1]
                # Tenta pegar fechamento anterior para calcular variação
                # Nota: Em futuros, o calculo exato de variação pode variar, 
                # mas usamos o fechamento do candle anterior como base.
                fechamento_anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
                
                variacao = ((preco_atual - fechamento_anterior) / fechamento_anterior) * 100
                
                dados_lista.append({
                    "Ativo": nome,
                    "Preço ($)": f"{preco_atual:.2f}",
                    "Variação (%)": variacao
                })
        except Exception as e:
            dados_lista.append({"Ativo": nome, "Preço ($)": "Erro", "Variação (%)": 0.0})
            
    return dados_lista

# Botão de Atualizar
if st.button('Atualizar Dados Agora 🔄'):
    dados = pegar_dados()
    
    # Criando colunas para exibir
    col1, col2 = st.columns(2)
    
    for i, item in enumerate(dados):
        variacao = item['Variação (%)']
        valor_formatado = f"{variacao:.2f}%"
        
        # Define cor (Verde para alta, Vermelho para baixa)
        cor_delta = "normal" # O Streamlit usa cores automáticas no metric
        
        # Exibição visual
        with (col1 if i % 2 == 0 else col2):
            st.metric(
                label=item['Ativo'],
                value=item['Preço ($)'],
                delta=valor_formatado,
                delta_color="normal" # normal = verde para positivo, vermelho para negativo
            )

    st.markdown("---")
    st.caption("*Dados fornecidos pelo Yahoo Finance. Podem haver atrasos de 15 minutos.")

    # Análise Automatizada Simples
    st.subheader("🤖 Análise Rápida da IA")
    
    sp500 = next((item for item in dados if item["Ativo"] == "S&P 500 Futuro"), None)
    ewz = next((item for item in dados if item["Ativo"] == "EWZ (Brasil em NY)"), None)
    
    if sp500 and ewz:
        var_sp = sp500['Variação (%)']
        var_ewz = ewz['Variação (%)']
        
        if var_sp > 0.2 and var_ewz > 0.5:
            st.success("✅ **Cenário Otimista:** Exterior positivo e Brasil (EWZ) subindo. Tendência de abertura em ALTA.")
        elif var_sp < -0.2 and var_ewz < -0.5:
            st.error("🔻 **Cenário Pessimista:** Exterior negativo e Brasil caindo. Tendência de abertura em BAIXA.")
        else:
            st.warning("⚠️ **Cenário Misto/Neutro:** Sinais divergentes. Cuidado com a volatilidade na abertura.")

else:
    st.info("Clique no botão acima para carregar os dados em tempo real.")
