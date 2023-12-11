import mysql.connector
from mysql.connector import Error

#PARTE 1 -> CONEXAO COM BANCO DE DADOS
#CRIAÇÃO DE CONEXÃO COM SERVIDOR DO BD:
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

#CONEXÃO COM O BANCO DE DADOS DO SISTEMA APOLLO
conexao = criar_conexao('root','','localhost','apollo')

#CRIAÇÃO DE CURSOR PARA EXECUÇÃO DE AÇÕES
cursor = conexao.cursor()

#PARTE 2 -> CONSULTAS PARA OBTENÇÃO DOS DADOS
#CONSULTA FATURAMENTO BRUTO POR MÊS 
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

#QUANTIDADE DE PRESTAÇÕES REALIZADAS POR MÊS, ANO 
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

#TOTAL DE CUSTOS POR MÊS, ANO COM PRESTAÇÕES
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

#GASTOS TOTAIS COM DIÁRIAS DE FUNCIONÁRIOS EM PRESTAÇÕES
query_gastos_funcionarios="""
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

#QUANTIDADE DE SERVIÇOS E DESCRIÇÃO REALIZADOS EM PRESTAÇÕES
query_servicos_qtd="""
SELECT COUNT(prestacao_servico.IDServico) as qtd, servico.nome
FROM prestacao, prestacao_servico, servico
WHERE prestacao.IDPrestacao = prestacao_servico.IDPrestacao
AND prestacao_servico.IDServico = servico.id
GROUP BY servico.nome
ORDER BY qtd;
"""
cursor.execute(query_servicos_qtd)
resultado_query_servicos_qtd = cursor.fetchall()

#FATURAMENTO LÍQUIDO = fat_bruto - tot_custos - tot_diarias
# Criar uma lista para armazenar o faturamento líquido
faturamento_liquido = []
# Iterar sobre os resultados e calcular o faturamento líquido
for i in range(len(resultado_faturamento_bruto)):
    faturamento_bruto, mes, ano = resultado_faturamento_bruto[i]
    custos, _, _ = resultado_query_total_custos[i]
    gastos_diarias, _, _ = resultado_query_gastos_funcionarios[i]

    # Calcular o faturamento líquido
    faturamento_liquido.append((faturamento_bruto - custos - gastos_diarias, mes, ano))


# TOTAL DE FUNCIONARIOS CADASTRADOS NO SISTEMA
query_total_funcionarios = """
SELECT COUNT(*) FROM funcionario
"""
cursor.execute(query_total_funcionarios)
resultado_query_total_funcionarios = cursor.fetchall()

# TOTAL DE CLIENTES CADASTRADOS NO SISTEMA
query_total_clientes="""
SELECT COUNT(*) FROM cliente
"""
cursor.execute(query_total_clientes)
resultado_query_total_clientes = cursor.fetchall()

#







