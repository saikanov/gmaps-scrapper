from fastapi import FastAPI, HTTPException, Request
import httpx
import os

app = FastAPI()

# Read from environment, default to empty string
GOOGLE_SHEET_WEB_APP_URL = os.environ.get("GOOGLE_SHEET_WEB_APP_URL", "")

@app.post("/api/sheets/add")
async def add_to_sheet(request: Request):
    if not GOOGLE_SHEET_WEB_APP_URL:
        # Do not allow action if URL is missing
        raise HTTPException(status_code=500, detail="Google Sheets Webhook URL not configured on backend.")
        
    try:
        # Get JSON payload from request body
        payload = await request.json()
        
        # Forward request to Google Sheets App Script
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                GOOGLE_SHEET_WEB_APP_URL, 
                json=payload
            )
            
            # Simple check if there was an HTTP error on the Google end
            if response.status_code >= 400:
                raise HTTPException(status_code=502, detail=f"Target URL responded with code {response.status_code}")
                
            return {"status": "success"}

    except Exception as e:
        print(f"Error forwarding request to Google Sheets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process or forward request.")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "webhook_configured": bool(GOOGLE_SHEET_WEB_APP_URL)}
