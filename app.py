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
        # AQUI ESTAVA O ERRO EM ALGUNS COMPUTADORES:
        st.metric(
            label="Ibov à Vista", 
            value=f"{ibov:,.0f}", 
            delta=f"{dados['Ibov Spot']['var']:.2f}%"
        )
        st.info(f"🎯 **Preço Justo: {justo_ind:,.0f}** (+{diff_ind:.0f} pts juros)")

    # Cálculo Dólar
    dolar = dados['Dólar Spot']['preco']
    justo_dol = (dolar * ((1 + taxa_di/100)**(du_dol/360))) * 1000
    
    with col_j2:
        st.subheader("💵 Mini Dólar (WDO)")
        st.metric(
            label="Dólar Comercial", 
            value=f"R$ {dolar:.4f}", 
            delta=f"{dados['Dólar Spot']['var']:.2f}%"
        )
        st.info(f"🎯 **Preço Justo: {justo_dol:.1f} pts**")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: RADAR MACRO GLOBAL (CORRIGIDO)
    # ==========================================
    st.header("2️⃣ Radar Macro Global")
    
    # Linha 1
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        item = dados['S&P 500 Fut']
        st.metric(label="🇺🇸 S&P 500", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")
        
    with c2:
        item = dados['Nasdaq Fut']
        st.metric(label="💻 Nasdaq", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")

    with c3:
        item = dados['EWZ (Brasil)']
        st.metric(label="🇧🇷 EWZ (NY)", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")
        
    with c4:
        item = dados['Vale ADR']
        st.metric(label="⛏️ Vale ADR", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")

    # Linha 2
    c5, c6, c7, c8 = st.columns(4)
    
    with c5:
        item = dados['Petróleo Brent']
        st.metric(label="🛢️ Petróleo", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")
        
    with c6:
        item = dados['Ouro']
        st.metric(label="🥇 Ouro", value=f"{item['preco']:.2f}", delta=f"{item['var']:.2f}%")
