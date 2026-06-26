STATUS_CONCLUIDO = ["Pago", "Contrato/Template quitado"]

def calcular_kpis(df_compras, df_pagamentos):
    orcamento_total = df_compras["Valor"].sum()

    df_pago = df_pagamentos[df_pagamentos["Status"].isin(STATUS_CONCLUIDO)]
    df_andamento = df_pagamentos[~df_pagamentos["Status"].isin(STATUS_CONCLUIDO)]

    total_pago = df_pago["Valor"].sum()
    total_andamento = df_andamento["Valor"].sum()
    saldo_disponivel = orcamento_total - total_pago - total_andamento
    perc_executado = (total_pago / orcamento_total * 100) if orcamento_total > 0 else 0

    contratos_vencendo = df_compras[
        (df_compras["Dias vencimento"] <= 30) & (df_compras["Dias vencimento"] >= 0)
    ].shape[0]

    contratos_vencidos = df_compras[df_compras["Dias vencimento"] < 0].shape[0]

    return {
        "orcamento_total": orcamento_total,
        "total_pago": total_pago,
        "total_andamento": total_andamento,
        "saldo_disponivel": saldo_disponivel,
        "perc_executado": perc_executado,
        "contratos_vencendo": contratos_vencendo,
        "contratos_vencidos": contratos_vencidos,
        "fornecedores_ativos": df_andamento["Fornecedor"].nunique(),
        "parcelas_pendentes": df_andamento.shape[0],
    }
