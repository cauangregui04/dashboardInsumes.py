from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
# import from folders/theme changer
from app import *
from dash_bootstrap_templates import ThemeSwitchAIO
import datetime
from bcb import currency
from bcb import sgs
import sidrapy
from plotly.graph_objs import *


##pegando dados
#série selic

hoje = datetime.datetime.now()
um_ano_atras = hoje - datetime.timedelta(days = 365)

selic = sgs.get({'selic':432}, start = um_ano_atras)

# Importa as variações do IPCA
ipca_raw = sidrapy.get_table(table_code = '1737',
                            territorial_level = '1',
                            ibge_territorial_code = 'all',
                            variable = '63,69,2263,2264,2265',
                            period = 'last%20472')

# Realiza a limpeza e manipulação da tabela
hoje = datetime.datetime.now()
um_ano_atras = hoje - datetime.timedelta(days = 365)

ipca =  (
    ipca_raw
    .loc[1:,['V', 'D2C', 'D3N']]
    .rename(columns = {'V': 'value',
                    'D2C': 'date',
                    'D3N': 'variable'}
            )
    .assign(variable = lambda x: x['variable'].replace({'IPCA - Variação mensal' : 'Var. mensal (%)',
                                                        'IPCA - Variação acumulada no ano': 'Var. acumulada no ano (%)', 
                                                        'IPCA - Variação acumulada em 3 meses' : 'Var. MM3M (%)',
                                                        'IPCA - Variação acumulada em 6 meses': 'Var. MM6M (%)',
                                                        'IPCA - Variação acumulada em 12 meses' : 'Var. MM12M (%)'}),
            date  = lambda x: pd.to_datetime(x['date'],
                                            format = "%Y%m"),
            value = lambda x: x['value'].astype(float)
        )
    .pipe(lambda x: x.loc[x.date > "2022/04/10"]
    )
        )
ipca_12m = (   
            ipca
            .pipe(lambda x: x.loc[x.variable == 'Var. MM12M (%)'])
)

ipca_12mA = ipca_12m['value']

ipca_12mA = ipca_12mA.iloc[-1]

#Dolar
dados_mercado = currency.get(['USD'],
                    start=um_ano_atras,
                    end=hoje,
                    side='ask')

dados_fechamento = dados_mercado['USD']
dados_fechamento = dados_fechamento.dropna()

dados_fechamento_mensal = dados_fechamento.resample("M").last()
dados_fechamento_anual = dados_fechamento.resample("Y").last()
dados_fechamento_dia = dados_fechamento.resample("D").last()

dados_selic_mensal = selic.resample("M").last()
dados_selic_anual = selic.resample("Y").last()
dados_selic_dia = selic.resample("D").last()

retorno_ano_dolar = dados_fechamento_anual.pct_change().dropna()
retorno_mes_dolar = dados_fechamento_mensal.pct_change().dropna()
retorno_dia_dolar = dados_fechamento_dia.pct_change().dropna()

retorno_ano_selic = dados_selic_anual.pct_change().dropna()
retorno_mes_selic = dados_selic_mensal.pct_change().dropna()
retorno_dia_selic = dados_selic_dia.pct_change().dropna()

dados_selic_anual = dados_selic_anual.iloc[-1]

retorno_dia_dolar = retorno_dia_dolar.iloc[-1]

retorno_mes_dolar = retorno_mes_dolar.iloc[-1]

retorno_ano_dolar = retorno_ano_dolar.iloc[-1]

retorno_dia_dolar = round(retorno_dia_dolar * 100, 2)
retorno_mes_dolar = round(retorno_mes_dolar * 100, 2)
retorno_ano_dolar = round(retorno_ano_dolar * 100, 2)

retorno_ano_selic = round(retorno_ano_selic * 100, 2)
retorno_mes_selic = round(retorno_mes_selic * 100, 2)
retorno_dia_selic = round(retorno_dia_selic * 100, 2)

# ========== Styles ============ #
tab_card = {'height': '100%','width': '100%', 'align-items': 'center'}


