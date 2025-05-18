import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')


def get_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


@app.route('/')
def index():
    # Извлекаем и удаляем сообщение из сессии
    message_data = session.pop('last_check_message', None)
    if message_data:
        flash(message_data[0], message_data[1])
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def urls():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT 
            urls.id,
            urls.name,
            urls.created_at,
            MAX(url_checks.created_at) AS last_check,
            (SELECT status_code 
             FROM url_checks 
             WHERE url_id = urls.id 
             ORDER BY created_at DESC 
             LIMIT 1) AS last_status
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        GROUP BY urls.id
        ORDER BY urls.created_at DESC;
    ''')
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>')
def url_detail(id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Получение данных URL
            cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
            url = cur.fetchone()
            if not url:
                abort(404)

            # Получение списка проверок
            cur.execute('''
                SELECT 
                    id, 
                    url_id, 
                    status_code, 
                    h1, 
                    title, 
                    description, 
                    created_at 
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC
            ''', (id,))
            checks = cur.fetchall()

        return render_template('url_detail.html', url=url, checks=checks)
    except psycopg2.Error as e:
        app.logger.error(f'Database error: {str(e)}')
        abort(500)
    finally:
        conn.close()


@app.route('/urls', methods=['POST'])
def add_url():
    raw_url = request.form.get('url', '').strip()
    error = validate_url(raw_url)  # Изменено на error вместо errors
    if error:
        flash(error, 'danger')
        return render_template('index.html', url=raw_url), 422

    parsed_url = urlparse(raw_url)
    normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
            (normalized_url, datetime.now())
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        flash('Сайт успешно добавлен', 'success')
        return redirect(url_for('url_detail', id=url_id))
    except psycopg2.IntegrityError:
        conn.rollback()
        cur.execute('SELECT id FROM urls WHERE name = %s;', (normalized_url,))
        url_id = cur.fetchone()[0]
        flash('Страница уже существует', 'info')
        return redirect(url_for('url_detail', id=url_id))
    finally:
        cur.close()
        conn.close()


@app.route('/urls/<int:id>/checks', methods=['POST'])
def url_check(id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Получаем URL из базы
            cur.execute('SELECT id, name FROM urls WHERE id = %s', (id,))
            url_data = cur.fetchone()
            if not url_data:
                flash('Сайт не найден', 'danger')
                return redirect(url_for('urls'))

            url_id, url_name = url_data

            try:
                response = requests.get(url_name, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                flash('Произошла ошибка при проверке', 'danger')
                return redirect(url_for('url_detail', id=url_id))

            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем данные
            h1 = soup.h1.text.strip() if soup.h1 else None
            title = soup.title.text.strip() if soup.title else None
            description_tag = soup.find('meta', attrs={'name': 'description'})
            description = description_tag['content'].strip() if description_tag else None

            # Вставляем проверку
            cur.execute('''
                INSERT INTO url_checks (
                    url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                url_id,
                response.status_code,
                h1[:255] if h1 else None,
                title[:255] if title else None,
                description[:255] if description else None,
                datetime.now()
            ))
            conn.commit()
            flash('Страница успешно проверена', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
        app.logger.error(f'Ошибка проверки: {str(e)}')
    finally:
        conn.close()

    return redirect(url_for('url_detail', id=id))


def validate_url(url):
    if not url:
        return 'URL обязателен'
    if len(url) > 255:
        return 'URL превышает 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'
    return None

