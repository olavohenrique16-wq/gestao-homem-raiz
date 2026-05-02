import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. CONFIGURAÇÃO DE ACESSO (MUDE AQUI) ---
USUARIO_MESTRE = "olavoebruna"
SENHA_MESTRE = "Luke2026"

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Homem Raiz - Gestão", layout="wide", page_icon="🌲")

# --- 3. LÓGICA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>🌲 Homem Raiz | Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar Painel", use_container_width=True):
                if u == USUARIO_MESTRE and p == SENHA_MESTRE:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop() # Interrompe o código aqui até logar

# --- 4. CONEXÃO COM GOOGLE SHEETS ---
# COLOQUE O LINK DA SUA PLANILHA ABAIXO
url = "COLE_AQUI_O_LINK_DA_SUA_PLANILHA_DO_GOOGLE"
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        return conn.read(spreadsheet=url, usecols=[0,1,2,3,4], ttl=0)
    except:
        return pd.DataFrame(columns=["SKU", "Produto", "NCM", "Custo Fornecedor", "Custo Total"])

df_produtos = carregar_dados()

# --- 5. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetric"] { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; }
    [data-testid="stMetricValue"] { color: #1E3A8A; font-size: 1.8rem !important; }
    .dre-container { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 2px solid #1E3A8A; color: #000000 !important; }
    .dre-item { display: flex; justify-content: space-between; border-bottom: 1px dashed #cbd5e1; color: #000000 !important; font-size: 0.95rem; }
    .dre-lucro { margin-top: 10px; font-size: 1.1rem; font-weight: bold; color: #166534 !important; text-align: center; background-color: #dcfce7; border-radius: 5px; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. BARRA LATERAL ---
with st.sidebar:
    st.title("🌲 Homem Raiz")
    if st.button("Sair (Logout)"):
        st.session_state.autenticado = False
        st.rerun()
    st.markdown("---")
    st.header("⚙️ Configurações de Taxas")
    imposto_perc = st.number_input("Imposto (%)", value=4.0)
    embalagem_valor = st.number_input("Embalagem (R$)", value=2.50)
    marketing_perc = st.number_input("Ads/Mkt (%)", value=5.0)
    st.markdown("---")
    st.subheader("🎯 Margens Alvo")
    m_n1 = st.slider("Fase 1 (Lançamento)", 0, 50, 5) / 100
    m_n2 = st.slider("Fase 2 (Escala)", 0, 50, 18) / 100
    m_n3 = st.slider("Fase 3 (Elite)", 0, 50, 35) / 100

niveis_map = {"Fase 1 (Lançamento)": m_n1, "Fase 2 (Escala)": m_n2, "Fase 3 (Elite)": m_n3}

# --- 7. CADASTRO DE PRODUTOS ---
st.title("🚀 Central de Inteligência Comercial")

with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: nome_prod = st.text_input("📦 Nome do Produto")
    with c2: sku_input = st.text_input("🆔 SKU", value=f"HR-{datetime.datetime.now().strftime('%M%S')}")
    with c3: ncm_input = st.text_input("🧾 NCM", value="0000.00.00")
    
    c4, c5 = st.columns([1, 3])
    with c4: custo_compra = st.number_input("💰 Custo Compra", min_value=0.0, value=40.0)
    with c5:
        st.write(" ")
        if st.button("🚀 SALVAR E SINCRONIZAR NO GOOGLE", use_container_width=True):
            if nome_prod:
                novo_dado = pd.DataFrame({
                    "SKU": [sku_input], "Produto": [nome_prod], "NCM": [ncm_input],
                    "Custo Fornecedor": [float(custo_compra)], "Custo Total": [float(custo_compra + embalagem_valor)]
                })
                df_atualizado = pd.concat([df_produtos, novo_dado], ignore_index=True)
                conn.update(spreadsheet=url, data=df_atualizado)
                st.success("Produto salvo na planilha!")
                st.rerun()

# --- 8. ANÁLISE E DRE ---
if not df_produtos.empty:
    st.markdown("---")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        opcoes = df_produtos.apply(lambda x: f"{x['SKU']} - {x['Produto']}", axis=1).tolist()
        index_sel = st.selectbox("📂 Selecione o produto para precificar:", range(len(opcoes)), index=len(opcoes)-1, format_func=lambda x: opcoes[x])
    with col_sel2:
        fase_sel = st.selectbox("📈 Fase de Venda:", list(niveis_map.keys()))

    dados_p = df_produtos.iloc[index_sel]
    margem_alvo = niveis_map[fase_sel]

    def calcular_dre(taxa_perc, fixa):
        denominador = (1 - (taxa_perc/100) - (imposto_perc/100) - (marketing_perc/100) - margem_alvo)
        custo_tot = float(dados_p["Custo Total"])
        pv = (custo_tot + fixa) / denominador if denominador > 0 else 0
        return {"pv": pv, "mktplace": pv * (taxa_perc/100) + fixa, "imposto": pv * (imposto_perc/100), "ads": pv * (marketing_perc/100), "lucro": pv * margem_alvo}

    plataformas = [("🔵 ML Clássico", 14.0, 6.0), ("💎 ML Premium", 19.0, 6.0), ("🟠 Shopee", 20.0, 4.0), ("🎬 TikTok Shop", 15.0, 1.0)]
    
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
                    <div class="dre-lucro">💰 LUCRO LÍQUIDO: R$ {res['lucro']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("Aguardando o primeiro cadastro para exibir a análise.")