from fastapi import FastAPI
app = FastAPI(title="Hotello WhatsApp Bot")

@app.get("/health")
async def health():
    return {"status":"ok"}