import requests
import whois
import re
import base64
from flask import Flask, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify 


app = Flask(__name__)
CORS(app)

GOOGLE_SAFE_BROWSING_API_KEY = "AIzaSyAJfB3obk9skPUodobr6JR5Kn4NpJQ5_VM"

# List of well-known domains to whitelist
WHITELISTED_DOMAINS = {}

# Decode URL if encoded
def decode_url(url):
    try:
        decoded_url = base64.b64decode(url).decode('utf-8')
        return decoded_url
    except:
        return url  # Return original if decoding fails

# Fetch content using requests
def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return str(e)

# Check API legitimacy with Whois
def check_api_legitimacy(api_url):
    try:
        domain = api_url.split("/")[2]
        domain_info = whois.whois(domain)
        if domain_info.creation_date and (2024 - domain_info.creation_date.year < 1):
            return False  # Likely a scam
        return True
    except:
        return False  # Unable to verify domain

# Check Domain Reputation
def check_domain_reputation(domain):
    if domain in WHITELISTED_DOMAINS:
        return True
    try:
        headers = {"x-apikey": "e4aaefad292fc259db711d283b27275d0796e744d6c166140489f34080a7a8d6"}
        response = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["data"]["attributes"]["last_analysis_stats"]["malicious"] > 0:
                return False  # Domain has been flagged as malicious
        return True
    except:
        return False  # Unable to verify domain reputation

# Check SSL Certificate Validity
def check_ssl_certificate(url):
    try:
        response = requests.get(url, verify=True)
        return response.status_code == 200
    except requests.exceptions.SSLError:
        return False
    except:
        return False

# Check with Google Safe Browsing API
def check_google_safe_browsing(url):
    try:
        payload = {
            "client": {"clientId": "your_client_id", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}",
            json=payload
        )
        result = response.json()
        return "matches" not in result
    except:
        return False

# Analyze Webpage
def analyze_webpage(url):
    try:
        url = decode_url(url)  # Decode if encoded
        domain = url.split("/")[2]
        
        if domain in WHITELISTED_DOMAINS:
            return False  # Directly mark as safe if in whitelist
        
        # Perform security checks
        domain_reputation = check_domain_reputation(domain)
        ssl_valid = check_ssl_certificate(url)
        google_safe = check_google_safe_browsing(url)
        
        # Risk evaluation
        is_scam = not domain_reputation or not ssl_valid or not google_safe
        
        return is_scam
    except Exception as e:
        return False

# Flask API Route
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        body = request.get_json()
        url = body.get('url')

        if not url:
            raise ValueError("No URL provided in the request")

        result = analyze_webpage(url)

        return jsonify({"safe": not result})

    except Exception as e:
        return "False"  # Default to False on errors

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)