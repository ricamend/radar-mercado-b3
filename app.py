import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Radar B3 + Preço Justo", layout="wide")

st.title("🇧🇷 Radar B3 & Calculadora de Preço Justo")
st.markdown("Monitoramento global e cálculo matemático do valor teórico do Índice e Dólar.")
st.markdown("---")

# --- BARRA LATERAL (PARÂMETROS) ---
st.sidebar.header("⚙️ Parâmetros do Preço Justo")
st.sidebar.markdown("Para o cálculo exato, ajuste a taxa de juros anual (DI Futuro).")

# Taxa DI (Estimativa atual do mercado ~12.25% a 13% em 2025, ajuste conforme necessário)
taxa_di = st.sidebar.number_input("Taxa DI/Selic Anual (%)", value=12.25, step=0.25)
dias_uteis_manual = st.sidebar.checkbox("Inserir dias úteis manualmente?", value=False)

# Função para estimar dias úteis até o vencimento
def get_dias_uteis():
    hoje = date.today()
    
    # --- Vencimento INDICE (Quarta-feira mais próxima do dia 15 dos meses PARES) ---
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Lógica simplificada para encontrar próximo mês par
    proximo_mes_ind = mes_atual + (mes_atual % 2) # Se ímpar, soma 1. Se par, soma 2 (próximo vencimento)
    if mes_atual % 2 == 0: proximo_mes_ind += 2 # Se já estamos em mês par, pula para o próximo
    
    # Se virou o ano
    if proximo_mes_ind > 12:
        proximo_mes_ind -= 12
        ano_atual += 1
        
    # Estimativa simples: dia 15 do mês alvo
    vencimento_ind = date(ano_atual, proximo_mes_ind, 15)
    delta_ind = (vencimento_ind - hoje).days
    dias_uteis_ind = int(delta_ind * (5/7)) # Aproximação de dias úteis (tira fds)
    if dias_uteis_ind < 0: dias_uteis_ind = 0

    # --- Vencimento DÓLAR (1º dia útil do mês seguinte) ---
    # Simplificação: dia 1 do mês seguinte
    mes_dol = hoje.month + 1
    ano_dol = hoje.year
    if mes_dol > 12:
        mes_dol = 1
        ano_dol += 1
    
    vencimento_dol = date(ano_dol, mes_dol, 1)
    delta_dol = (vencimento_dol - hoje).days
    dias_uteis_dol = int(delta_dol * (5/7))
    if dias_uteis_dol < 0: dias_uteis_dol = 0
    
    return dias_uteis_ind, dias_uteis_dol

# Define dias úteis (automático ou manual)
du_ind_auto, du_dol_auto = get_dias_uteis()

if dias_uteis_manual:
    du_ind = st.sidebar.number_input("Dias Úteis (Índice)", value=du_ind_auto, min_value=0)
    du_dol = st.sidebar.number_input("Dias Úteis (Dólar)", value=du_dol_auto, min_value=0)
else:
    du_ind = du_ind_auto
    du_dol = du_dol_auto
    st.sidebar.info(f"Dias Úteis estimados: Índice ({du_ind}), Dólar ({du_dol})")


# --- FUNÇÃO DE DADOS ---
def pegar_dados_calculo():
    # Tickers: Ibov Spot (^BVSP), Dolar Spot (BRL=X), S&P Fut (ES=F), Petróleo (BZ=F)
    tickers_map = {
        'Ibovespa (À Vista)': '^BVSP',
        'Dólar (À Vista)': 'BRL=X',
        'S&P 500 Futuro': 'ES=F',
        'Petróleo Brent': 'BZ=F'
    }
    
    resultado = {}
    
    for nome, ticker in tickers_map.items():
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="2d")
            if len(hist) > 0:
                preco = hist['Close'].iloc[-1]
                var = 0.0
                if len(hist) > 1:
                    anterior = hist['Close'].iloc[-2]
                    var = ((preco - anterior) / anterior) * 100
                resultado[nome] = {'preco': preco, 'var': var}
            else:
                resultado[nome] = {'preco': 0.0, 'var': 0.0}
        except:
            resultado[nome] = {'preco': 0.0, 'var': 0.0}
            
    return resultado

