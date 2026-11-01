# RISE AI – Student FAQ Assistant

A college-specific FAQ web application built with Flask, SQLite, HTML, CSS and JavaScript.

## Requirements
- Python 3.10+
- VS Code (or another editor)

## Windows 11 setup
Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open http://127.0.0.1:5000

## Local demo admin
- Email: admin@rise.local
- Password: ChangeThisAdmin123!

Change the credentials before deploying publicly. This is a local demonstration setup, not production-ready authentication.

## Database
SQLite database is created automatically at `database/rise_faq.db` on first run.
The starter FAQ content is SAMPLE information. Confirm all college-specific facts, fees, dates and policies with the institution before marking any entry as verified or publishing it.

## Scope
This version is a web application only. Android packaging and Play Store publishing are deferred.
