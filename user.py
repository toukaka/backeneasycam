import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import logging
import secrets
import string
from email.message import EmailMessage
import smtplib
import secrets


def generate_token():
    return secrets.token_urlsafe(16)  # 16-byte secure token

def send_password_email(token, name, email, password):
    smtp_server = "74.125.140.108"
    smtp_port = 587
    sender_email = "easyparkpronextsys@gmail.com"
    sender_password = "kadu qtyg tihr zkhz"
    # Create the email message
    message = EmailMessage()
    message['From'] = email
    message['To'] = email
    message['Subject'] = f"Welcome to easycampro by nextsys-solutions"
    body = f"""Hello {name}

A new account has been issued to you
if not please contact: support@nextsys-solutions.fr

e-mail: {email}
password: {password}

confirm your account by clicking 

https://easycampro.nextsys-solutions.fr/api/confirm?token={str(token)}
---    
Have a great day !

Nextsys-solution Team

EasyParkPro team

Powered by autosenseOS
"""
    message.set_content(body)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("Email sent!")
        return True, "Email with password sent successfully"
    except Exception as e:
        return False, f"contact Support: support@nextsys-solutions.fr"


def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(secrets.choice(chars) for _ in range(length))

# === Config ===
DB_CONFIG = {
    'host': 'localhost',
    'user': 'pi',
    'password': 'Hesoyam96.',
    'database': 'USERS'
}

# === Logger Setup ===
logging.basicConfig(
    filename='/tmp/user_module.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# ======================================= Database Connection =======================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.debug("Database connection established.")
        return conn
    except Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

# ======================================= Register User =======================================
def register_user(name, email, phone, birthday):
    password = generate_random_password()
    confirmation_token = generate_token()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, name, phone, birthday, password, confirmation_token)
            VALUES (%s, %s, %s,%s,%s,%s)
        """, (email, name, phone, birthday, password, confirmation_token))

        conn.commit()
        success, info = send_password_email(confirmation_token, name, email, password)
        if success:
            logger.info(f"New user registered: {email}")
            return True, "User registered successfully"
        else:
            return False, "Password e-mail not sent please contact support support@nextsys-solution.fr"

    except mysql.connector.IntegrityError:
        logger.warning(f"Attempt to register duplicate email: {email}")
        return False, "Email already registered"

    except Error as e:
        logger.error(f"Error during registration for {email}: {e}")
        return False, f"Database error: {e}"

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# ======================================= Register User =======================================
def check_register(token):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE confirmation_token = %s", (token,))
        user = cursor.fetchone()
        if user:
            cursor.execute("""
                UPDATE users
                SET is_confirmed = 100, confirmation_token = NULL
                WHERE id = %s
            """, (user[0],))
            conn.commit()
            return True, {'status': 'success', 'message': 'Account confirmed'}
        else:
            return False, {'status': 'error', 'message': 'Invalid or expired token'}

    except Error as e:
        logger.error(f"Error during verify for {email}: {e}")
        return  False, f"Database error: {e}"

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()



# ======================================= Login User =======================================
def login_user(email, password):
    try:
        print("--------*********-login request-********--------")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, password, is_confirmed FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()


        print("--------*********-login request-********--------", user['is_confirmed'])
        if user['is_confirmed'] != 100:  # is_confirmed is False
            return False, "Please confirm your account via the email sent to you"

        cursor.execute("SELECT id, name, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user['password'] == password:
            print(f"Successful login: {email}")
            return True, {
                "id": user['id'],
                "name": user['name'],
                "email": email
            }
        else:
            logger.warning(f"Failed login attempt: {email}")
            return False, "Invalid credentials"

    except Error as e:
        logger.error(f"Error during login for {email}: {e}")
        return False, f"Database error: {e}"

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

