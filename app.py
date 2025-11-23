import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Master Radar B3", layout="wide")

st.title("🇧🇷 Master Radar B3: Justo & Macro")
st.markdown("Cálculo de Preço Justo + Painel Global Completo em Tempo Real (Yahoo).")
st.markdown("---")

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("⚙️ Configuração Juros")
taxa_di = st.sidebar.number_input("Taxa DI/Selic Anual (%)", value=12.25, step=0.25)
st.sidebar.caption("Usado para calcular o Preço Justo.")

# Função de Dias Úteis (Automática)
def get_dias_uteis():
    hoje = date.today()
    # Lógica simplificada Índice (Vencimento meses pares, dia 15)
    mes = hoje.month
    ano = hoje.year
    prox_mes = mes + (mes % 2)
    if mes % 2 == 0: prox_mes += 2
    if prox_mes > 12:
        prox_mes -= 12
        ano += 1
    venc_ind = date(ano, prox_mes, 15)
    du_ind = int((venc_ind - hoje).days * (5/7))
    
    # Lógica simplificada Dólar (Dia 1 mês seguinte)
    mes_dol = hoje.month + 1
    ano_dol = hoje.year
    if mes_dol > 12: mes_dol=1; ano_dol+=1
    venc_dol = date(ano_dol, mes_dol, 1)
    du_dol = int((venc_dol - hoje).days * (5/7))
    
    return max(0, du_ind), max(0, du_dol)

du_ind, du_dol = get_dias_uteis()
st.sidebar.markdown(f"**Dias Úteis Est.:** IND ({du_ind}) | DOL ({du_dol})")


# --- FUNÇÃO DE DADOS (AGORA COMPLETA) ---
def pegar_dados_full():
    # Lista completa de Tickers
    tickers_map = {
        'Ibov Spot': '^BVSP',
        'Dólar Spot': 'BRL=X',
        'S&P 500 Fut': 'ES=F',
        'Nasdaq Fut': 'NQ=F',      # VOLTOU
        'Petróleo Brent': 'BZ=F',
        'Ouro': 'GC=F',            # VOLTOU
        'EWZ (Brasil)': 'EWZ',     # VOLTOU
        'Vale ADR': 'VALE'         # VOLTOU
    }
    
    dados = {}
    texto_status = ""
    
    for nome, ticker in tickers_map.items():
        try:
            acao = yf.Ticker(ticker)
            hist = acao.history(period="5d") # Pega 5 dias para garantir
            
            if len(hist) > 0:
                preco_atual = hist['Close'].iloc[-1]
                # Pega fechamento anterior para variação
                anterior = hist['Close'].iloc[-2] if len(hist) > 1 else preco_atual
                variacao = ((preco_atual - anterior) / anterior) * 100
                
                dados[nome] = {'preco': preco_atual, 'var': variacao}
            else:
                dados[nome] = {'preco': 0.0, 'var': 0.0}
        except:
            dados[nome] = {'preco': 0.0, 'var': 0.0}
            
    return dados

# --- BOTÃO DE ATUALIZAÇÃO ---
if st.button('Atualizar Painel Completo 🔄'):
    with st.spinner('Analisando mercados globais...'):
        dados = pegar_dados_full()

    # ==========================================
    # SEÇÃO 1: CÁLCULO DE PREÇO JUSTO (Math)
    # ==========================================
    st.header("1️⃣ Preço Justo (Fair Value)")
    col_j1, col_j2 = st.columns(2)

    # Cálculo Índice
    ibov = dados['Ibov Spot']['preco']
    justo_ind = ibov * ((1 + taxa_di/100)**(du_ind/252))
    diff_ind = justo_ind - ibov
    
    with col_j1:
        st.subheader("📊 Mini Índice (WIN)")
        st.metric("Ibov à Vista", f"{ibov:,.0f}", f"{dados['Ibov Spot']['var']:.2f}%")
        st.info(f"🎯 **Preço Justo: {justo_ind:,.0f}** (+{diff_ind:.0f} pts juros)")

    # Cálculo Dólar
    dolar = dados['Dólar Spot']['preco']
    justo_dol = (dolar * ((1 + taxa_di/100)**(du_dol/360))) * 1000
    
    with col_j2:
        st.subheader("💵 Mini Dólar (WDO)")
        st.metric("Dólar Comercial", f"R$ {dolar:.4f}", f"{dados['Dólar Spot']['var']:.2f}%")
        st.info(f"🎯 **Preço Justo: {justo_dol:.1f} pts**")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: RADAR MACRO GLOBAL (Tudo de volta)
    # ==========================================
    st.header("2️⃣ Radar Macro Global")
    
    # Linha 1: Estados Unidos (Risco)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # S&P 500
        item = dados['S&P 500 Fut']
        st.metric("🇺🇸 S&P 500", f"{item['preco']:.2f}", f"{item['var']:.2f}%")
        
    with c2:
        # Nasdaq
        item = dados['Nasdaq Fut']
        st.metric("💻 Nasdaq", f"{item['preco']:.2f}", f"{item['var']:.2f}%")

    with c3:
        # EWZ
        item = dados['EWZ (Brasil)']
        st.metric("🇧🇷 EWZ (NY)", f"{item['preco']:.2f}", f"{item['var']:.2f}%")
        
    with c4:
        # Vale ADR
        item = dados['Vale ADR']
        st.metric("⛏️ Vale ADR", f"{item['preco']:.2f}", f"{item['var']:.2f}%")

    # Linha 2: Commodities & Proteção
    c5, c6, c7, c8 = st.columns(4)
    
    with c5:
        # Petróleo
        item = dados['Petróleo Brent']
        st.metric
