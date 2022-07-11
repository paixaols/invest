# -*- coding: utf-8 -*-
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

from matplotlib import cm
from matplotlib.dates import DateFormatter, MonthLocator

# @st.cache
def load_wallet():
    url = 'http://127.0.0.1:5000/load-wallet'
    data = {'year':2022, 'month':6}
    data = json.dumps(data)
    header = {'Content-type': 'application/json'}
    r = requests.post(url, data=data, headers=header)

    df = pd.DataFrame(r.json(), columns = r.json()[0].keys())
    year = df.loc[0, 'year']
    month = df.loc[0, 'month']
    w = df.loc[0, 'wallet']
    w = pd.DataFrame(w)
    # Exchange rate
    w['value_brl'] = w['value']*w['currency_rate']
    # Wallet date
    w['month'] = f'{year}-{month}'
    w['month_datetime'] = w['month'].apply(lambda x: pd.to_datetime(x, format = '%Y-%m'))
    # Make expire naive datetime objects
    w['expire'] = w['expire'].apply(lambda x: pd.to_datetime(x.split('T')[0]))
    return w

# =============================================================================
# Settings
# =============================================================================
main_palette = 'winter_r'
main_palette = 'autumn'
st.set_page_config(layout = 'wide')

# TODO: explicitly close figures

# =============================================================================
# Helper functions
# =============================================================================
def get_sns_colors(palette, n):
    cmap = cm.get_cmap(palette)
    c = np.linspace(0, 1, n+4)
    c = c[2:-2]
    return cmap(c)

def pieplot(x, labels, ax, palette = 'winter_r'):
    explode = [0.03]*len(x)
    ax.pie(x, labels = labels, autopct = '%.1f%%', explode = explode, 
            shadow = False, wedgeprops = {'edgecolor': 'black'}, 
            startangle = 90, counterclock = False, 
            colors = get_sns_colors(palette, len(x)))

def barplot(x, y, ax, palette = 'winter_r', rotation = 0, align = 'center', ylabel = '', y2 = False, **kwargs):
    sns.barplot(x = x, y = y, ax = ax, palette = palette, **kwargs)
    ax.tick_params(axis = 'x', rotation = rotation)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment(align)
    ax.set_xlabel('')
    ax.set_ylabel(ylabel)
    if y2:# Right axis with percentages
        total = sum(y)
        abs2pct = lambda x: 100*x/total
        pct2abs = lambda x: total*x/100
        ax2 = ax.secondary_yaxis('right', functions = (abs2pct, pct2abs))
        ax2.set_ylabel('%')
        for rect in ax.patches:
            ax.text(rect.get_x(), rect.get_height(), 
                    '%.1f%%'%abs2pct(rect.get_height()), 
                    weight = 'bold', 
                    rotation = rotation)
    else:
        for rect in ax.patches:
            ax.text(rect.get_x(), rect.get_height(), 
                    '%.2f'%rect.get_height(), 
                    weight = 'bold', 
                    rotation = rotation)