config_graph={"displayModeBar": False, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY

selic = pd.DataFrame(selic, columns=['Date', 'selic'])

# ===== Reading n cleaning File ====== #

df = pd.read_excel(r"C:\Users\cvivan\Documents\Projeto-envio-mensal-gestor\FORNECEDORES.xlsx",sheet_name= "FOR")
df = pd.DataFrame(df, columns=['FORNECEDOR', 'CATEGORIA', 'V. TOTAL', 'DATE'])

df_cru = df.copy()


df.loc[ df['DATE'] == 'jan-23', 'DATE'] = '01/23'
df.loc[ df['DATE'] == 'fev-23', 'DATE'] = '02/23'
df.loc[ df['DATE'] == 'mar-23', 'DATE'] = '03/23'
df.loc[ df['DATE'] == 'abr-23', 'DATE'] = '04/23'

df['V. TOTAL'] = df['V. TOTAL'].astype(float)

layout = Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

#Comparacao mês anterior card
df7 = df.groupby(['DATE'])["V. TOTAL"].sum()
df7 = df7.reset_index()

fig37 = go.Figure(layout=layout)
fig37.add_trace(go.Indicator(mode='number+delta',
            title = {"text": f"<span style='font-size:150%'>{df7['DATE'].iloc[-1]} - Gastos do mês</span><br><span style='font-size:70%'>Em gastos - em relacao ao mês anterior</span><br>"},
            value = df7['V. TOTAL'].iloc[-1],
            number = {'prefix': "R$"},
            delta = {'relative': True, 'valueformat': '.1%', 'reference': df7['V. TOTAL'].iloc[-2]}))
fig37.update_layout(width=300, height=300, font_size=(15), title_pad_b=10, margin_l=80)

dados_fechamento_mensal = pd.DataFrame(dados_fechamento_mensal, columns=['Date','USD'])

df1 = df.groupby(['FORNECEDOR', 'DATE'])['V. TOTAL'].sum().reset_index()
df1_group = df.groupby('DATE')['V. TOTAL'].sum().reset_index()

selic = pd.DataFrame(selic, columns=['selic'])

ipca_12m = pd.DataFrame(ipca_12m, columns=['value', 'date'])

opcoes_for = list(df['FORNECEDOR'].unique())
opcoes_for.append("Todos os fornecedores")


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    # dcc.Store(id='dataset', data=df_store),

    # Layout
    # Row 1

    dbc.Row([
        dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                        html.Legend(''),
                        html.H1('')
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Col([
                                html.H5("Bem-vindo"),
                                html.H6("RNI"),
                                ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])
                            ]),
                            dbc.Col([
                                html.Img(src=r'assets/rni.png', width=100, style={'padding-left': '10px'}),
                            ])
                        ], style={'display': 'flex', 'align-items': 'center'})
                    ], class_name='teste')]),
                        dbc.Col([
                                html.Div([
                                html.Legend(''),
                                html.H1('')
                                ]),
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='fig3', className='dbc', config=config_graph)
                                    ], style={'align-items': 'center'})
                                ], style={'height': '140px', 'align-items': 'center'})
                            ], lg=3, sm=3),
                            dbc.Col([
                                html.Div([
                                html.Legend(''),
                                html.H1('')
                                ]),
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='fig2', className='dbc', config=config_graph)
                                    ], style={'align-items': 'center'})
                                ], style={'height': '140px', 'align-items': 'center'})
                            ], lg=3, sm=3),
                            dbc.Col([
                                html.Div([
                                html.Legend(''),
                                html.H1('')
                                ]),
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(id='fig4', className='dbc', config=config_graph)
                                    ], style={'align-items': 'center'})
                                ], style={'height': '140px', 'align-items': 'center'})
                            ], lg=3, sm=3)
                ]),
            ]),
    ]),
    html.Div([
        html.Legend(''),
        html.H1('')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        dcc.Dropdown(opcoes_for, value='Todos os fornecedores', id='lista_fornecedor', className='dropdown-class-2')
                    ]),
                    dcc.Graph(id='fig7', className='dbc', config=config_graph)
                ])
            ])
        ],style=tab_card),
    ]),
])


