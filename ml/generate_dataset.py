import pandas as pd
import random

def generate_dataset(num_samples=10000):
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
        "cat+/etc/shadow",
        "cat+../etc/passwd",
        "cat+../etc/shadow",
        "cat+../../etc/passwd",
        "cat+../../etc/shadow",
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
    
    # suspicious-looking words but normal
    ambiguous_normal = [
        "/api/v2/accounts?action=select_all",
        "/orders?action=drop_filter",
        "/admin/settings?tab=user_table",
        "/browse?category=scripts&page=2",
        "/support?topic=password_reset",
        "/faq?q=how+to+select+a+plan",
        "/orders?status=etc&order=desc",
        "/api/v2/accounts?fields=username,role",
        "/admin/settings?view=union_members",
        "/support?q=delete+my+account+please",
        "/orders?filter=1+OR+more+items",
        "/browse?search=table+decorations+for+wedding",
        "/faq?q=how+to+drop+a+course",
        "/register?ref=alert-service.com",
        "/browse?search=script+writing+course",
        "/faq?q=forgot+password+what+do+I+do",
        "/support?q=cat+food+delivery+options",
        "/orders?note=from+etc+to+home+address",
    ]
    
    data = []
    
    for _ in range(num_samples):
        roll = random.random()
        method = random.choices(
            ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
            weights=[50, 30, 10, 5, 5]
        )[0]
        
        if roll < 0.20:
            # suspicious
            base = random.choice(endpoints)
            payload = random.choice(suspicious_patterns)
            
            # context-aware parameter
            if "etc" in payload or "passwd" in payload or "shadow" in payload or "windows" in payload or ".ini" in payload:
                # path traversal
                param = random.choice(["?file=", "?page=", "?download=", "?template=", "?path=", "?include=", "?load=", "?doc="])
            elif "script" in payload or "onerror" in payload:
                # XSS
                param = random.choice(["?search=", "?query=", "?name=", "?q=", "?comment=", "?input=", "?msg=", "?value="])
            else:
                # SQLi
                param = random.choice(["?id=", "?username=", "?category=", "?sort=", "?user=", "?product=", "?order_id=", "?filter="])                
            url = f"{base}{param}{payload}"
            label = 'Suspicious'
        elif roll < 0.28:
            # contains suspicious-looking words
            url = random.choice(ambiguous_normal)
            label = 'Normal'
        else:
            url = random.choice(endpoints)
            # 30% chance to have normal parameters
            if random.random() < 0.3:
                url += random.choice(normal_params)
                
                if "?id=" in url:
                    url += f"{random.randint(1, 500000)}"
                elif "?page=" in url:
                    url += f"{random.randint(1, 50)}"
            label = 'Normal'
            
        data.append({
            'method': method,
            'url': url,
            'label': label
        })
        
    df = pd.DataFrame(data)
    df.to_csv('ml/train_data.csv', index=False)
    print(f"Generated {num_samples} samples to ml/train_data.csv")

if __name__ == "__main__":
    generate_dataset()
