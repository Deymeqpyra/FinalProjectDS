from fastapi import FastAPI
from src.routes import marketplace, scrape, product, regrassion, scrape_export

app = FastAPI(docs_url="/docs")


app.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scrape"])
app.include_router(product.router, prefix="/product", tags=["Product"])
app.include_router(regrassion.router, prefix="/regression", tags=["Regression Analysis"]) # Додали цей рядок
app.include_router(scrape_export.router, prefix="/export", tags=["Export"])
