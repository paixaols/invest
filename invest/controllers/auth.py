from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from invest import db
from invest.models.forms import LoginForm, RegisterForm
from invest.models.tables import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_pw = form.confirm_password.data
        error = None

        if not name:
            error = 'Campo nome é obrigatório.'
        elif not email:
            error = 'Campo e-mail é obrigatório.'
        elif not password:
            error = 'Campo senha é obrigatório.'
        elif password != confirm_pw:
            error = 'Senhas são diferentes.'

        if error is None:
            try:
                user = User(name, email, password)
                db.session.add(user)
                db.session.commit()
            except:
                error = f'E-mail {email} já cadastrado.'
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.pw_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.')

            # TODO: 
            # next = request.args.get('next')
            # # is_safe_url should check if the url is safe for redirects.
            # # See http://flask.pocoo.org/snippets/62/ for an example.
            # if not is_safe_url(next):
            #     return flask.abort(400)

            # return flask.redirect(next or flask.url_for('index'))

            return redirect(url_for('restricted.home'))
        else:
            flash('Invalid credentials.')

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
