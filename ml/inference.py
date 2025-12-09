import joblib
import pandas as pd
import pymysql
import time
import random
import sys

import os

print("Script started...")

# Check files
if not os.path.exists('ml/model.pkl'):
    print("Error: ml/model.pkl not found!")
    exit(1)

print("Loading model...")
# Load model
clf = joblib.load('ml/model.pkl')
vectorizer = joblib.load('ml/vectorizer.pkl')
print("Model loaded.")
sys.stdout.flush()

# DB Connection
print("Attempting to connect to DB at localhost:3307...")
sys.stdout.flush()
try:
    mydb = pymysql.connect(
      host="localhost",
      user="ids_user",
      password="ids_password",
      database="ids_db",
      port=3307
    )
    cursor = mydb.cursor()
    print("Combined to Database")
    sys.stdout.flush()
except Exception as e:
    print(f"Error connecting to DB: {e}")
    sys.stdout.flush()
    # Fallback/Retry logic could go here

def predict_and_save(method, url, ip="127.0.0.1"):
    # Feature engineering
    text_feature = f"{method} {url}"
    X_vec = vectorizer.transform([text_feature])
    
    # Predict
    prediction_class = clf.predict(X_vec)[0]
    # prediction_class is 0 or 1
    label = "Suspicious" if prediction_class == 1 else "Normal"
    
    # Probability
    probs = clf.predict_proba(X_vec)
    confidence = probs[0][prediction_class]
    
    print(f"Analysed: {method} {url} -> {label} ({confidence:.2f})")
    
    # Save to DB
    if 'mydb' in globals() and mydb.open:
        sql = "INSERT INTO Log (timestamp, ip_address, request_method, endpoint, status_code, prediction_label, confidence_score) VALUES (NOW(), %s, %s, %s, %s, %s, %s)"
        val = (ip, method, url, 200, label, float(confidence))
        cursor.execute(sql, val)
        mydb.commit()

def run_simulation_loop():
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    endpoints = ['/login', '/home', '/api/data', '/contact', '/about', '/admin', '/search?q=test', '/search?q=<script>']
    
    print("Starting inference loop...")
    while True:
        method = random.choice(methods)
        url = random.choice(endpoints)
        if random.random() < 0.1:
            url += "' OR '1'='1"
            
        predict_and_save(method, url)
        time.sleep(2)

if __name__ == "__main__":
    run_simulation_loop()
