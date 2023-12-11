import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

# PARTE 1 -> CONEXAO COM BANCO DE DADOS
# CRIAÇÃO DE CONEXÃO COM SERVIDOR DO BD:
def criar_conexao(usuario, senha, host, bd):
    conexao = None

    try:
        conexao = mysql.connector.connect(
            host=host,
            user=usuario,
            passwd=senha,
            database=bd
        )
        print("MySQL BD conectado com sucesso")
    except Error as e:
        print(f"Erro: {e}")

    return conexao


# CONEXÃO COM O BANCO DE DADOS DO SISTEMA APOLLO
conexao = criar_conexao('root', '', 'localhost', 'apollo')

# CRIAÇÃO DE CURSOR PARA EXECUÇÃO DE AÇÕES
cursor = conexao.cursor()

# PARTE 2 -> CONSULTAS PARA OBTENÇÃO DOS DADOS
# CONSULTA FATURAMENTO BRUTO POR MÊS
query_faturamento_bruto = """
SELECT 
    SUM(total) AS Valor_Arrecadado,
    mes,
    ano
FROM (
    SELECT 
        MONTH(DiaData) AS mes, 
        YEAR(DiaData) AS ano,
        prestacao.IDPrestacao,
        (Adicional + COALESCE(SUM(servico.preco), 0)) AS total
    FROM 
        prestacao
    JOIN 
        prestacao_servico ON prestacao.IDPrestacao = prestacao_servico.IDPrestacao
    JOIN 
        servico ON prestacao_servico.IDServico = servico.id
    JOIN 
        prestacao_data ON prestacao.IDPrestacao = prestacao_data.IDPrestacao
    JOIN 
        data ON prestacao_data.IDData = data.IDData
    GROUP BY 
        mes, prestacao.IDPrestacao
) AS subquery
GROUP BY 
    mes
ORDER BY
    ano, mes
"""
cursor.execute(query_faturamento_bruto)
resultado_faturamento_bruto = cursor.fetchall()

# QUANTIDADE DE PRESTAÇÕES REALIZADAS POR MÊS, ANO
query_prestacoes_mes = """
SELECT COUNT(prestacao.IDPrestacao) as qtd_prestacoes, MONTH(DiaData) as mes, YEAR(DiaData) as ano
FROM prestacao, prestacao_data, data
WHERE prestacao.IDPrestacao = prestacao_data.IDData 
AND prestacao_data.IDData = data.IDData
GROUP BY mes
ORDER BY ano, mes
"""
cursor.execute(query_prestacoes_mes)
resultado_query_prestacoes_mes = cursor.fetchall()

# TOTAL DE CUSTOS POR MÊS, ANO COM PRESTAÇÕES
query_total_custos = """
SELECT 
    COALESCE(SUM(total_custos), 0) AS total_custos_mes,
    mes,
    ano
FROM (
    SELECT 
        MONTH(d.DiaData) AS mes,
        YEAR(d.DiaData) AS ano,
        COALESCE(SUM(c.ValorCusto), 0) AS total_custos
    FROM 
        prestacao p
    LEFT JOIN 
        prestacao_custo pc ON p.IDPrestacao = pc.IDPrestacao
    LEFT JOIN 
        custo c ON pc.IDCusto = c.IDCusto
    LEFT JOIN 
        prestacao_data pd ON p.IDPrestacao = pd.IDPrestacao
    LEFT JOIN 
        data d ON pd.IDData = d.IDData
    GROUP BY 
        mes, ano
) AS subquery
GROUP BY 
    mes, ano
ORDER BY 
    ano, mes;

"""
cursor.execute(query_total_custos)
resultado_query_total_custos = cursor.fetchall()

# GASTOS TOTAIS COM DIÁRIAS DE FUNCIONÁRIOS EM PRESTAÇÕES
query_gastos_funcionarios = """
SELECT 
    SUM(diarias) AS total_diarias,
    mes,
    ano
FROM (
    SELECT 
        SUM(diaria) AS diarias,
        MONTH(d.DiaData) AS mes, 
        YEAR(d.DiaData) AS ano
    FROM 
        prestacao_funcionario pf
    JOIN 
        funcionario f ON pf.IDFuncionario = f.id
    JOIN 
        prestacao_data pd ON pf.IDPrestacao = pd.IDPrestacao
    JOIN 
        data d ON pd.IDData = d.IDData
    GROUP BY 
        f.id, mes, ano, d.DiaData
    HAVING 
        COUNT(DISTINCT pf.IDPrestacao) = 1
) AS subquery
GROUP BY 
    mes, ano
ORDER BY ano, mes;
"""
cursor.execute(query_gastos_funcionarios)
resultado_query_gastos_funcionarios = cursor.fetchall()

# QUANTIDADE DE SERVIÇOS E DESCRIÇÃO REALIZADOS EM PRESTAÇÕES
query_servicos_qtd = """
SELECT COUNT(prestacao_servico.IDServico) as qtd, servico.nome
FROM prestacao, prestacao_servico, servico
WHERE prestacao.IDPrestacao = prestacao_servico.IDPrestacao
AND prestacao_servico.IDServico = servico.id
GROUP BY servico.nome
ORDER BY qtd;
"""
cursor.execute(query_servicos_qtd)
resultado_query_servicos_qtd = cursor.fetchall()

