import requests

# =========================
# GOOGLE SAFE BROWSING
# =========================

GOOGLE_API_KEY = "PASTE_GOOGLE_API_KEY"

def check_google_safe_browsing(url):

    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"

    payload = {

        "client": {
            "clientId": "fake-detector",
            "clientVersion": "1.0"
        },

        "threatInfo": {

            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE"
            ],

            "platformTypes": [
                "ANY_PLATFORM"
            ],

            "threatEntryTypes": [
                "URL"
            ],

            "threatEntries": [
                {"url": url}
            ]
        }
    }

    response = requests.post(
        api_url,
        json=payload
    )

    result = response.json()

    return "matches" in result

# =========================
# VIRUSTOTAL
# =========================

VIRUSTOTAL_API_KEY = "PASTE_VIRUSTOTAL_API_KEY"

def check_virustotal(url):

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    response = requests.post(
        "https://www.virustotal.com/api/v3/urls",
        headers=headers,
        data={"url": url}
    )

    if response.status_code != 200:
        return 0

    result = response.json()

    url_id = result["data"]["id"]

    report = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{url_id}",
        headers=headers
    )

    report_json = report.json()

    try:

        stats = report_json["data"]["attributes"]["stats"]

        return stats["malicious"]

    except:

        return 0