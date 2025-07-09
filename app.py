from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import smtplib
from email.message import EmailMessage

import sys
from datetime import datetime
import sqlite3
import os
import user  # Your separate user module

def add_or_update_entry(email, name, phone):
    # Define absolute path (change this to your preferred folder)
    db_dir = '//nextsys_data/'  # example directory
    # os.makedirs(db_dir, exist_ok=True)  # create if missing

    db_path = os.path.join(db_dir, 'contact_forms.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT
    )
    ''')

    try:
        cursor.execute('''
        INSERT INTO contacts (email, name, phone) VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name=excluded.name,
            phone=excluded.phone
        ''', (email, name, phone))
        conn.commit()
        print(f"Entry added/updated for {name} ({email})")
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def log_to_file(message):
    print("++++++++")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('/tmp/app.log', 'a') as f:
        f.write(f"{timestamp} {message}\n")

def request_command_send_email(dest, name, phone, message):
    smtp_server = "74.125.140.108"
    smtp_port = 587
    sender_email = "easyparkpronextsys@gmail.com"
    sender_password = "kadu qtyg tihr zkhz"
    subject = 'Thank you for your intrest in EasycamPro Solution'

    # Create the email message
    order = EmailMessage()
    order['From'] = dest
    order['To'] = dest
    order['Subject'] = subject
    body = f"""Thank you for your request. Our team will get in touch with you shortly.

---    
Have a great day !

Nextsys-solution Team

Your message body:
name : {name}
phone: {phone}
email: {dest}
{message}
"""
    order.set_content(body)

    confirmation = EmailMessage()
    confirmation['From'] = sender_email
    confirmation['To'] = sender_email
    confirmation['Subject'] = f"New order from {phone}"
    body_confirmation = f"""Message Received
Thank you for your request. Our team will get in touch with you shortly.

Have a great day !
name : {name}
phone: {phone}
email: {dest}
message: {message}


EasyParkPro team

Powered by autosenseOS
"""

    confirmation.set_content(body_confirmation)
    

    # Connect and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(order)
            server.send_message(confirmation)
            print("Email sent!")
            log_to_file("Email sent successfully.")
        return True, "Email sent successfully"
    except Exception as e:
        log_to_file(f"Email failed {str(e)}")
        return False, f"contact Support: support@nextsys-solutions.fr"

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)
print("_______________App backend__________________")


@app.route('/contact', methods=['POST'])
def contact():
    print("--------0000000-Contact request-0000000--------")
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    message = request.form.get('message', '')
    add_or_update_entry(email, name, phone)
    log_to_file(f"Received order request from {email}, name: {name}, phone: {phone}")
    success, info = request_command_send_email(email, name, phone, message)
    if success:
        return jsonify({'status': 'success', 'message': 'Email sent successfully !'})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to send email: {info}'}), 500


@app.route('/login', methods=['POST'])
def login():
    print("--------0000000-Login request-0000000--------")
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not all([email, password]):
        return jsonify({'status': 'error', 'message': 'Email and password required'}), 400

    success, info = user.login_user(email, password)
    print("Result ... ", success, info)
    if success:
        return jsonify({'status': 'success', 'message': 'Login successful', 'user': info}),201
    else:
        return jsonify({'status': 'error', 'message': info}), 401

    
@app.route('/register', methods=['POST'])
def register():
    print("--------0000000-Register request-0000000--------")
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    birthday = request.form.get('birthday', '').strip()
    if not all([name, email, phone, birthday]):
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    success, msg = user.register_user(name, email, phone, birthday)
    if success:
        return jsonify({'status': 'success', 'message': msg}), 201
    else:
        return jsonify({'status': 'error', 'message': msg}), 409

from flask import render_template, request

@app.route('/confirm', methods=['GET'])
def confirm_account():
    print("--------0000000-Confirm request-0000000--------")
    token = request.args.get('token')
    if not token:
        return render_template('error.html'), 400
    
    success, msg = user.check_register(token)
    print("--------0000000-Confirm request-0000000--------", success, msg)
    
    if success:
        return render_template('success.html'), 200
    else:
        return render_template('error.html'), 409

if __name__ == '__main__':
    app.run(debug=False)