#SELIC CARD

@app.callback(
    Output('fig2', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def fig2(toggle):
    template = template_theme1 if toggle else template_theme2

    fig2 = go.Figure(layout=layout)
    fig2.add_trace(go.Indicator(mode='number+delta',
                title = {"text": f"<span style='font-size:150%'>Selic</span><br><span style='font-size:70%'>Taxa atual (BCB)</span><br>"},
                value = selic['selic'].iloc[-1],
                number = {'prefix': "%"},
                delta = {'relative': True, 'valueformat': '.1%', 'reference': selic['selic'].iloc[-2]}))
    fig2.update_layout(width=240, height=205, font_size=(2), margin_t=55, margin_l=70)

    fig2.update_layout(template=template)

    return fig2

#INFLACAO CARD

@app.callback(
    Output('fig3', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def fig3(toggle):
    template = template_theme1 if toggle else template_theme2

    fig3 = go.Figure(layout=layout)
    fig3.add_trace(go.Indicator(mode='number+delta',
                title = {"text": f"<span style='font-size:150%'>IPCA</span><br><span style='font-size:70%'>Acumulado de 12 meses</span><br>"},
                value = ipca_12m['value'].iloc[-1],
                number = {'prefix': "%"},
                delta = {'relative': True, 'valueformat': '.1%', 'reference': ipca_12m['value'].iloc[-2]}))
    fig3.update_layout(width=230, height=205, font_size=(2), margin_t=55, margin_l=70)
    
    fig3.update_layout(template=template)

    return fig3

#DOLAR CARD

@app.callback(
    Output('fig4', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def fig4(toggle):
    template = template_theme1 if toggle else template_theme2

    
    fig4 = go.Figure(layout=layout)
    fig4.add_trace(go.Indicator(mode='number+delta',
                title = {"text": f"<span style='font-size:150%'>Dolar</span><br><span style='font-size:70%'>Retorno no mês</span><br>"},
                value = dados_fechamento_mensal['USD'].iloc[-1],
                number = {'prefix': "R$"},
                delta = {'relative': True, 'valueformat': '.1%', 'reference': dados_fechamento_mensal['USD'].iloc[-2]}))
    fig4.update_layout(width=230, height=205, font_size=(2), margin_t=55, margin_l=70),
        
    fig4.update_layout(template=template)

    return fig4

@app.callback(
    Output('fig7', 'figure'),
    Input('lista_fornecedor', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def fig7(value, toggle):
    template = template_theme1 if toggle else template_theme2
    
    if value == "Todos os fornecedores":
        fig7 = px.line(df1, y='V. TOTAL', x='DATE', color='FORNECEDOR', markers=True, labels={'V. TOTAL': 'VALOR   EM   R$', 'DATE': ''});
        fig7.add_trace(go.Scatter(y=df1_group['V. TOTAL'], x=df1_group['DATE'], mode='lines+markers', fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)', name='Total de despesa'));
        fig7.update_layout(template=template)
    else:
        tabela_filtrada = df.loc[df['FORNECEDOR']==value, :]
        tabela_grupo = df.groupby([df['DATE'].where(df['FORNECEDOR'] == value)])['V. TOTAL'].sum().reset_index()
        fig7 = px.line(tabela_filtrada, y='V. TOTAL', x='DATE', color='CATEGORIA', markers=True, labels={'V. TOTAL': 'VALOR   EM   R$', 'DATE': ''});
        fig7.add_trace(go.Scatter(y=tabela_grupo['V. TOTAL'], x=tabela_grupo['DATE'], mode='lines+markers', fill='tozeroy', fillcolor='rgba(140, 150, 0, 0.1)', name='Total de despesa'));
        fig7.update_layout(template=template)
    return fig7


# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
