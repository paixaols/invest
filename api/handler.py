import pandas as pd
from flask import Flask, request, Response

from db.mongodb_engine import get_collection
from pipeline import Wallet

# Initialize API
app = Flask(__name__)

@app.route('/get-assets', methods = ['GET'])
def get_assests():
    collection = get_collection('investe', 'assets')
    cursor = collection.find()
    assets = pd.DataFrame(cursor)
    json_response = assets.drop(columns='_id').to_json(orient = 'records', date_format = 'iso')
    return json_response

@app.route('/get-statement', methods = ['GET'])
def get_statement():
    collection = get_collection('investe', 'transactions')
    cursor = collection.find()
    statement = pd.DataFrame(cursor)
    json_response = statement.drop(columns='_id').to_json(orient = 'records', date_format = 'iso')
    return json_response

@app.route('/consolidate-statement', methods = ['GET'])
def consolidate_statement():
    # Get statement from DB
    collection = get_collection('investe', 'transactions')
    cursor = collection.find()
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
    json = request.get_json()
    year = json['year']
    month = json['month']
    collection = get_collection('investe', 'wallet')
    query = {'year':year,'month':month}
    cursor = collection.find(query)
    wallet = pd.DataFrame(cursor)
    wallet.drop(columns='_id', inplace=True)
    json_response = wallet.to_json(orient = 'records', date_format = 'iso')
    return json_response

if __name__ == '__main__':
    from os import environ
    app.run(host = '0.0.0.0', port = environ.get('PORT', 5000))
