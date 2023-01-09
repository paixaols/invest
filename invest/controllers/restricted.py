import datetime

from flask import (
    Blueprint, current_app, redirect, render_template, request, url_for
)
from flask_login import current_user, login_required

from invest import db
from invest.models.forms import AssetForm
from invest.models.tables import Asset

bp = Blueprint('restricted', __name__, url_prefix='/r')

@bp.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('restricted/home.html')

@bp.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    user = current_user
    form = AssetForm()
    wallet = []
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        market = form.market.data
        asset_type = form.asset_type.data
        asset_group = form.asset_group.data
        expiration_date = form.expiration_date.data
        asset = Asset(name, description, market, asset_type, asset_group, expiration_date)
        db.session.add(asset)
        db.session.commit()

    return render_template(
        'restricted/my-assets.html',
        form=form,
        wallet=wallet
        # wallet=current_app.config['wallet']
    )
