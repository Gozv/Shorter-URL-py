from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import sqlite3
import uuid
import validators

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            visits INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def validate_url(url):
    if not validators.url(url):
        return False
    return url.startswith(('http://', 'https://'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    
    if not validate_url(original_url):
        return render_template('index.html', error='URL inválida'), 400

    short_code = str(uuid.uuid4().hex)[:6]
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO urls (original_url, short_code, created_at) VALUES (?, ?, ?)',
                    (original_url, short_code, created_at))
        conn.commit()
    except sqlite3.IntegrityError:
        # Regenerar código si hay colisión (muy improbable)
        short_code = str(uuid.uuid4().hex)[:6]
        conn.execute('INSERT INTO urls (original_url, short_code, created_at) VALUES (?, ?, ?)',
                    (original_url, short_code, created_at))
        conn.commit()
    finally:
        conn.close()

    shortened_url = request.host_url + short_code
    return render_template('shortened.html', 
                         shortened_url=shortened_url,
                         original_url=original_url)

@app.route('/<short_code>')
def redirect_short_url(short_code):
    conn = get_db_connection()
    url = conn.execute('SELECT original_url FROM urls WHERE short_code = ?',
                      (short_code,)).fetchone()
    conn.close()
    
    if url:
        conn = get_db_connection()
        conn.execute('UPDATE urls SET visits = visits + 1 WHERE short_code = ?',
                    (short_code,))
        conn.commit()
        conn.close()
        return redirect(url['original_url'])
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

    short_code = str(uuid.uuid4().hex)[:6]
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO urls (original_url, short_code, created_at) VALUES (?, ?, ?)',
                    (original_url, short_code, created_at))
        conn.commit()
    except sqlite3.IntegrityError:
        short_code = str(uuid.uuid4().hex)[:6]
        conn.execute('INSERT INTO urls (original_url, short_code, created_at) VALUES (?, ?, ?)',
                    (original_url, short_code, created_at))
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        'original_url': original_url,
        'short_url': request.host_url + short_code,
        'short_code': short_code
    }), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)