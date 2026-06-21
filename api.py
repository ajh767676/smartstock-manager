from fastapi import FastAPI
from inventory_core import get_products, get_orders_with_total, forecast_demand_df

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SmartStock API Running"}

@app.get("/orders")
def orders():
    orders_df = get_orders_with_total()

    return orders_df.to_dict(orient="records")

@app.get("/products")
def products():
    products_df = get_products()

    return products_df.to_dict(orient="records")

@app.get("/forecast")
def forecast():
    forecast_df = forecast_demand_df()

    return forecast_df.to_dict(orient="records")