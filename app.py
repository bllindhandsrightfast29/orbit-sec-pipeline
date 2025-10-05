"""
Vulnerable Flask Application for DevSecOps Pipeline Demo
This app intentionally contains security issues for educational purposes
"""
from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# Intentional vulnerability: Hardcoded secret (for Gitleaks to detect)
API_KEY = "sk_live_51234567890abcdefghijklmnop"
DATABASE_PASSWORD = "SuperSecret123!"

@app.route('/')
def home():
    return """
    <h1>DevSecOps Pipeline Demo</h1>
    <p>This is a vulnerable Flask application for demonstrating security scanning.</p>
    <ul>
        <li><a href="/api/user?name=John">User API (SSTI vulnerable)</a></li>
        <li><a href="/fetch?url=https://example.com">URL Fetcher (SSRF vulnerable)</a></li>
    </ul>
    """

@app.route('/api/user')
def user():
    # Intentional vulnerability: Server-Side Template Injection (SSTI)
    name = request.args.get('name', 'Guest')
    template = f"<h2>Hello {name}!</h2>"
    return render_template_string(template)

@app.route('/fetch')
def fetch_url():
    # Intentional vulnerability: Server-Side Request Forgery (SSRF)
    url = request.args.get('url', '')
    if url:
        try:
            response = requests.get(url, timeout=5)
            return f"<pre>{response.text[:500]}</pre>"
        except Exception as e:
            return f"Error: {str(e)}"
    return "Provide a URL parameter"

@app.route('/config')
def show_config():
    # Intentional vulnerability: Exposing sensitive configuration
    return {
        "api_key": API_KEY,
        "db_password": DATABASE_PASSWORD,
        "debug_mode": True
    }

if __name__ == '__main__':
    # Intentional vulnerability: Debug mode in production
    app.run(host='0.0.0.0', port=5001, debug=True)
