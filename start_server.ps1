Write-Host "Starting FastAPI Professor Research & Email API..." -ForegroundColor Green
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Cyan
Write-Host "- GET  /                  : API information"
Write-Host "- POST /scraping          : Scrape professor data"
Write-Host "- POST /email             : Generate personalized email"
Write-Host "- POST /scrape-and-email  : Combined scrape and email"
Write-Host "- GET  /health            : Health check"
Write-Host "- GET  /docs              : Interactive API documentation"
Write-Host ""
python app.py
