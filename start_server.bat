@echo off
echo Starting FastAPI Professor Research & Email API...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo.
echo Available endpoints:
echo - GET  /                  : API information
echo - POST /scraping          : Scrape professor data
echo - POST /email             : Generate personalized email
echo - POST /scrape-and-email  : Combined scrape and email
echo - GET  /health            : Health check
echo - GET  /docs              : Interactive API documentation
echo.
python app.py
