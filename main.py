from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

# CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the Pydantic model
class Employer(BaseModel):
    company_name: str
    contact_email: str
    employee_count: int

@app.post("/submit")
async def submit_employer(data: Employer):
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME")
        )
        cursor = conn.cursor()
        query = """INSERT INTO employers (company_name, contact_email, employee_count)
                   VALUES (%s, %s, %s)"""
        values = (data.company_name, data.contact_email, data.employee_count)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Employer submitted successfully"}
    except Exception as e:
        return {"error": str(e)}