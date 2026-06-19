from fastapi import FastAPI
from inventory_core import get_products

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SmartStock API Running"}

@app.get("/products")
def products():
    products_df = get_products()

    return products_df.to_dict(orient="records")