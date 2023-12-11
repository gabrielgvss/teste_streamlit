from apollo_conexao import *
import pandas as pd

# PARTE 3 -> DEFINIÇÃO DOS DADOS OBTIDOS EM DATAFRAMES

# CRIAÇÃO DE DICIONÁRIO COM NOMES PARA ASSOCIAÇÃO JUNTO AOS MESES
mes_ref = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

# DEFINIÇÃO DOS DATAFRAMES
df_fat_liq = pd.DataFrame(faturamento_liquido, columns=['faturamento liquido','mes','ano'])
df_fat_bruto = pd.DataFrame(resultado_faturamento_bruto, columns=['faturamento', 'mes','ano'])
df_qtd_prest = pd.DataFrame(resultado_query_prestacoes_mes, columns=['quantidade de prestacoes', 'mes','ano'])
df_qtd_servicos = pd.DataFrame(resultado_query_servicos_qtd, columns=['quantidade', 'servico'])
df_gastos_func = pd.DataFrame(resultado_query_gastos_funcionarios, columns=['total', 'mes','ano'])
df_tot_func = pd.DataFrame(resultado_query_total_funcionarios, columns=['total funcionarios'])
df_tot_clientes = pd.DataFrame(resultado_query_total_clientes, columns=['total clientes'])

# MAPEAMENTO DOS NOMES DOS MESES NA COLUNA MÊS
df_fat_bruto['mes'] = df_fat_bruto['mes'].map(mes_ref).astype(str)
df_fat_liq['mes'] = df_fat_liq['mes'].map(mes_ref).astype(str)
df_qtd_prest['mes'] = df_qtd_prest['mes'].map(mes_ref).astype(str)
df_gastos_func['mes']= df_gastos_func['mes'].map(mes_ref).astype(str)

# UNIÃO DOS DF DE FATURAMENTO
df_faturamento = df_fat_liq.merge(df_fat_bruto)


