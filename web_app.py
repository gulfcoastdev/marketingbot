#!/usr/bin/env python3
"""
Web Interface for Marketing Bot
Provides manual posting controls with basic security
"""
import os
import sys
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Rate limiting (relaxed for testing)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"]
)

# Simple authentication (replace with proper auth in production)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv('ADMIN_PASSWORD', 'changeme123'))

# CSRF protection
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def csrf_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('_csrf_token')
        if not token or token != request.form.get('_csrf_token'):
            flash('Invalid CSRF token', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Template globals
app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['authenticated'] = True
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
            time.sleep(1)  # Prevent brute force

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/post_events', methods=['POST'])
@login_required
@csrf_required
@limiter.limit("10 per minute")
def post_events():
    try:
        print(f"\n🎯 [WEB] Starting daily events posting at {datetime.now()}")

        # Import here to avoid circular imports
        from scripts.social_media_automation import SocialMediaAutomation

        automation = SocialMediaAutomation()
        today = datetime.now().strftime('%Y-%m-%d')

        print(f"🎯 [WEB] Initialized automation, posting for date: {today}")

        # Check available media first
        media = automation.select_random_media()
        print(f"🎯 [WEB] Selected media: {media.get('name', 'None') if media else 'None'}")

        # Check Publer accounts
        accounts = automation.publer.get_accounts()
        print(f"🎯 [WEB] Available Publer accounts: {len(accounts) if accounts else 0}")
        if accounts:
            for acc in accounts:
                print(f"    - {acc.get('type', 'unknown')}: {acc.get('username', 'N/A')} (ID: {acc.get('id')})")

        # Run in test mode for immediate feedback
        result = automation.run_daily_events(today, test_mode=True)

        print(f"🎯 [WEB] Automation completed. Result: {result}")

        return jsonify({
            'success': True,
            'message': 'Daily events posted successfully!',
            'details': {
                'posting_result': result,
                'media_used': media.get('name', 'None') if media else 'None',
                'accounts_available': len(accounts) if accounts else 0,
                'date': today,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"❌ [WEB] Error in post_events: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error posting events: {str(e)}',
            'details': {'error_type': type(e).__name__, 'timestamp': datetime.now().isoformat()}
        }), 500

@app.route('/post_facts', methods=['POST'])
@login_required
@csrf_required
@limiter.limit("10 per minute")
def post_facts():
    try:
        print(f"\n🌊 [WEB] Starting daily facts posting at {datetime.now()}")

        # Import here to avoid circular imports
        from scripts.social_media_automation import SocialMediaAutomation

        automation = SocialMediaAutomation()

        # Check available media first
        media = automation.select_random_media()
        print(f"🌊 [WEB] Selected media: {media.get('name', 'None') if media else 'None'}")

        # Check Publer accounts
        accounts = automation.publer.get_accounts()
        print(f"🌊 [WEB] Available Publer accounts: {len(accounts) if accounts else 0}")

        # Run in test mode for immediate feedback
        result = automation.run_daily_facts(test_mode=True)

        print(f"🌊 [WEB] Facts automation completed. Result: {result}")

        return jsonify({
            'success': True,
            'message': 'Daily facts posted successfully!',
            'details': {
                'posting_result': result,
                'media_used': media.get('name', 'None') if media else 'None',
                'accounts_available': len(accounts) if accounts else 0,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"❌ [WEB] Error in post_facts: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error posting facts: {str(e)}',
            'details': {'error_type': type(e).__name__, 'timestamp': datetime.now().isoformat()}
        }), 500

@app.route('/status')
@login_required
def status():
    """Check system status"""
    try:
        # Basic health checks
        checks = {
            'openai_key': bool(os.getenv('OPENAI_API_KEY')),
            'publer_key': bool(os.getenv('PUBLER_API_KEY')),
            'time': datetime.now().isoformat(),
            'environment': 'local'
        }

        return jsonify(checks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set")
    if not os.getenv('PUBLER_API_KEY'):
        print("⚠️  Warning: PUBLER_API_KEY not set")

    print(f"🔐 Admin credentials: {ADMIN_USERNAME} / {os.getenv('ADMIN_PASSWORD', 'changeme123')}")
    print("🚀 Starting web interface...")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )