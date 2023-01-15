import functools

from datetime import datetime
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from invest import db
from invest.models.forms import AssetForm
from invest.models.tables import Asset


def admin_access(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if current_user.role != 'admin':
            return '<h1>Unauthorized</h1><p>Admin privilege is required.</p>'
        return view(**kwargs)
    return wrapped_view


bp = Blueprint('admin', __name__, url_prefix='/adm')

@bp.route('/assets', methods=['GET', 'POST'])
@login_required
@admin_access
def assets():
    form = AssetForm()
    assets = Asset.query.all()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        market = form.market.data
        asset_type = form.asset_type.data
        group = form.asset_group.data
        expiration_date = form.expiration_date.data
        if form.unexpirable.data:
            expiration_date = datetime(2200, 12, 31)

        asset = Asset(name, description, market, asset_type, group, expiration_date)
        db.session.add(asset)
        db.session.commit()

        return redirect(url_for('admin.assets'))

    return render_template('admin/assets.html', form=form, assets=assets)

@bp.route('/update-asset', methods=['GET', 'POST'])
@login_required
@admin_access
def update_asset():
    # Fill form
    asset_id = request.args.get('id')
    asset = Asset.query.get_or_404(
        int(asset_id),
        description=f'There is no data with id: {asset_id}'
    )
    expiration_date = asset.asset_expiration_date

    data = {
        'name': asset.asset_name,
        'description': asset.description,
        'market': asset.market,
        'asset_type': asset.asset_type,
        'asset_group': asset.asset_group,
        'expiration_date': expiration_date,
        'unexpirable': False
    }
    expiration_field_disabled = False
    if expiration_date == datetime(2200, 12, 31):
        data['expiration_date'] = None
        data['unexpirable'] = True
        expiration_field_disabled = True
    form = AssetForm(data=data)

    if form.validate_on_submit():
        # Update changes
        asset.asset_name = form.name.data
        asset.description = form.description.data
        asset.market = form.market.data
        asset.asset_type = form.asset_type.data
        asset.asset_group = form.asset_group.data
        if form.unexpirable.data:
            asset.asset_expiration_date = datetime(2200, 12, 31)
        else:
            asset.asset_expiration_date = form.expiration_date.data

        db.session.commit()

        return redirect(url_for('admin.assets'))

    return render_template(
        'admin/update-asset.html',
        form=form,
        asset_id=asset_id,
        disabled=expiration_field_disabled
    )

@bp.route('/delete-asset', methods=['GET'])
@login_required
@admin_access
def delete_asset():
    asset_id = request.args.get('id')
    asset = Asset.query.get_or_404(
        int(asset_id),
        description=f'There is no data with id: {asset_id}'
    )
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('admin.assets'))
