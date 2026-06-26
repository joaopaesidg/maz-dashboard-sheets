import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

SHEET_ID = "1Cy1hmAt8SVii762eMX5Nec-J18Zk7tEbgLgZB4tmy5Y"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1725486310"
STATUS_CONCLUIDO = ["Pago", "Contrato/Template quitado"]

def load_data():
    df = pd.read_csv(URL, header=2, dtype=str)
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")
    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Fornecedor"] = df["Fornecedor"].astype(str).str.strip()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Dias vencimento"] = pd.to_numeric(df["Dias vencimento"], errors="coerce").fillna(0)
    df["Data pgto"] = pd.to_datetime(df["Data pgto"], errors="coerce", dayfirst=True)
    df["Término Contrato"] = pd.to_datetime(df["Término Contrato"], errors="coerce", dayfirst=True)
    df_compras = df[df["Tipo"] == "Compra"].copy()
    df_pagamentos = df[df["Tipo"] == "Pagamento"].copy()
    return df_compras, df_pagamentos

def calcular_kpis(df_compras, df_pagamentos):
    orcamento_total = df_compras["Valor"].sum()
    df_pago = df_pagamentos[df_pagamentos["Status"].isin(STATUS_CONCLUIDO)]
    df_andamento = df_pagamentos[~df_pagamentos["Status"].isin(STATUS_CONCLUIDO)]
    total_pago = df_pago["Valor"].sum()
    total_andamento = df_andamento["Valor"].sum()
    saldo_disponivel = orcamento_total - total_pago - total_andamento
    perc_executado = (total_pago / orcamento_total * 100) if orcamento_total > 0 else 0
    return {
        "orcamento_total": orcamento_total,
        "total_pago": total_pago,
        "total_andamento": total_andamento,
        "saldo_disponivel": saldo_disponivel,
        "perc_executado": perc_executado,
        "contratos_vencendo": df_compras[(df_compras["Dias vencimento"] <= 30) & (df_compras["Dias vencimento"] >= 0)].shape[0],
        "contratos_vencidos": df_compras[df_compras["Dias vencimento"] < 0].shape[0],
        "fornecedores_ativos": df_andamento["Fornecedor"].nunique(),
        "parcelas_pendentes": df_andamento.shape[0],
    }

st.set_page_config(page_title="MAZ | Pagamentos", page_icon="🏛️", layout="wide")

st.title("🏛️ MAZ | Museu das Amazônias")
st.subheader("Painel de Acompanhamento de Pagamentos")
st.divider()

try:
    df_compras, df_pagamentos = load_data()
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

kpis = calcular_kpis(df_compras, df_pagamentos)

st.sidebar.header("🔍 Filtros")
fornecedores_sel = st.sidebar.multiselect("Fornecedor", sorted(df_pagamentos["Fornecedor"].dropna().unique()))
status_sel = st.sidebar.multiselect("Status", sorted(df_pagamentos["Status"].dropna().unique()))
st.sidebar.caption(f"📋 {len(df_pagamentos)} parcelas no total")

df_view = df_pagamentos.copy()
if fornecedores_sel:
    df_view = df_view[df_view["Fornecedor"].isin(fornecedores_sel)]
if status_sel:
    df_view = df_view[df_view["Status"].isin(status_sel)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("💼 Orçamento Total", f"R$ {kpis['orcamento_total']:,.0f}".replace(",", "."))
c2.metric("✅ Total Pago", f"R$ {kpis['total_pago']:,.0f}".replace(",", "."))
c3.metric("🔄 Em Andamento", f"R$ {kpis['total_andamento']:,.0f}".replace(",", "."))
c4.metric("💰 Saldo Disponível", f"R$ {kpis['saldo_disponivel']:,.0f}".replace(",", "."), delta=f"{kpis['perc_executado']:.1f}% executado")

st.divider()
c5, c6, c7, c8 = st.columns(4)
c5.metric("📊 % Executado", f"{kpis['perc_executado']:.1f}%")
c6.metric("⚠️ Vencem em 30d", kpis['contratos_vencendo'])
c7.metric("🔴 Contratos Vencidos", kpis['contratos_vencidos'])
c8.metric("📋 Parcelas Pendentes", kpis['parcelas_pendentes'])

st.divider()
col_esq, col_dir = st.columns([3, 2])

mapa_cores = {
    "Pago": "#2ecc71", "Contrato/Template quitado": "#27ae60",
    "Aprovado": "#3498db", "Em aprovação": "#f1c40f",
    "NF em análise": "#f39c12", "Aguardando emissão de NF/DANFE": "#e67e22",
    "Aguardando Requisição de Pagamento": "#e67e22", "Aguardando informações": "#e67e22",
    "Atendimento Compras/Financeiro": "#e74c3c", "Contrato/Template em aberto": "#c0392b",
    "Contrato/Template vencido": "#922b21",
}

with col_esq:
    st.subheader("📊 Gargalos por Status (R$)")
    df_status = df_view.groupby("Status")["Valor"].sum().reset_index().sort_values("Valor", ascending=True)
    fig1 = px.bar(df_status, x="Valor", y="Status", orientation="h",
                  text=df_status["Valor"].apply(lambda v: f"R$ {v:,.0f}".replace(",", ".")),
                  color="Status", color_discrete_map=mapa_cores)
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig1, use_container_width=True)

with col_dir:
    st.subheader("🥧 Execução Orçamentária")
    fig2 = go.Figure(go.Pie(
        labels=["Pago", "Em Andamento", "Saldo"],
        values=[max(kpis["total_pago"], 0), max(kpis["total_andamento"], 0), max(kpis["saldo_disponivel"], 0)],
        hole=0.45, marker_colors=["#2ecc71", "#f39c12", "#95a5a6"], textinfo="label+percent"))
    fig2.update_layout(height=420)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("🏢 Volume por Fornecedor")
df_forn = df_view.groupby("Fornecedor")["Valor"].sum().reset_index().sort_values("Valor", ascending=False).head(15)
fig3 = px.bar(df_forn, x="Fornecedor", y="Valor",
              text=df_forn["Valor"].apply(lambda v: f"R$ {v:,.0f}".replace(",", ".")),
              color="Valor", color_continuous_scale="Blues")
fig3.update_traces(textposition="outside")
fig3.update_layout(showlegend=False, height=380)
st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("📋 Detalhamento de Parcelas")
colunas = ["Fornecedor", "Descritivo", "Valor", "Status", "Data pgto", "Doc Fiscal", "Dias vencimento", "Observações"]
colunas_existentes = [c for c in colunas if c in df_view.columns]
st.dataframe(df_view[colunas_existentes], use_container_width=True, height=400)

st.divider()
st.caption("IDG — Instituto de Desenvolvimento e Gestão | MAZ | Museu das Amazônias")