# --- BOTÃO DE CÁLCULO ---
if st.button('Calcular Preço Justo e Atualizar 🔄'):
    with st.spinner('Baixando cotações e calculando juros...'):
        dados = pegar_dados_calculo()
        
    # Variáveis para cálculo
    ibov_spot = dados['Ibovespa (À Vista)']['preco']
    dolar_spot = dados['Dólar (À Vista)']['preco']
    
    # --- FÓRMULA DO PREÇO JUSTO (COST OF CARRY) ---
    # Futuro = Spot * (1 + Taxa)^(Dias/252)
    # Nota: O Dólar Futuro também depende do Cupom Cambial, mas usar apenas o DI 
    # dá uma aproximação muito boa para o varejo (chamado Dólar Sujo).
    
    fator_juros_ind = (1 + (taxa_di/100)) ** (du_ind / 252)
    justo_ind = ibov_spot * fator_juros_ind
    pontos_juros_ind = justo_ind - ibov_spot
    
    fator_juros_dol = (1 + (taxa_di/100)) ** (du_dol / 360) # Dólar usa base 360 às vezes, mas 252 é padrão B3. Vamos manter simples.
    # Ajuste fino: Dólar futuro é cotado em pontos de milhar (ex: 5500.00)
    justo_dol = (dolar_spot * fator_juros_dol) * 1000 
    
    
    # --- EXIBIÇÃO ---
    
    # 1. Coluna do Índice
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Mini Índice (WIN)")
        st.metric("Ibovespa (Spot)", f"{ibov_spot:,.0f} pts", f"{dados['Ibovespa (À Vista)']['var']:.2f}%")
        st.write(f"➕ Juros estimados ({du_ind} dias): **+{pontos_juros_ind:.0f} pts**")
        st.info(f"🎯 **PREÇO JUSTO: {justo_ind:,.0f} pts**")
        st.caption("Se o WIN no seu Home Broker estiver MUITO acima disso, está caro.")

    # 2. Coluna do Dólar
    with col2:
        st.subheader("💵 Mini Dólar (WDO)")
        st.metric("Dólar Comercial (Spot)", f"R$ {dolar_spot:.4f}", f"{dados['Dólar (À Vista)']['var']:.2f}%")
        st.write(f"➕ Juros estimados ({du_dol} dias)")
        st.info(f"🎯 **PREÇO JUSTO: {justo_dol:.1f} pts**")
        st.caption("Valor convertido para pontos (Ex: 5.50 = 5500 pts).")

    st.divider()

    # 3. Cenário Macro (O Código anterior simplificado)
    st.subheader("🌍 Cenário Externo")
    col_macro1, col_macro2 = st.columns(2)
    
    sp_val = dados['S&P 500 Futuro']
    oil_val = dados['Petróleo Brent']
    
    with col_macro1:
        st.metric("S&P 500 Futuro", f"{sp_val['preco']:.2f}", f"{sp_val['var']:.2f}%")
    with col_macro2:
        st.metric("Petróleo Brent", f"{oil_val['preco']:.2f}", f"{oil_val['var']:.2f}%")
        
    # Análise de Texto
    if sp_val['var'] > 0.3 and oil_val['var'] > 0:
        st.success("✅ **Sinal Externo:** Positivo. Ajuda o Preço Justo a ser atingido com facilidade.")
    elif sp_val['var'] < -0.3:
        st.error("🔻 **Sinal Externo:** Negativo. O Futuro tende a negociar ABAIXO do Justo (Desconto).")
    else:
        st.warning("⚖️ **Sinal Externo:** Neutro.")

else:
    st.info("Clique no botão para calcular.")
