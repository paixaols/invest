from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('restricted', __name__, url_prefix='/r')

@bp.route('/home', methods=['GET'])
@login_required
def home():

    return render_template('restricted/home.html')
