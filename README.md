# Intrusion Detection System Dashboard

This project is a full-stack system simulating network traffic, running an ML model to classify requests as 'Normal' or 'Suspicious', and visualizing the results on a real-time web dashboard.

## Project Structure

### Machine Learning (`ml/`)
- **`generate_dataset.py`**: Generates the initial CSV of synthetic regular and malicious HTTP requests used to train the model.
- **`train_model.py`**: Trains a Random Forest Classifier with TF-IDF vectorization and saves the artifacts (`model.pkl` and `vectorizer.pkl`).
- **`inference.py`**: Runs an infinite loop that continually generates simulated traffic, predicts if it's an intrusion, and saves the logs directly to the MySQL database.

### Web Dashboard (`web/`)
- **`app/`**: Contains the Next.js application consisting of the frontend dashboard and the API routes that read logs and stats from the database.
- **`prisma/`**: Contains the database schema (`schema.prisma`) defining the `Log` table.
- **`.env`**: Stores the connection string so the Web App can talk to the Docker database.

### Database (`docker-compose.yml`)
- Provides a containerized MySQL database serving as the bridge between the ML script and the Web dashboard.

---

## How to Run the Project

You will need three terminal windows to run all components simultaneously.

### 1. Start the Database
From the root directory of the project, start the MySQL database:
```bash
docker-compose up -d
```

### 2. Start the Web Dashboard
Open a new terminal, navigate to the `web/` folder, and configure the application:
```bash
cd web
npm install          # Install dependencies
npx prisma db push   # Initialize database tables
npm run dev          # Start the dashboard on http://localhost:3000
```

### 3. Run the ML Pipeline
Open a third terminal, activate your Python virtual environment, and run the scripts:
```bash
source venv/bin/activate
pip install -r ml/requirements.txt # Ensure packages are installed

python ml/generate_dataset.py      # Generate training data
python ml/train_model.py           # Train the model
python ml/inference.py             # Start predicting and writing logs to the DB
```
