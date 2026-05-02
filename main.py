import streamlit as st
import pandas as pd
import os
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Homem Raiz - Gestão", layout="wide", page_icon="🌲")

# --- CSS PERSONALIZADO (AJUSTADO PARA MÁXIMA LEITURA) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    [data-testid="stMetricValue"] { color: #1E3A8A; font-size: 1.8rem !important; }
    
    /* ESTILO DO DRE - TEXTO ESCURO E LEITURA FÁCIL */
    .dre-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        font-size: 1rem;
        line-height: 1.8;
        border: 2px solid #1E3A8A;
        color: #000000 !important; /* Força o texto para preto puro */
    }
    .dre-item {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dashed #cbd5e1;
        color: #000000 !important;
    }
    .dre-lucro {
        margin-top: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        color: #166534 !important;
        text-align: center;
        background-color: #dcfce7;
        border-radius: 5px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    colunas = ["SKU", "Produto", "NCM", "Custo Fornecedor", "Custo Total"]
    if os.path.exists("meus_produtos.csv"):
        try:
            df = pd.read_csv("meus_produtos.csv")
            if not all(col in df.columns for col in colunas): return pd.DataFrame(columns=colunas)
            return df
        except: return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def salvar_dados(df):
    df.to_csv("meus_produtos.csv", index=False, encoding='utf-8')

df_produtos = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes de Taxas")
    with st.expander("📦 Operacional", expanded=False):
        imposto_perc = st.number_input("Imposto (%)", value=4.0)
        embalagem_valor = st.number_input("Embalagem (R$)", value=2.50)
        marketing_perc = st.number_input("Ads/Mkt (%)", value=5.0)

    with st.expander("🔵 Mercado Livre", expanded=True):
        taxa_ml_cl = st.number_input("ML Clássico (%)", value=14.0)
        taxa_ml_pr = st.number_input("ML Premium (%)", value=19.0)
        fixa_ml = st.number_input("ML Taxa Fixa", value=6.0)
        
    with st.expander("🟠 Outras Lojas", expanded=False):
        taxa_sh = st.number_input("Shopee (%)", value=20.0)
        fixa_sh = st.number_input("Shopee Fixa", value=4.0)
        taxa_tt = st.number_input("TikTok (%)", value=15.0)
        fixa_tt = st.number_input("TikTok Fixa", value=1.0)

    st.markdown("---")
    st.subheader("🎯 Margens das Fases")
    m_n1 = st.slider("Lançamento", 0, 50, 5) / 100
    m_n2 = st.slider("Escala", 0, 50, 18) / 100
    m_n3 = st.slider("Elite", 0, 50, 35) / 100

niveis_map = {"Fase 1 (Lançamento)": m_n1, "Fase 2 (Escala)": m_n2, "Fase 3 (Elite)": m_n3}

# --- TÍTULO ---
st.title("🌲 Homem Raiz | Inteligência Comercial")

# --- CADASTRO ---
with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: nome_prod = st.text_input("📦 Nome do Produto")
    with c2: sku_input = st.text_input("🆔 SKU Interno", value=f"HR-{datetime.datetime.now().strftime('%M%S')}")
    with c3: ncm_input = st.text_input("🧾 NCM", value="0000.00.00")
    c4, c5 = st.columns([1, 3])
    with c4: custo_compra = st.number_input("💰 Custo Compra", min_value=0.0, value=40.0)
    with c5:
        st.write(" ")
        if st.button("🚀 SALVAR PRODUTO", use_container_width=True):
            if nome_prod:
                novo = pd.DataFrame({"SKU":[sku_input],"Produto":[nome_prod],"NCM":[ncm_input],"Custo Fornecedor":[custo_compra],"Custo Total":[custo_compra+embalagem_valor]})
                df_produtos = pd.concat([df_produtos, novo], ignore_index=True); salvar_dados(df_produtos); st.rerun()

# --- ANÁLISE E DRE ---
if not df_produtos.empty:
    st.markdown("---")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        opcoes = df_produtos.apply(lambda x: f"{x['SKU']} - {x['Produto']}", axis=1).tolist()
        index_sel = st.selectbox("📂 Selecione o produto:", range(len(opcoes)), format_func=lambda x: opcoes[x])
    with col_sel2:
        fase_sel = st.selectbox("📈 Fase de Venda:", list(niveis_map.keys()))

    dados_p = df_produtos.iloc[index_sel]
    margem_alvo = niveis_map[fase_sel]

    st.markdown(f"""<div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <span style="background: #e0e7ff; padding: 5px 15px; border-radius: 20px; font-weight: bold; color: #4338ca;">SKU: {dados_p['SKU']}</span>
        <span style="background: #fef3c7; padding: 5px 15px; border-radius: 20px; font-weight: bold; color: #b45309;">NCM: {dados_p['NCM']}</span>
    </div>""", unsafe_allow_html=True)

    def calcular_dre(taxa_perc, fixa):
        denominador = (1 - (taxa_perc/100) - (imposto_perc/100) - (marketing_perc/100) - margem_alvo)
        pv = (dados_p["Custo Total"] + fixa) / denominador if denominador > 0 else 0
        return {
            "pv": pv,
            "mktplace": pv * (taxa_perc/100) + fixa,
            "imposto": pv * (imposto_perc/100),
            "ads": pv * (marketing_perc/100),
            "lucro": pv * margem_alvo
        }

    plataformas = [("🔵 ML Clássico", taxa_ml_cl, fixa_ml), ("💎 ML Premium", taxa_ml_pr, fixa_ml), ("🟠 Shopee", taxa_sh, fixa_sh), ("🎬 TikTok", taxa_tt, fixa_tt)]
    
    cols = st.columns(4)
    for i, (nome, taxa, fixa) in enumerate(plataformas):
        res = calcular_dre(taxa, fixa)
        with cols[i]:
            st.metric(label=nome, value=f"R$ {res['pv']:.2f}", delta=f"Lucro R$ {res['lucro']:.2f}")
            with st.expander("📄 Ver DRE Detalhado"):
                st.markdown(f"""
                <div class="dre-container">
                    <div class="dre-item"><span>📦 Custo Base:</span> <b>R$ {dados_p['Custo Total']:.2f}</b></div>
                    <div class="dre-item"><span>🏢 Comissões:</span> <b>R$ {res['mktplace']:.2f}</b></div>
                    <div class="dre-item"><span>💸 Impostos:</span> <b>R$ {res['imposto']:.2f}</b></div>
                    <div class="dre-item"><span>📢 Ads/Mkt:</span> <b>R$ {res['ads']:.2f}</b></div>
                    <div class="dre-lucro">💰 LUCRO: R$ {res['lucro']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📂 Banco de Dados"):
        st.dataframe(df_produtos, use_container_width=True)
        if st.button("🗑️ Resetar Tudo"):
            if os.path.exists("meus_produtos.csv"): os.remove("meus_produtos.csv"); st.rerun()