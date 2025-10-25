VALORA Backend (Ready)
======================

Quickstart (Windows - PowerShell)
1. Ensure you have Python 3.12+ installed and on PATH (python --version)
2. Extract this folder.
3. Open PowerShell in the extracted folder and run:
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   # edit .env to add Algorand keys if you plan to enable on-chain submitter
   python run.py
4. Visit http://127.0.0.1:8000/docs to use the API Swagger UI.
