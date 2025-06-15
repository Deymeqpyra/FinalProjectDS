from fastapi import FastAPI
from routes import marketplace, scrape


app = FastAPI(docs_url="/docs")


app.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
app.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
