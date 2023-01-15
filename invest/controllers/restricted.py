import datetime
import pandas as pd

from flask import (
    Blueprint, current_app, redirect, render_template, request, url_for
)
from flask_login import current_user, login_required

from invest import db
from invest.models.forms import AssetForm, WalletEntryForm
from invest.models.tables import Asset

bp = Blueprint('restricted', __name__, url_prefix='/r')

@bp.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('restricted/home.html')

# def build_select_field_choices(table, col):
#     ch = [ getattr(row, col) for row in table ]
#     choices = []
#     for c in ch:
#         if c not in choices:
#             choices.append(c)
#     choices.sort()
#     return [ (c, c) for c in choices ]

def build_select_field_choices(df, col):
    choices = list(df[col].unique())
    choices.sort()
    return [ (c, c) for c in choices ]

@bp.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    # user = current_user
    form = WalletEntryForm()

    query = Asset.query
    df = pd.read_sql(query.statement, query.session.bind)

    form.market.choices = build_select_field_choices(df, 'market')
    form.asset_type.choices = build_select_field_choices(df, 'asset_type')
    form.asset_group.choices = build_select_field_choices(df, 'asset_group')
    form.asset.choices = build_select_field_choices(df, 'asset_name')
    # # if form.validate_on_submit():
    # #     # name = form.name.data
    # #     # description = form.description.data
    # #     # market = form.market.data
    # #     # asset_type = form.asset_type.data
    # #     # asset_group = form.asset_group.data
    # #     # expiration_date = form.expiration_date.data
    # #     # asset = Asset(name, description, market, asset_type, asset_group, expiration_date)
    # #     # # db.session.add(asset)
    # #     # # db.session.commit()

    # assets_json = {'BBAS3': 'Brasil'}
    assets_json = df.to_json(orient='records')
    return render_template('restricted/my-assets.html', form=form, assets=assets_json)
    # return render_template('restricted/my-assets.html', form=form, assets={})
