import pandas as pd
import pickle
import re

from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# =========================
# SMALL TRAINING DATA
# =========================

data = {

    "url": [

        # SAFE
        "https://google.com",
        "https://github.com",
        "https://openai.com",
        "https://microsoft.com",
        "https://apple.com",
        "https://wikipedia.org",
        "https://amazon.com",
        "https://facebook.com",

        # PHISHING
        "http://paypal-login-verify123.xyz",
        "http://amaz0n-secure-login.tk",
        "http://free-netflix-account.ga",
        "http://bank-secure-update.ru",
        "http://verify-paypal-account.ml",
        "http://secure-login-confirm.cf",
        "http://bonus-free-gift.xyz",
        "http://signin-paypal-security.tk"

    ],

    # 0 = SAFE
    # 1 = PHISHING

    "label": [
        0,0,0,0,0,0,0,0,
        1,1,1,1,1,1,1,1
    ]
}

df = pd.DataFrame(data)

# =========================
# FEATURE EXTRACTION
# =========================

def extract_features(url):

    parsed = urlparse(url)

    features = {}

    features["url_length"] = len(url)

    features["dots"] = url.count(".")

    features["hyphens"] = url.count("-")

    features["digits"] = sum(
        c.isdigit() for c in url
    )

    features["https"] = (
        1 if parsed.scheme == "https" else 0
    )

    suspicious_words = [
        "login",
        "verify",
        "secure",
        "update",
        "account",
        "bank",
        "paypal",
        "signin",
        "bonus",
        "free"
    ]

    features["suspicious_words"] = sum(
        word in url.lower()
        for word in suspicious_words
    )

    suspicious_tlds = [
        ".xyz",
        ".tk",
        ".ru",
        ".ga",
        ".ml",
        ".cf"
    ]

    features["suspicious_tld"] = (
        1 if any(
            tld in url.lower()
            for tld in suspicious_tlds
        )
        else 0
    )

    return features

# =========================
# CREATE FEATURES
# =========================

feature_list = []

for url in df["url"]:

    feature_list.append(
        extract_features(url)
    )

X = pd.DataFrame(feature_list)

y = df["label"]

# Save feature columns
feature_columns = list(X.columns)

pickle.dump(
    feature_columns,
    open("feature_columns.pkl", "wb")
)

# =========================
# TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# SCALER
# =========================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

pickle.dump(
    scaler,
    open("scaler.pkl", "wb")
)

# =========================
# MODEL
# =========================

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(f"Accuracy: {accuracy * 100:.2f}%")

# Save model
pickle.dump(
    model,
    open("phishing_model.pkl", "wb")
)

print("Model Saved Successfully")