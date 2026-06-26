import pandas as pd

SHEET_ID = "1Cy1hmAt8SVii762eMX5Nec-J18Zk7tEbgLgZB4tmy5Y"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_data():
    df = pd.read_csv(URL, header=2, dtype=str)

    # Normaliza nomes das colunas (remove espaços invisíveis)
    df.columns = df.columns.str.strip()

    # Remove linhas completamente vazias
    df = df.dropna(how="all")

    # Padroniza os campos de texto
    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Fornecedor"] = df["Fornecedor"].astype(str).str.strip()

    # Converte campos numéricos e de data
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Dias vencimento"] = pd.to_numeric(df["Dias vencimento"], errors="coerce").fillna(0)
    df["Data pgto"] = pd.to_datetime(df["Data pgto"], errors="coerce", dayfirst=True)
    df["Término Contrato"] = pd.to_datetime(df["Término Contrato"], errors="coerce", dayfirst=True)

    # Separação crucial: Compra = orçamento | Pagamento = fluxo de caixa
    df_compras = df[df["Tipo"] == "Compra"].copy()
    df_pagamentos = df[df["Tipo"] == "Pagamento"].copy()

    return df_compras, df_pagamentos
