from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_pairs.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CorrelatedPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin1 = db.Column(db.String(10), nullable=False)
    coin2 = db.Column(db.String(10), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    pairs = CorrelatedPair.query.all()
    return render_template('index.html', pairs=pairs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_pair', methods=['POST'])
@login_required
def add_pair():
    coin1 = request.form['coin1'].upper()
    coin2 = request.form['coin2'].upper()
    new_pair = CorrelatedPair(coin1=coin1, coin2=coin2)
    db.session.add(new_pair)
    db.session.commit()
    flash(f'Added new pair: {coin1} - {coin2}')
    return redirect(url_for('index'))

@app.route('/remove_pair/<int:pair_id>', methods=['POST'])
@login_required
def remove_pair(pair_id):
    pair = CorrelatedPair.query.get_or_404(pair_id)
    db.session.delete(pair)
    db.session.commit()
    flash(f'Removed pair: {pair.coin1} - {pair.coin2}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    app.run(debug=True)