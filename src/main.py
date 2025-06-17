from fastapi import FastAPI
from routes import marketplace, scrape, product


app = FastAPI(docs_url="/docs")


app.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scrape"])
app.include_router(product.router, prefix="/product", tags=["Product"])
