from smartstock.database.connection import get_connection
import pandas as pd
from sklearn.linear_model import LinearRegression

def forecast_demand():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT product_id, quantity
        FROM OrderItems
    """, conn)

    if df.empty:
        conn.close()
        return pd.DataFrame(columns=["product_id", "predicted_demand"])

    forecasts = []
    cursor = conn.cursor()

    for pid, group in df.groupby("product_id"):
        group = group.reset_index(drop=True)

        if len(group) < 2:
            pred = int(group["quantity"].iloc[-1])
        else:
            group["time"] = range(len(group))
            X = group[["time"]]
            y = group["quantity"]

            model = LinearRegression()
            model.fit(X, y)

            next_time = pd.DataFrame({"time": [len(group)]})
            pred = round(max(0, model.predict(next_time)[0]))

        forecasts.append({
            "product_id": pid,
            "predicted_demand": pred
        })

    conn.close()
    return pd.DataFrame(forecasts)
