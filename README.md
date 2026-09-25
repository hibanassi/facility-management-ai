# Facility Management AI

AI-powered chatbot for managing employee complaints related to
Facility Management.

## Description

This project provides an intelligent chatbot that allows employees
to report facility-related problems such as:

- Air conditioning
- Plumbing
- Electrical problems
- Furniture
- Cleaning
- Parking
- Landscaping

The chatbot collects the necessary information from the employee
and sends the complaint to the Facility Management team.

## Technologies

### Backend
- Python
- FastAPI
- Ollama
- Qwen3

### Frontend
- React

### Services
- Google Sheets
- Email

## Installation

### Backend

Create a virtual environment:

```bash
python -m venv venv

## Activate it on Windows

.\venv\Scripts\Activate.ps1

## Install dependencies

pip install -r requirements.txt

## Run the backend

uvicorn backend.main:app --reload

### Frontend

cd frontend
npm install
npm run dev


