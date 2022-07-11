import pandas as pd

from db.mongodb_engine import get_collection

def parse_statement_entry(x, c):
    evento = x['event']
    id_ativo = x['id_asset']
    moeda = x['currency']
    qnt = x['quantity']
    inst = x['bank']
    if evento == 'compra' or evento == 'subscrição':
        custo = x['value']+x['fee']
        custo_real = custo*x['currency_rate']
        if id_ativo in c:
            c[id_ativo]['quantity'] += qnt
            c[id_ativo]['cost'] += custo
            c[id_ativo]['cost_brl'] += custo_real
        else:
            c[id_ativo] = {'id_asset': id_ativo, 'bank': inst, 'currency': moeda, 
                           'quantity': qnt, 'cost': custo, 'cost_brl': custo_real}
    elif evento == 'venda':
        # Moeda original
        cm = c[id_ativo]['cost']/c[id_ativo]['quantity']
        venda = round(cm*qnt, 2)
        c[id_ativo]['cost'] -= venda
        # BRL
        cm = c[id_ativo]['cost_brl']/c[id_ativo]['quantity']
        venda = round(cm*qnt, 2)
        c[id_ativo]['cost_brl'] -= venda
        c[id_ativo]['quantity'] -= qnt
    elif evento == 'desdobramento':
        c[id_ativo]['quantity'] *= x['pos_split']/x['pre_split']
    elif evento == 'grupamento':
        c[id_ativo]['quantity'] = round(c[id_ativo]['quantity']*x['pos_split']/x['pre_split'], 5)
    elif evento == 'bonificação':
        c[id_ativo]['quantity'] += qnt
        c[id_ativo]['cost'] += x['value']
    elif evento == 'amortização':
        c[id_ativo]['cost'] -= x['value']
    else:
        print('Evento de {} não suportado em {}: {}'.format(id_ativo, x['date'].date(), evento))
    return c

class Wallet(object):
    def __init__(self):
        pass
    
    def consolidate(self, statement):
        c = {}
        for i in range(len(statement)):
            c = parse_statement_entry(statement.iloc[i], c)
        for key in list(c.keys()):
            if c[key]['quantity'] == 0:
                c.pop(key)
        wallet = pd.DataFrame.from_dict(c, orient='index')
        return wallet.reset_index(drop=True)
