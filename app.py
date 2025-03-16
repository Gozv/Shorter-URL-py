from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import uuid
import validators
from config import config
from flask_sqlalchemy import SQLAlchemy

# Inicialización de la aplicación
app = Flask(__name__)
app.config.from_object(config['development'])

# Configuración de la base de datos
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.Column(db.Integer, default=0)

# Comando CLI para inicializar la base de datos
@app.cli.command()
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
    print("Database initialized!")

def validate_url(url):
    if not validators.url(url):
        return False
    return url.startswith(('http://', 'https://'))

def generate_short_code():
    return uuid.uuid4().hex[:6]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    
    if not validate_url(original_url):
        return render_template('index.html', error='URL inválida'), 400

    short_code = generate_short_code()
    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        existing_url = URL.query.filter_by(short_code=short_code).first()
        if not existing_url:
            break
        short_code = generate_short_code()
        attempts += 1
    else:
        return render_template('index.html', error='Error generando URL, intenta nuevamente'), 500

    new_url = URL(
        original_url=original_url,
        short_code=short_code,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(new_url)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return render_template('index.html', error='Error guardando URL'), 500

    shortened_url = request.host_url + short_code
    return render_template('shortened.html', 
                         shortened_url=shortened_url,
                         original_url=original_url)

@app.route('/<short_code>')
def redirect_short_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    
    if url:
        url.visits += 1
        db.session.commit()
        return redirect(url.original_url)
    else:
        return render_template('404.html'), 404

@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL requerida'}), 400
    
    original_url = data['url']
    if not validate_url(original_url):
        return jsonify({'error': 'URL inválida'}), 400

    short_code = generate_short_code()
    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        existing_url = URL.query.filter_by(short_code=short_code).first()
        if not existing_url:
            break
        short_code = generate_short_code()
        attempts += 1
    else:
        return jsonify({'error': 'Error generando código único'}), 500

    new_url = URL(
        original_url=original_url,
        short_code=short_code,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(new_url)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

    return jsonify({
        'original_url': original_url,
        'short_url': request.host_url + short_code,
        'short_code': short_code,
        'visits': new_url.visits
    }), 201

@app.route('/api/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if not url:
        return jsonify({'error': 'URL no encontrada'}), 404
    
    return jsonify({
        'created_at': url.created_at.isoformat(),
        'visits': url.visits,
        'original_url': url.original_url
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')