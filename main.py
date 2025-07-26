
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def create_tables():
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            dbname=os.environ.get("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            employee_count INT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            employer_id INT NOT NULL,
            dob DATE,
            gender VARCHAR(50),
            salary DECIMAL(10,2),
            smoker_status BOOLEAN,
            dependents INT,
            occupation_type VARCHAR(100),
            FOREIGN KEY (employer_id) REFERENCES employers(id)
        );

        CREATE TABLE IF NOT EXISTS claims_history (
            id SERIAL PRIMARY KEY,
            employer_id INT NOT NULL,
            line_of_coverage VARCHAR(100),
            month DATE,
            claim_amount DECIMAL(10,2),
            FOREIGN KEY (employer_id) REFERENCES employers(id)
        );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tables created or already exist.")
    except Exception as e:
        print("❌ Error creating tables:", str(e))

@app.get("/")
def root():
    return {"message": "Schema creation endpoint live"}
