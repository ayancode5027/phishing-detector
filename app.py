import streamlit as st
import pandas as pd
import pickle
import re
import os

from urllib.parse import urlparse
from dotenv import load_dotenv

from api_checker import (
    check_google_safe_browsing,
    check_virustotal
)

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# LOAD FILES
# =========================

model = pickle.load(open("phishing_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Fake Website Detector",
    page_icon="🔐"
)

st.title("🔐 AI Fake Website Detector")
st.write("AI + Google Safe Browsing + VirusTotal")

# =========================
# INPUT
# =========================

url = st.text_input("Enter Website URL")

# =========================
# FEATURE EXTRACTION
# =========================

def extract_features(url):

    parsed = urlparse(url)

    features = {}

    features["url_length"] = len(url)
    features["dots"] = url.count(".")
    features["hyphens"] = url.count("-")
    features["digits"] = sum(c.isdigit() for c in url)

    features["https"] = 1 if parsed.scheme == "https" else 0

    suspicious_words = [
        "login", "verify", "secure", "update",
        "account", "bank", "paypal", "signin",
        "bonus", "free"
    ]

    features["suspicious_words"] = sum(
        word in url.lower() for word in suspicious_words
    )

    suspicious_tlds = [".xyz", ".tk", ".ru", ".ga", ".ml", ".cf"]

    features["suspicious_tld"] = 1 if any(
        tld in url.lower() for tld in suspicious_tlds
    ) else 0

    return pd.DataFrame([features])

# =========================
# MAIN CHECK BUTTON
# =========================

if st.button("Check Website"):

    if url.strip() == "":
        st.warning("Please enter a URL")

    else:

        try:

            # =========================
            # ML MODEL PREDICTION
            # =========================

            data = extract_features(url)
            data = data[feature_columns]

            scaled_data = scaler.transform(data)

            prediction = model.predict(scaled_data)[0]
            probability = model.predict_proba(scaled_data)[0][1]

            # =========================
            # API CHECKS
            # =========================

            google_flagged = check_google_safe_browsing(url)
            virustotal_score = check_virustotal(url)

            # =========================
            # RISK ENGINE
            # =========================

            risk_score = 0

            # ML contribution
            if prediction == 1:
                risk_score += 30

            risk_score += int(probability * 20)

            # Google Safe Browsing
            if google_flagged:
                risk_score += 40

            # VirusTotal
            risk_score += min(virustotal_score * 5, 30)

            # Keyword checks
            suspicious_keywords = [
                "login", "verify", "secure",
                "update", "account", "bank",
                "paypal", "bonus", "free"
            ]

            keyword_hits = sum(
                word in url.lower() for word in suspicious_keywords
            )

            risk_score += keyword_hits * 8

            # Extra rules
            if url.count("-") >= 2:
                risk_score += 15

            suspicious_tlds = [".xyz", ".tk", ".ru", ".ga", ".ml", ".cf"]

            if any(tld in url.lower() for tld in suspicious_tlds):
                risk_score += 20

            if not url.startswith("https"):
                risk_score += 10

            if len(url) > 70:
                risk_score += 10

            # Cap score
            risk_score = min(risk_score, 100)

            # =========================
            # OUTPUT
            # =========================

            st.subheader("Detection Result")

            if risk_score >= 70:
                st.error(f"⚠️ HIGH RISK PHISHING WEBSITE\n\nThreat Score: {risk_score}%")

            elif risk_score >= 40:
                st.warning(f"⚠️ SUSPICIOUS WEBSITE\n\nThreat Score: {risk_score}%")

            else:
                st.success(f"✅ WEBSITE LOOKS SAFE\n\nThreat Score: {risk_score}%")

            st.progress(risk_score)

            # =========================
            # DETAILS
            # =========================

            st.subheader("Threat Intelligence")

            st.write(f"Google Safe Browsing Flagged: {google_flagged}")
            st.write(f"VirusTotal Malicious Score: {virustotal_score}")

            st.subheader("Extracted Features")
            st.dataframe(data)

        except Exception as e:
            st.error(f"Error: {str(e)}")