# =============================================================================
# Dashboard panels
# =============================================================================
def general_view(df):
    # Filter time window
    time_window = st.sidebar.radio('Período', ['12 meses', 'No ano', 'Máx'])
    now = datetime.datetime.now()
    y = now.year
    if time_window == 'No ano':
        start_date = datetime.datetime(year=y, month=1, day=1)
        df = df.loc[df['month_datetime'] >= start_date]
    if time_window == '12 meses':
        y -= 1
        start_date = datetime.datetime(year=y, month=now.month, day=1)
        df = df.loc[df['month_datetime'] >= start_date]
    
    st.header('Visão geral')
    st.subheader('Histórico')
    
    # Change
    aux = df[['month_datetime', 'value_brl']].groupby('month_datetime').sum().reset_index()
    initial = aux.iloc[0, 1]
    final = aux.iloc[-1, 1]
    change_percent = 100 * (final-initial) / initial
    st.metric('Variação', 
              'R$ {:,.2f}'.format(final-initial), 
              '{:.1f}%'.format(change_percent))
    
    # Fill area
    colors = get_sns_colors(main_palette, 2)
    
    fig, axs = plt.subplots(ncols = 2, figsize = (10, 3))
    axs[0].plot(aux['month_datetime'], aux['value_brl']/1000, '-o', color = colors[0])
    axs[0].fill_between(aux['month_datetime'], aux['value_brl']/1000, 
                        y2 = aux['value_brl'].min()/1000, 
                        alpha = 0.5, color = colors[1])
    axs[0].xaxis.set_major_locator(MonthLocator())
    axs[0].xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.setp(axs[0].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    plt.setp(axs[1].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    axs[0].set_ylabel('R$ mil')
    
    # Stackplot
    aux = df[['month_datetime', 'value_brl', 'class']].groupby(['month_datetime', 'class']).sum().reset_index()
    aux2 = aux.pivot(index='month_datetime', columns='class', values = 'value_brl')
    aux2 = aux2.apply(lambda x: 100*x/sum(x), axis=1)
    
    aux2.plot(kind='area', stacked=True,
              ax=axs[1],
              color=get_sns_colors(main_palette, aux2.shape[1]),
              ylim=(0,100)
    )
    # axs[1].xaxis.set_major_locator(MonthLocator())
    # axs[1].xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    axs[1].set_ylabel('%')
    axs[1].legend()
    
    st.pyplot(fig)
    
    # Valores atuais
    st.subheader('Atual')
    
    fig, axs = plt.subplots(ncols = 2, figsize = (10, 3))
    
    # Current month - by location
    df = df.loc[df['month_datetime'] == df['month_datetime'].max()]
    aux = df[['market', 'value_brl']].groupby('market').sum().reset_index()
    aux.sort_values('value_brl', ascending=False, inplace=True)
    barplot(aux['market'], aux['value_brl']/1000, axs[0], palette = main_palette, 
            rotation = 0, align = 'center', ylabel = 'R$ mil', y2 = True)
    
    # Current month - by class
    aux = df[['class', 'value_brl']].groupby('class').sum().reset_index()
    aux.sort_values('value_brl', ascending=False, inplace=True)
    barplot(aux['class'], aux['value_brl']/1000, axs[1], palette = main_palette, 
            rotation = 0, align = 'center', ylabel = 'R$ mil', y2 = True)
    
    fig.tight_layout()
    st.pyplot(fig)

def view_rf(df):
    st.header('Renda variável')
    
    # Class overview
    st.subheader('Visão geral')
    df_current = df.loc[df['mês_datetime'] == df['mês_datetime'].max()]
    fig, axs = plt.subplots(ncols = 2, figsize = (10, 3))
    
    aux = df_current[['valor_real', 'tipo']].groupby('tipo').sum().reset_index()
    aux.sort_values('valor_real', ascending=False, inplace=True)
    pieplot(aux['valor_real'], aux['tipo'], axs[0], palette=main_palette)
    barplot(aux['tipo'], aux['valor_real']/1000, axs[1], palette=main_palette, 
            rotation=30, align='center', ylabel='R$ mil', y2=True)
    
    st.pyplot(fig)
    
    # Vencimento
    st.subheader('Datas de vencimento')
    
    aux1 = df_current.groupby(['tipo', 'vencimento']).sum().reset_index()
    aux1['vencimento'] = aux1['vencimento'].apply(lambda x: x.year)
    aux1 = aux1[['tipo', 'vencimento', 'valor_real']].groupby(['tipo', 'vencimento']).sum().reset_index()
    aux1.sort_values('valor_real', inplace = True, ascending = False)
    
    # Fill empty years
    yr_range = list(range(aux1['vencimento'].min(), aux1['vencimento'].max()))
    fill_vencimento = np.setdiff1d(yr_range, aux1['vencimento'].to_list())
    aux1 = aux1.append(pd.DataFrame({'tipo': ['IPCA']*len(fill_vencimento), 
                                     'vencimento': fill_vencimento, 
                                     'valor': [0]*len(fill_vencimento)}))
    
    aux2 = aux1.groupby('vencimento').sum().reset_index()
    new_index = pd.Index(range(aux2['vencimento'].min(), aux2['vencimento'].max()+1), name = 'vencimento')
    aux2 = aux2.set_index('vencimento').reindex(new_index).reset_index()
    aux2['valor_real'].fillna(0, inplace = True)
    
    # Plot
    fig, ax = plt.subplots(figsize = (10, 3))
    barplot(aux2['vencimento'], aux2['valor_real']/1000, ax, 
            palette = main_palette, alpha = 0.2, rotation = 45)
    sns.barplot(x = aux1['vencimento'], y = aux1['valor_real']/1000, data = aux1, 
                ax = ax, hue = 'tipo', palette = main_palette)
    ax.set_ylabel('BRL mil')
    ax.legend(loc = 'upper right')
    st.pyplot(fig)

def view_rv(df):
    st.header('Renda variável')
    
    # Class overview
    st.subheader('Visão geral')
    df_current = df.loc[df['mês_datetime'] == df['mês_datetime'].max()]
    fig, axs = plt.subplots(ncols = 2, figsize = (10, 3))
    
    aux = df_current[['valor_real', 'tipo']].groupby('tipo').sum().reset_index()
    aux.sort_values('valor_real', ascending=False, inplace=True)
    pieplot(aux['valor_real'], aux['tipo'], axs[0], palette=main_palette)
    barplot(aux['tipo'], aux['valor_real']/1000, axs[1], palette=main_palette, 
            rotation=0, align='center', ylabel='R$ mil', y2=True)
    
    st.pyplot(fig)
    
    # Individual asset type
    type_list = df_current['tipo'].unique()
    asset_type = st.sidebar.radio('Categorias', type_list)
    df_current = df_current.loc[df_current['tipo'] == asset_type]
    currency_code = df_current['moeda'].iloc[0]
    
    # Type overview
    st.subheader(asset_type)
    
    # Change
    aux = df_current[df_current['tipo'] == asset_type]
    initial = aux['custo'].sum()
    final = aux['valor'].sum()
    change_percent = 100 * (final-initial) / initial
    st.metric('Custo: {:,.2f} {}'.format(initial, currency_code), 
              '{:,.2f} {}'.format(final, currency_code), 
              '{:.1f}%'.format(change_percent))
    
    # Table and plot
    aux = df_current[['ativo', 'custo', 'valor']].groupby('ativo').sum().reset_index()
    aux['var%'] = aux.apply(lambda x: 100*(x['valor']/x['custo']-1), axis=1)
    
    c1, c2 = st.columns(2)
    aux.sort_values('var%', ascending=False, inplace=True)
    c1.write(aux.style.format(formatter = {('custo'): '{:,.2f}', 
                                           ('valor'): '{:,.2f}', 
                                           ('var%'): '{:,.1f}%'}))
    fig, ax = plt.subplots(figsize = (5, 4))
    aux.sort_values('valor', ascending=False, inplace=True)
    barplot(aux['ativo'], aux['valor']/1000, ax, palette=main_palette, 
            rotation=30, align='center', ylabel='Mil '+currency_code, y2=True)
    c2.pyplot(fig)
    
    # Individual asset
    asset_list = df_current['ativo'].unique()
    asset_list.sort()
    asset = st.sidebar.radio('Ativos', asset_list)
    st.subheader(asset)
    
    df = df.loc[df['ativo'] == asset].groupby('mês_datetime').sum().reset_index()
    current_qnt = df.loc[df['mês_datetime'] == df['mês_datetime'].max(), 'qnt'].iloc[0]
    current_cost = df.loc[df['mês_datetime'] == df['mês_datetime'].max(), 'custo'].iloc[0]
    avg_cost = current_cost/current_qnt
    st.write('Custo médio: {:,.2f} {}'.format(avg_cost, currency_code))
    
    fig, axs = plt.subplots(ncols=2, figsize = (10, 3))
    axs[0].set_title('Valor')
    axs[1].set_title('Cotação')
    colors = get_sns_colors(main_palette, 2)
    
    axs[0].plot(df['mês_datetime'], df['valor']/1000, '-o', color = colors[0])
    axs[0].fill_between(df['mês_datetime'], df['valor']/1000, 
                        y2 = df['valor'].min()/1000, 
                        alpha = 0.5, color = colors[1])
    plt.setp(axs[0].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    plt.setp(axs[0].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    axs[0].set_ylabel('Mil '+currency_code)
    
    axs[1].plot(df['mês_datetime'], df['cotação'], '-o', color = colors[0])
    axs[1].fill_between(df['mês_datetime'], df['cotação'], 
                        y2 = min(df['cotação'].min(), avg_cost), 
                        alpha = 0.5, color = colors[1])
    axs[1].axhline(avg_cost, ls='--', color=colors[0])
    plt.setp(axs[1].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    plt.setp(axs[1].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    axs[1].set_ylabel(currency_code)
    
    st.pyplot(fig)

def view_cripto(df):
    st.write('Cripto')
    
    # Class overview
    st.subheader('Visão geral')
    df_current = df.loc[df['mês_datetime'] == df['mês_datetime'].max()]
    fig, axs = plt.subplots(ncols = 2, figsize = (10, 3))
    
    aux = df_current[['valor_real', 'tipo']].groupby('tipo').sum().reset_index()
    aux.sort_values('valor_real', ascending=False, inplace=True)
    pieplot(aux['valor_real'], aux['tipo'], axs[0], palette=main_palette)
    barplot(aux['tipo'], aux['valor_real'], axs[1], palette=main_palette, 
            rotation=0, align='center', ylabel='R$', y2=True)
    
    st.pyplot(fig)
    
    # Individual asset type
    type_list = df_current['tipo'].unique()
    asset_type = st.sidebar.radio('Categorias', type_list)
    df_current = df_current.loc[df_current['tipo'] == asset_type]
    currency_code = df_current['moeda'].iloc[0]
    
    # Type overview
    st.subheader(asset_type)
    
    # Change
    aux = df_current[df_current['tipo'] == asset_type]
    initial = aux['custo'].sum()
    final = aux['valor'].sum()
    change_percent = 100 * (final-initial) / initial
    st.metric('Custo: {:,.2f} {}'.format(initial, currency_code), 
              '{:,.2f} {}'.format(final, currency_code), 
              '{:.1f}%'.format(change_percent))
    
    # Table and plot
    aux = df_current[['ativo', 'custo', 'valor']].groupby('ativo').sum().reset_index()
    aux['var%'] = aux.apply(lambda x: 100*(x['valor']/x['custo']-1) if x['custo'] != 0
                            else 0, axis=1)
    
    c1, c2 = st.columns(2)
    aux.sort_values('var%', ascending=False, inplace=True)
    c1.write(aux.style.format(formatter = {('custo'): '{:,.2f}', 
                                           ('valor'): '{:,.2f}', 
                                           ('var%'): '{:,.1f}%'}))
    fig, ax = plt.subplots(figsize = (5, 4))
    aux.sort_values('valor', ascending=False, inplace=True)
    barplot(aux['ativo'], aux['valor'], ax, palette=main_palette, 
            rotation=0, align='center', ylabel=currency_code, y2=True)
    c2.pyplot(fig)
    
    # Individual asset
    asset_list = df_current['ativo'].unique()
    asset_list.sort()
    asset = st.sidebar.radio('Ativos', asset_list)
    st.subheader(asset)
    
    df = df.loc[df['ativo'] == asset].groupby('mês_datetime').sum().reset_index()
    current_qnt = df.loc[df['mês_datetime'] == df['mês_datetime'].max(), 'qnt'].iloc[0]
    current_cost = df.loc[df['mês_datetime'] == df['mês_datetime'].max(), 'custo'].iloc[0]
    avg_cost = current_cost/current_qnt
    st.write('Custo médio: {:,.2f} {}'.format(avg_cost, currency_code))
    
    fig, axs = plt.subplots(ncols=2, figsize = (10, 3))
    axs[0].set_title('Valor')
    axs[1].set_title('Cotação')
    colors = get_sns_colors(main_palette, 2)
    
    axs[0].plot(df['mês_datetime'], df['valor'], '-o', color = colors[0])
    axs[0].fill_between(df['mês_datetime'], df['valor'], 
                        y2 = df['valor'].min(), 
                        alpha = 0.5, color = colors[1])
    plt.setp(axs[0].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    plt.setp(axs[0].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    axs[0].set_ylabel(currency_code)
    
    axs[1].plot(df['mês_datetime'], df['cotação'], '-o', color = colors[0])
    axs[1].fill_between(df['mês_datetime'], df['cotação'], 
                        y2 = min(df['cotação'].min(), avg_cost), 
                        alpha = 0.5, color = colors[1])
    axs[1].axhline(avg_cost, ls='--', color=colors[0])
    plt.setp(axs[1].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    plt.setp(axs[1].get_xticklabels(), rotation = 30)#, horizontalalignment='right')
    axs[1].set_ylabel(currency_code)
    
    fig.tight_layout()
    st.pyplot(fig)


# =============================================================================
# Main page
# =============================================================================
df = load_wallet()

# Filter class
wallet_classes = df['class'].unique()
page_dict = {'RF': 'Renda fixa',
             'RV': 'Renda variável',
             'Cripto': 'Cripto'}
pages_list = ['Visão geral'] + [ page_dict[p] for p in wallet_classes ]
page = st.sidebar.selectbox('Visualizar', pages_list)

if page == 'Renda fixa':
    df = df.loc[df['class'] == 'RF']
elif page == 'Renda variável':
    df = df.loc[df['class'] == 'RV']
elif page == 'Cripto':
    df = df.loc[df['class'] == 'Cripto']

# Filter location
loc_list = df['market'].unique()
locations = st.sidebar.multiselect('Locais', loc_list, default = loc_list)
df = df.loc[df['market'].isin(locations)]

if page == 'Visão geral':
    general_view(df)
# elif page == 'Renda fixa':
#     view_rf(df)
# elif page == 'Renda variável':
#     view_rv(df)
# elif page == 'Cripto':
#     view_cripto(df)
