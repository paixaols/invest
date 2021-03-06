import datetime
import pandas as pd

from flask import Flask, request, Response

from db.mongodb_engine import get_collection
from pipeline import Wallet

# Initialize API
app = Flask(__name__)

collection_assets = get_collection('investe', 'assets')
collection_transactions = get_collection('investe', 'transactions')
collection_wallet = get_collection('investe', 'wallet')

@app.route('/get-assets', methods = ['GET'])
def get_assests():
    cursor = collection_assets.find()
    assets = pd.DataFrame(cursor)
    json_response = assets.drop(columns='_id').to_json(orient = 'records', date_format = 'iso')
    return json_response

@app.route('/get-statement', methods = ['GET'])
def get_statement():
    cursor = collection_transactions.find()
    statement = pd.DataFrame(cursor)
    json_response = statement.drop(columns='_id').to_json(orient = 'records', date_format = 'iso')
    return json_response

@app.route('/consolidate-statement', methods = ['GET'])
def consolidate_statement():
    # Get statement from DB
    cursor = collection_transactions.find()
    statement = pd.DataFrame(cursor)
    statement.drop(columns='_id', inplace=True)
    statement['pre_split'] = statement['split_factor'].str['pre']
    statement['pos_split'] = statement['split_factor'].str['pos']
    # Consolidate pipeline
    pipeline = Wallet()
    wallet = pipeline.consolidate(statement)
    json_response = wallet.to_json(orient = 'records', date_format = 'iso')
    return json_response

@app.route('/load-wallet', methods = ['POST'])
def load_wallet():
    filters = request.get_json()
    if 'year' in filters:
        year = filters['year']
        month = filters['month']
        query = {'date':{
            '$gte':datetime.datetime(year,month,1)
        }}
    else:
        query = {}
    cursor = collection_wallet.find(query, projection={'_id':0})
    df = pd.DataFrame(cursor)
    json_response = df.to_json(orient = 'records', date_format = 'iso')
    return json_response

if __name__ == '__main__':
    from os import environ
    app.run(host = '0.0.0.0', port = environ.get('PORT', 5000))
