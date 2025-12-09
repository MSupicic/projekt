import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Load dataset
def load_data():
    # Placeholder for loading from the downloaded CSVs
    # Assuming the zip is extracted and files are available
    # For now, we will create a dummy dataset if files are missing or implement the loading logic
    
    # Check if files exist
    if not os.path.exists('ml/train_data.csv'):
        print("Dataset not found. Please run generate_dataset.py.")
        # Create dummy data for testing the flow
        data = {
            'method': ['GET', 'POST', 'GET', 'POST', 'GET'],
            'url': ['/index.html', '/login', '/api/data', '/admin/exec', '/about'],
            'label': ['Normal', 'Normal', 'Normal', 'Suspicious', 'Normal']
        }
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv('ml/train_data.csv')
    
    return df

def train():
    df = load_data()
    
    # Simple Feature Engineering
    # Treat method and url as text features
    df['text'] = df['method'] + " " + df['url']
    
    X = df['text']
    y = df['label'].apply(lambda x: 1 if x == 'Suspicious' else 0)
    
    # Vectorization
    vectorizer = TfidfVectorizer()
    X_vec = vectorizer.fit_transform(X)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)
    
    # Model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save artifacts
    joblib.dump(clf, 'ml/model.pkl')
    joblib.dump(vectorizer, 'ml/vectorizer.pkl')
    print("Model and vectorizer saved to ml/")

if __name__ == "__main__":
    train()