# FATURAMENTO LÍQUIDO = fat_bruto - tot_custos - tot_diarias
# Criar uma lista para armazenar o faturamento líquido
faturamento_liquido = []
# Iterar sobre os resultados e calcular o faturamento líquido
for i in range(len(resultado_faturamento_bruto)):
    faturamento_bruto, mes, ano = resultado_faturamento_bruto[i]
    custos, _, _ = resultado_query_total_custos[i]
    gastos_diarias, _, _ = resultado_query_gastos_funcionarios[i]

    # Calcular o faturamento líquido
    faturamento_liquido.append((faturamento_bruto - custos - gastos_diarias, mes, ano))

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

# MAPEAMENTO DOS NOMES DOS MESES NA COLUNA MÊS
df_fat_bruto['mes'] = df_fat_bruto['mes'].map(mes_ref).astype(str)
df_fat_liq['mes'] = df_fat_liq['mes'].map(mes_ref).astype(str)
df_qtd_prest['mes'] = df_qtd_prest['mes'].map(mes_ref).astype(str)
df_gastos_func['mes']= df_gastos_func['mes'].map(mes_ref).astype(str)

# UNIÃO DOS DF DE FATURAMENTO
df_faturamento = df_fat_liq.merge(df_fat_bruto)


# Configurando layout da página
st.set_page_config(
    page_title="Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# Configurando estilo para os gráficos:
fig_style={
    'showlegend':True,
    'font': dict(family="Arial", size=16, color="black"),
    'paper_bgcolor': '#f8f8f8',
    'plot_bgcolor': '#f8f8f8'
}


# Configurando colunas de exibição:
col1, col2 = st.columns(2)

# Dropdown para seleção de ano
ano_selecionado = col1.selectbox('Selecione o Ano:', sorted(df_faturamento['ano'].unique(), reverse=True))
# Gráfico de Faturamento por Mês (Vertical de Barras)
fig_faturamento = px.bar(df_faturamento[df_faturamento['ano'] == ano_selecionado],
                         x='mes', y=['faturamento', 'faturamento liquido'],
                         labels={'value':'Faturamento (R$)', 'mes':'Mês'},
                         title=f'Faturamento (Bruto/Líquido) por Mês: Ano {ano_selecionado}',
                         height=500,
                         barmode='group',
                         orientation='v',
                         color_discrete_sequence=px.colors.qualitative.Dark24)
fig_faturamento.update_layout(
    margin=dict(l=15, t=50, b=0),
    xaxis=dict(title='Mês', tickfont=dict(size=15, color="black")),
    yaxis=dict(title='Faturamento (R$)', tickfont=dict(size=15, color="black")),
    **fig_style
)
col1.plotly_chart(fig_faturamento)

# Dropdown para seleção de ano
ano_selecionado_prestacoes = col2.selectbox('Selecione o ano para Prestações:', sorted(df_qtd_prest['ano'].unique(), reverse=True))
# Gráfico de Quantidade de Prestações por Mês (Horizontal) com Dropdown para Ano
fig_prestacoes = px.bar(df_qtd_prest[df_qtd_prest['ano'] == ano_selecionado_prestacoes],
                        y='mes', x='quantidade de prestacoes',
                        labels={'quantidade de prestacoes': 'Quantidade de Prestações', 'mes':'Mês'},
                        title=f'Quantidade de Prestações por Mês: Ano {ano_selecionado_prestacoes}',
                        color='mes',
                        height=500,
                        hover_data={'quantidade de prestacoes':':.2f'},
                        orientation='h',
                        color_discrete_sequence=px.colors.qualitative.Dark24)
fig_prestacoes.update_layout(
        margin=dict(l=15, t=50, b=0),
        xaxis=dict(title='Quantidade de Prestações',tickfont=dict(size=15, color="black")),
        yaxis=dict(title='Mês', tickfont=dict(size=15, color="black")),
        **fig_style
)
col2.plotly_chart(fig_prestacoes)

#Gráfico de Quantidade de Serviços
fig_qtd_servicos = px.pie(
    df_qtd_servicos,
    values='quantidade',
    names='servico',
    title='Quantitativo de Serviços realizados',
    color_discrete_sequence=px.colors.qualitative.Dark24
)
fig_qtd_servicos.update_layout(
    **fig_style
)
col2.plotly_chart(fig_qtd_servicos)

#Dropdown para seleção do ano
ano_selecionado_gastos_func = col1.selectbox('Selecione o Ano para Gastos com Funcionários:',
                                           sorted(df_gastos_func['ano'].unique(), reverse=True))
# Gráfico de Gastos com Funcionários por Mês (Horizontal) com Dropdown para Ano
fig_gastos_func = px.bar(df_gastos_func[df_gastos_func['ano'] == ano_selecionado_gastos_func],
                         y='total', x='mes',
                         labels={'total': 'Gastos com Funcionários'},
                         title=f'Gastos com Funcionários por Mês - Ano {ano_selecionado_gastos_func}',
                         color='mes',
                         height=500,
                         hover_data={'total':':.2f'},
                         orientation='v',
                         color_discrete_sequence=px.colors.qualitative.Dark24
                         )
fig_gastos_func.update_layout(
    margin=dict(l=15, t=50, b=0),
    xaxis=dict(title='Gastos com funcionários', tickfont=dict(size=15, color="black")),
    yaxis=dict(title='Mês', tickfont=dict(size=15, color="black")),
    **fig_style
)
col1.plotly_chart(fig_gastos_func)


