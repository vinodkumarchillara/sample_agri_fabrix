from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
from pydantic import BaseModel
import os
import json
import math

app = FastAPI()

def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)
    
data = load_data()

# Mount the 'static' directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

class Director(BaseModel):
    din: str
    director_name: str
    designation: str
    appointment_date: str

class Record(BaseModel):
    data_id: int
    data_number_of_members: int
    data_company_name: str
    data_registered_address: str
    data_cin: str
    data_active_compliance : str
    data_roc_code : str
    data_registration_number : int
    data_directors: List[Director]

@app.get("/", response_class=HTMLResponse)
async def main_index():
    # Open 'index.html' file in the 'static' directory
    with open(os.path.join("static", "index.html")) as f:
        return f.read()
    
@app.get("/fpo_database", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join("static", "fpo_database.html")) as f:
        return HTMLResponse(content=f.read())

@app.get("/fpo_database/records", response_model=dict)
async def get_records(page: int = 1, per_page: int = 12):  # per_page has a default value of 12
    # Adjust to calculate the start and end index based on the current page
    start = (page - 1) * per_page
    end = start + per_page
    
    # Fetch records based on start and end indices
    records = data[start:end]
    
    # Calculate the total number of pages
    total_pages = math.ceil(len(data) / per_page)
    
    # Return pagination info and the selected records
    return {
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,  # Add total pages
        "records": records
    }

@app.get("/fpo_database/records/{data_id}", response_model=Record)
async def get_record_by_id(data_id: int):
    # Find the record by data_id
    record = next((item for item in data if item['data_id'] == data_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.get("/fpo_database/directors/{data_id}", response_model=List[Director])
async def get_directors_by_company_id(data_id: int):
    # Find the record by data_id
    record = next((item for item in data if item['data_id'] == data_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Return the directors of the found record
    return record['data_directors']
