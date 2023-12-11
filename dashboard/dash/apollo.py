from apollo_tratamento_dados import *
import streamlit as st
import plotly.express as px

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


