from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_pairs.db'
db = SQLAlchemy(app)

class CorrelatedPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin1 = db.Column(db.String(10), nullable=False)
    coin2 = db.Column(db.String(10), nullable=False)

class PairForm(FlaskForm):
    coin1 = StringField('Coin 1', validators=[DataRequired()])
    coin2 = StringField('Coin 2', validators=[DataRequired()])
    submit = SubmitField('Ekle')

@app.route('/get_chart', methods=['POST'])
def get_chart():
    # İşlemler burada yapılacak
    return jsonify({"status": "success"})

@app.route('/')
def index():
    pairs = CorrelatedPair.query.all()
    form = PairForm()
    return render_template('index.html', pairs=pairs, form=form)

@app.route('/add_pair', methods=['POST'])
def add_pair():
    form = PairForm()
    if form.validate_on_submit():
        new_pair = CorrelatedPair(coin1=form.coin1.data.upper(), coin2=form.coin2.data.upper())
        db.session.add(new_pair)
        db.session.commit()
        flash('Yeni çift başarıyla eklendi!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_pair/<int:pair_id>')
def remove_pair(pair_id):
    pair = CorrelatedPair.query.get_or_404(pair_id)
    db.session.delete(pair)
    db.session.commit()
    flash('Çift başarıyla silindi!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
