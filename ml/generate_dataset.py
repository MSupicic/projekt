import pandas as pd
import random

def generate_dataset(num_samples=1000):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    endpoints = ['/login', '/home', '/api/data', '/contact', '/about', '/admin']
    suspicious_patterns = [
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "cat /etc/passwd",
        "DROP TABLE users"
    ]
    
    data = []
    
    for _ in range(num_samples):
        is_suspicious = random.random() < 0.2
        method = random.choice(methods)
        
        if is_suspicious:
            base = random.choice(endpoints)
            pattern = random.choice(suspicious_patterns)
            # Suspicious is often POST or GET with payload in URL/Body (simplified here as URL part)
            url = f"{base}?q={pattern}"
            label = 'Suspicious'
        else:
            url = random.choice(endpoints)
            # Add some random params
            if random.random() < 0.3:
                url += f"?id={random.randint(1, 1000)}"
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
