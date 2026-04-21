import joblib
import pandas as pd
import pymysql
import time
import random
import sys

import os

print("Script started...")

if not os.path.exists('ml/model.pkl'):
    print("Error: ml/model.pkl not found!")
    exit(1)

print("Loading model...")
# load model
clf = joblib.load('ml/model.pkl')
vectorizer = joblib.load('ml/vectorizer.pkl')
print("Model loaded.")
sys.stdout.flush()

# DB conn
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

def predict_and_save(method, url, ip="127.0.0.1"):
    # feature engineering
    text_feature = f"{method} {url}"
    X_vec = vectorizer.transform([text_feature])
    
    # predict
    prediction_class = clf.predict(X_vec)[0]
    # prediction_class is 0 or 1
    label = "Suspicious" if prediction_class == 1 else "Normal"
    
    # probability
    probs = clf.predict_proba(X_vec)
    confidence = probs[0][prediction_class]
    
    print(f"Analysed: {method} {url} -> {label} ({confidence:.2f})")
    
    # save to DB
    if 'mydb' in globals() and mydb.open:
        sql = "INSERT INTO Log (timestamp, ip_address, request_method, endpoint, status_code, prediction_label, confidence_score) VALUES (NOW(), %s, %s, %s, %s, %s, %s)"
        val = (ip, method, url, 200, label, float(confidence))
        cursor.execute(sql, val)
        mydb.commit()

def run_simulation_loop():
    # methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    # base realistic endpoints
    endpoints = ['/login', '/register', '/api/v1/users', '/api/v2/accounts', '/support', 
                 '/faq', '/admin/settings', '/admin/dashboard', '/orders', '/browse', 
                 '/search', '/contact', '/about', '/products', '/home']
    
    suspicious_patterns = [
        # SQLi
        "'+OR+1=1--",
        "'+OR+2=2--",
        "'+OR+'1'='1",
        "'+OR+'2'='2",
        "a'+OR+'a'='a",
        "b'+OR+'b'='b",
        "';+DELETE+FROM+accounts--",
        "';+DELETE+FROM+users--",
        "';+DROP+TABLE+users--",
        "';+DROP+TABLE+orders--",
        "'+UNION+SELECT+username,+password+FROM+admins--",
        "'+UNION+SELECT+*+FROM+users--",
        "'+UNION+SELECT+*+FROM+credentials--",
        "1;+DROP+TABLE+orders--",
        "1+OR+1=1",
        "1+OR+2=2",
        
        # XSS
        "<script>alert('xss')</script>",
        "<script>alert(\"does+this+work??\")</script>",
        "<script>console.log('im+in')</script>",
        "<img+src=x+onerror=alert(1)>",
        
        # path traversal
        "../../../../etc/passwd",
        "../../../etc/passwd",
        "../../etc/passwd",
        "../etc/passwd",
        "../../../../etc/shadow",
        "../../../etc/shadow",
        "../../etc/shadow",
        "../etc/shadow",
        "cat+/etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "..\\..\\..\\windows\\win.ini",
        "..\\..\\..\\boot.ini",
        "..\\..\\windows\\system32\\drivers\\etc\\hosts",
    ]
    
    normal_params = [
        "?id=", "?sort=asc", "?sort=desc", "?order=asc", "?order=desc", "?page=", 
        "?type=electronics", "?type=clothing", "?category=books", "?category=tech", 
        "?ref=google.com", "?ref=x.com", "?ref=bing.com", "?lang=en"
    ]
    
    # contains suspicious-looking words but normal
    ambiguous_normal = [
        "/products?action=select_color",
        "/home?section=drop_down_menu",
        "/admin/dashboard?tab=table_settings",
        "/search?q=best+scripts+for+beginners",
        "/contact?topic=change+password",
        "/about?ref=union-bank.com",
        "/products?filter=select+size+and+color",
        "/search?q=cat+videos+compilation",
        "/api/v1/users?fields=name,email,role",
        "/home?promo=alert50off",
        "/search?q=how+to+delete+browsing+history",
        "/products?sort=OR+filter+by+price",
        "/about?page=our-executive-table",
        "/contact?subject=drop+off+location",
        "/search?q=passwd+manager+recommendations",
        "/products?tag=script+font+wedding+invitation",
    ]
    
    print("Starting inference loop...")
    while True:
        method = random.choices(
            ["GET", "POST", "PUT", "DELETE", "PATCH"],
            weights=[50, 25, 12.5, 6.25, 6.25]
        )[0]

        url = random.choice(endpoints)
        
        roll = random.random()
        # 20% chance to be suspicious
        if roll < 0.2:
            payload = random.choice(suspicious_patterns)
            
            # select realistic parameter based on the payload type
            if "etc" in payload or "passwd" in payload or ".ini" in payload:
                # path traversal
                param = random.choice(["?file=", "?page=", "?download=", "?template=", "?path=", "?include=", "?load=", "?doc="])
            elif "script" in payload:
                # XSS
                param = random.choice(["?search=", "?query=", "?name=", "?q=", "?comment=", "?input=", "?msg=", "?value="])
            else:
                # SQLi
                param = random.choice(["?id=", "?username=", "?category=", "?sort=", "?user=", "?product=", "?order_id=", "?filter="])
                
            # npr. /home?file=../../etc/passwd
            url += f"{param}{payload}"
        elif roll < 0.28:
            # contains suspicious-looking words but normal
            url = random.choice(ambiguous_normal)
        else:
            # 30% chance to have normal parameters
            if random.random() < 0.3:
                # npr. /api/v1/users?page=2
                url += random.choice(normal_params)

                if "?id=" in url:
                    url += f"{random.randint(1, 500000)}"
                elif "?page=" in url:
                    url += f"{random.randint(1, 50)}"
            
        predict_and_save(method, url)
        time.sleep(2)

if __name__ == "__main__":
    run_simulation_loop()
