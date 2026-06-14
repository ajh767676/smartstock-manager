import streamlit as st
import plotly.express as px
import os
import base64
import pandas as pd
import random
from datetime import datetime, timedelta

from inventory_core import (
    get_products,
    get_total_revenue,
    get_best_selling_product,
    get_sales_by_product,
    forecast_demand_df,
    smart_reorder_df,
    get_low_stock_items,
    get_system_report,
    create_order_db,
    add_product_db,
    authenticate_user,
    create_user,
    reset_database,
    get_revenue_over_time,
    update_product,
    update_product_quantity,
    delete_product_db,
    get_inventory_value,
    delete_order_db,
    init_database,
    create_cart_order_db
)

def img_to_base64(path):
    try:
        # Try actual image first
        if path and isinstance(path, str):
            full_path = os.path.join("images", path)
        else:
            full_path = None

        # fallback to placeholder
        if not full_path or not os.path.exists(full_path):
            full_path = os.path.join("images", "placeholder.jpg")

        # still missing → safe return
        if not os.path.exists(full_path):
            return ""

        with open(full_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        ext = full_path.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"

        return f"data:{mime};base64,{encoded}"

    except:
        return ""


init_database()
# Page config
st.set_page_config(page_title="Inventory Dashboard", layout="wide")

from inventory_core import authenticate_user, create_user

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")
    if st.button("Continue as Demo User"):
        st.session_state["logged_in"] = True
        st.rerun()

    st.info("No account? Create one below.")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        if create_user(new_user, new_pass):
            st.success("Account created! You can now log in.")
        else:
            st.error("Username already exists.")

    st.stop()

# Sidebar (after Page Config)
st.sidebar.title("🧠 SmartStock Manager")
st.sidebar.markdown("Convenience store inventory, sales, and AI forecasting system")
st.sidebar.markdown("---")


# Sidebar navigation
section = st.sidebar.selectbox(
    "Section",
    ["Dashboard", "Management", "Insights"]
)

if section == "Dashboard":
    page = "Dashboard"
elif section == "Management":
    page = st.sidebar.radio("", ["Products", "Orders"])

elif section == "Insights":
    page = st.sidebar.radio("", ["Analytics", "AI Forecast"])
st.sidebar.markdown("---")

if st.sidebar.button("🎯 Load Sample Store Data"):
    reset_database()
    st.success("Demo data loaded successfully!")
    st.rerun()
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()


# ================= DASHBOARD =================
if page == "Dashboard":

    st.markdown("## 📊 Dashboard")
    st.caption("Overview of inventory, revenue, and system status.")

    products = get_products()
    revenue = get_total_revenue()
    best = get_best_selling_product()
    low_stock = get_low_stock_items()
    inventory_value = get_inventory_value()

    # ================= METRICS =================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 Total Products", len(products))
    col2.metric("💰 Total Revenue", f"${revenue:.2f}")

    if best:
        col3.metric(
            "🏆 Best Seller",
            best["name"].title(),
            f"{best['total_sold']} sold"
        )
    else:
        col3.metric("🏆 Best Seller", "N/A")
    col4.metric(
        "💲 Inventory Value",
        f"${inventory_value:,.2f}"
    )

    st.divider()

    # ================= SYSTEM STATUS =================
    st.subheader("⚙ System Status")

    if len(low_stock) > 0:
        st.error(f"⚠ {len(low_stock)} items need restocking")
    else:
        st.success("✅ All systems operating normally")

    st.divider()

    # ================= LOW STOCK =================
    st.subheader("⚠ Low Stock Items")

    if low_stock.empty:
        st.success("All inventory levels look good.")
    else:
        low_stock["name"] = low_stock["name"].str.title()

        st.dataframe(
            low_stock[["name", "quantity", "reorder_level"]],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # ================= PRODUCT TABLE =================
    st.subheader("📋 Inventory Overview")

    display_df = products.copy()
    display_df["name"] = display_df["name"].str.title()
    display_df["price"] = display_df["price"].apply(lambda x: f"${x:.2f}")

    display_df = display_df[["name", "price", "quantity", "reorder_level"]]

    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ================= PRODUCTS =================
elif page == "Products":

    st.markdown("<h1 style='text-align: center;'>📦 Product Management</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])

    # ================= LEFT =================
    with col1:

        # ✅ Messages
        if "product_added" in st.session_state:
            st.success(st.session_state["product_added"])
            del st.session_state["product_added"]
        
        if "product_updated" in st.session_state:
            st.success(st.session_state["product_updated"])
            del st.session_state["product_updated"]

        if "product_error" in st.session_state:
            st.error(st.session_state["product_error"])
            del st.session_state["product_error"]
        
        if "csv_import_success" in st.session_state:
            st.success(st.session_state["csv_import_success"])
            del st.session_state["csv_import_success"]

        # ✅ Action menu
        action = st.selectbox(
            "Choose Product Action",
            ["Add Product", "Edit Product", "Delete Product", "Import CSV"],
            key="product_action"
        )
        
        st.markdown("---")
        # ================= ADD =================
        if action == "Add Product":
            st.markdown("### ➕ Add Product")

            with st.form("add_product_form", clear_on_submit=True):
                name = st.text_input("Product Name")
                price = st.number_input("Price ($)", min_value=0.0)
                quantity = st.number_input("Quantity", min_value=0)
                reorder_level = st.number_input("Reorder Level", min_value=0)

                submitted = st.form_submit_button("Add Product")

            if submitted:
                result = add_product_db(name, price, quantity, reorder_level, None)

                if result["success"]:
                    st.session_state["product_added"] = result["message"]
                else:
                    st.session_state["product_error"] = result["message"]

                st.rerun()

        # ================= EDIT =================
        elif action == "Edit Product":
            st.markdown("### ✏️ Edit Product")

            products = get_products()

            if products.empty:
                st.warning("No products available")
            else:
                product_map = {row["name"]: row["product_id"] for _, row in products.iterrows()}

                selected = st.selectbox(
                    "Select Product",
                    list(product_map.keys()),
                    key="edit_product"
                )

                pid = product_map[selected]
                current = products[products["product_id"] == pid].iloc[0]

                new_name = st.text_input("New Name", value=current["name"])
                new_price = st.number_input("New Price", value=float(current["price"]))
                new_qty = st.number_input("New Quantity", value=int(current["quantity"]))
                new_rl = st.number_input("New Reorder Level", value=int(current["reorder_level"]))

                if st.button("Update Product"):
                    result = update_product(pid, new_name, new_price, new_qty, new_rl)

                    if result["success"]:
                        st.session_state["product_updated"] = result["message"]

                        
                
                    else:
                        st.session_state["product_error"] = result["message"]

                    st.rerun()

        # ================= DELETE =================
        elif action == "Delete Product":
            st.markdown("### 🗑 Delete Product")

            products = get_products()

            if products.empty:
                st.warning("No products available")
            else:
                product_map = {row["name"]: row["product_id"] for _, row in products.iterrows()}

                delete_name = st.selectbox(
                    "Select Product",
                    list(product_map.keys()),
                    key="delete_product"
                )

                confirm = st.checkbox("Confirm delete")

                if st.button("Delete Product"):
                    if confirm:
                        delete_product_db(product_map[delete_name])
                        st.success("Product deleted")
                        st.rerun()
                    else:
                        st.warning("Please confirm deletion")
       

        # ================= CSV Upload =================

        elif action == "Import CSV":

            st.markdown("### 📂 Import Products CSV")

            uploaded_file = st.file_uploader(
                "Upload CSV File",
                type=["csv"]
            )

            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)

                existing_products = get_products()

                duplicates = []

                for product_name in df["name"]:
                    if product_name.lower() in existing_products["name"].str.lower().values:
                        duplicates.append(product_name)

                if duplicates:
                    st.warning(
                        f"Products already exist and quantities will be added: {', '.join(duplicates)}"
                    )

                required_columns = {"name", "price", "quantity", "reorder_level"}

                if not required_columns.issubset(df.columns):
                    st.error("CSV must contain: name, price, quantity, reorder_level")
                else:
                    st.dataframe(df, use_container_width=True)

                    if st.button("Import Products"):
                        imported_count = 0

                        for _, row in df.iterrows():
                            result = add_product_db(
                                row["name"],
                                float(row["price"]),
                                int(row["quantity"]),
                                int(row["reorder_level"]),
                                None
                            )

                            if result["success"]:
                                imported_count += 1

                        st.session_state["csv_import_success"] = f"Imported {imported_count} products successfully!"
                        st.rerun()

        st.divider()

    # ================= RIGHT SIDE =================
    with col2:
        st.markdown("### 📋 Inventory")

        products = get_products()

        if products.empty:
            st.warning("No products yet")
        else:
            # SEARCH
            search = st.text_input("🔍 Search product")

            if search:
                products = products[products["name"].str.contains(search, case=False, na=False)]

            # CLEAN TABLE
            display_df = products.copy()

            display_df["name"] = display_df["name"].str.title()
            display_df["price"] = display_df["price"].apply(lambda x: f"${x:.2f}")

            display_df = display_df[["name", "price", "quantity", "reorder_level"]]

            st.dataframe(display_df, use_container_width=True, hide_index=True)


            # ⚠️ LOW STOCK
            low_stock = products[products["quantity"] <= products["reorder_level"]]

            if not low_stock.empty:
                st.warning("⚠️ Low stock items:")
                st.dataframe(low_stock[["name", "quantity", "reorder_level"]])

            # DOWNLOAD
            csv = products.to_csv(index=False)
            st.download_button("📤 Download Products CSV", data=csv, file_name="products.csv")

# ================= ANALYTICS =================
elif page == "Analytics":

    st.markdown("## 📊 Analytics Dashboard")
    st.caption("Track product performance and revenue trends for smarter decisions")

    # ================= SALES OVERVIEW =================
    st.subheader("📊 Sales Overview")

    df = get_sales_by_product()

    if df.empty:
        st.warning("No sales data yet.")
    else:
        # Clean product names
        df["name"] = df["name"].str.title()

        col1, col2 = st.columns([3, 1])

        # Bar Chart
        fig = px.bar(
            df,
            x="name",
            y="total_sold"
        )

        fig.update_layout(
            yaxis_title="Units Sold",
            xaxis_title="Product",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        col1.plotly_chart(fig, use_container_width=True)

        # Top Performer Card
        with col2:
            top = df.iloc[0]

            st.markdown("### 🏆 Top Performer")
            st.metric("Product", top["name"])
            st.metric("Units Sold", int(top["total_sold"]))

    # ================= REVENUE =================
    st.divider()
    st.subheader("📈 Revenue Trend")

    trend_df = get_revenue_over_time()

    if trend_df.empty:
        st.warning("No dated order data yet.")
    else:
        # Clean data
        trend_df["order_date"] = pd.to_datetime(trend_df["order_date"]).dt.strftime("%b %d")
        trend_df["revenue"] = trend_df["revenue"].round(2)

        fig2 = px.line(
            trend_df,
            x="order_date",
            y="revenue"
        )

        fig2.update_layout(
            yaxis_title="Revenue ($)",
            xaxis_title="Date",
            yaxis_tickprefix="$",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        fig2.update_traces(
            hovertemplate="Date: %{x}<br>Revenue: $%{y:.2f}<extra></extra>"
        )

        st.plotly_chart(fig2, use_container_width=True)

# ================= AI FORECAST =================
elif page == "AI Forecast":

    st.markdown("## 🤖 AI Forecasting")
    st.info("""
    🤖 This system uses Linear Regression to predict future demand.

    • It looks at past sales for each product  
    • Tracks how demand changes over time  
    • Predicts the next expected value  

    This helps businesses avoid overstocking or running out of products.
    """)
    st.caption("Predict demand and get smart reorder recommendations using machine learning")

    # ================= FORECAST =================
    st.subheader("📊 Demand Prediction")

    st.caption("Predictions based on historical order trends using linear regression")

    forecast_df = forecast_demand_df()

    if forecast_df is None or forecast_df.empty:
        st.warning("Not enough data for forecasting.")
    else:
        # Clean names
        forecast_df["name"] = forecast_df["name"].str.title()

        col1, col2 = st.columns([2, 3])

        # Table
        col1.dataframe(
            forecast_df[["name", "predicted_demand"]],
            use_container_width=True,
            hide_index=True
        )

        # Chart
        fig = px.bar(
            forecast_df,
            x="name",
            y="predicted_demand"
        )

        fig.update_layout(
            yaxis_title="Predicted Demand",
            xaxis_title="Product",
            margin=dict(l=10, r=10, t=20, b=10)
        )

        col2.plotly_chart(fig, use_container_width=True)

    # ================= REORDER =================
    st.divider()
    st.subheader("📦 Smart Reorder Recommendations")

    reorder_df = smart_reorder_df()

    if reorder_df.empty:
        st.warning("No product data available.")
    else:
        # Alerts (cleaner)
        issues = reorder_df[reorder_df["status"] != "OK"]

        if not issues.empty:
            st.warning("⚠ Products needing attention:")

            for _, row in issues.iterrows():
                st.write(
                    f"• **{row['name'].title()}** needs **{row['suggested_reorder']}** units "
                    f"(predicted: {row['predicted_demand']}, stock: {row['current_stock']})"
                )

        # Table styling
        def highlight_status(row):
            if row["status"] == "CRITICAL":
                return ["background-color: #ff1a1a"] * len(row)
            elif row["status"] == "LOW":
                return ["background-color: #ff944d"] * len(row)
            elif row["status"] == "REORDER":
                return ["background-color: #f4a261; color: black"] * len(row)
            else:
                return ["background-color: #2ecc71"] * len(row)

        styled_df = reorder_df.style.apply(highlight_status, axis=1)

        st.dataframe(styled_df, use_container_width=True)

        # Summary message
        reorder_count = len(issues)

        if reorder_count > 0:
            st.error(f"⚠ {reorder_count} products need attention!")
        else:
            st.success("✅ All inventory levels are healthy.")

# ================= ORDERS =================
elif page == "Orders":

    if "cart" not in st.session_state:
        st.session_state["cart"] = []

    st.subheader("🛒 Shopping Cart")

    products = get_products()

    if products.empty:
        st.warning("No products available.")

    else:
        product_map = {
            row["name"]: row["product_id"]
            for _, row in products.iterrows()
        }

        product_name = st.selectbox(
            "Select Product",
            list(product_map.keys())
        )

        pid = product_map[product_name]
        current = products[products["product_id"] == pid].iloc[0]

        max_qty = int(current["quantity"])

        st.caption(f"Available stock: {max_qty}")

        if max_qty <= 0:
            st.warning("⚠️ Out of stock")

        else:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=max_qty
            )

            if st.button("Add to Cart"):
                stock = int(current["quantity"])

                if quantity > stock:
                    st.error(f"❌ Not enough inventory. Available: {stock}")
                else:
                    st.session_state["cart"].append({
                        "product_id": pid,
                        "name": product_name,
                        "quantity": quantity,
                        "price": float(current["price"])
                    })

                    st.success(f"Added {quantity} {product_name} to cart")
                    st.rerun()

        # ================= CART DISPLAY =================
        if st.session_state["cart"]:
            st.subheader("🛒 Cart")

            cart_df = pd.DataFrame(st.session_state["cart"])
            cart_df["total"] = cart_df["quantity"] * cart_df["price"]

            display_cart = cart_df[["name", "quantity", "price", "total"]].copy()
            display_cart["name"] = display_cart["name"].str.title()
            display_cart["price"] = display_cart["price"].apply(lambda x: f"${x:.2f}")
            display_cart["total"] = display_cart["total"].apply(lambda x: f"${x:.2f}")

            st.dataframe(
                display_cart,
                use_container_width=True,
                hide_index=True
            )

            subtotal = cart_df["total"].sum()
            tax = subtotal * 0.085
            grand_total = subtotal + tax

            st.write(f"**Subtotal:** ${subtotal:.2f}")
            st.write(f"**Tax:** ${tax:.2f}")
            st.subheader(f"💰 Total: ${grand_total:.2f}")

            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Card", "Mobile Pay"]
            )

            col_checkout, col_clear = st.columns(2)

            with col_checkout:
                if st.button("Checkout"):
                    result = create_cart_order_db(st.session_state["cart"])

                    if result["success"]:
                        st.session_state["last_receipt"] = {
                            "order_id": result["order_id"],
                            "items": st.session_state["cart"].copy(),
                            "subtotal": subtotal,
                            "tax": tax,
                            "grand_total": grand_total,
                            "payment_method": payment_method
                        }

                        st.session_state["cart"] = []
                        st.success(result["message"])
                        st.rerun()

                    else:
                        st.error(result["message"])

            with col_clear:
                if st.button("Clear Cart"):
                    st.session_state["cart"] = []
                    st.rerun()

        # ================= RECEIPT =================
        if "last_receipt" in st.session_state:
            receipt = st.session_state["last_receipt"]

            st.divider()
            st.subheader("🧾 Receipt")

            st.write(f"**Order #{receipt['order_id']}**")

            for item in receipt["items"]:
                line_total = item["quantity"] * item["price"]
                st.write(
                    f"- {item['name'].title()} x{item['quantity']} — ${line_total:.2f}"
                )

            st.write(f"**Subtotal:** ${receipt['subtotal']:.2f}")
            st.write(f"**Tax:** ${receipt['tax']:.2f}")
            st.write(f"**Total:** ${receipt['grand_total']:.2f}")
            st.write(f"**Payment:** {receipt['payment_method']}")

            receipt_text = f"SmartStock Manager Receipt\n"
            receipt_text += f"Order #{receipt['order_id']}\n\n"

            for item in receipt["items"]:
                line_total = item["quantity"] * item["price"]
                receipt_text += f"{item['name'].title()} x{item['quantity']} - ${line_total:.2f}\n"

            receipt_text += f"\nSubtotal: ${receipt['subtotal']:.2f}"
            receipt_text += f"\nTax: ${receipt['tax']:.2f}"
            receipt_text += f"\nTotal: ${receipt['grand_total']:.2f}"
            receipt_text += f"\nPayment: {receipt['payment_method']}"

            st.download_button(
                "📄 Download Receipt",
                data=receipt_text,
                file_name=f"receipt_{receipt['order_id']}.txt",
                mime="text/plain"
            )

        st.divider()

        # ================= ORDER HISTORY =================
        st.subheader("📋 Order History")

        from inventory_core import get_orders_with_total

        try:
            orders = get_orders_with_total()
        except:
            orders = pd.DataFrame()
            st.error("Error loading orders")

        search_orders = st.text_input("🔍 Search orders by product")

        if search_orders and not orders.empty:
            orders = orders[orders["name"].str.contains(search_orders, case=False)]

        if not orders.empty:
            orders["price"] = orders["price"].apply(lambda x: f"${x:.2f}")
            orders["total_price"] = orders["total_price"].apply(lambda x: f"${x:.2f}")

            display_orders = orders.drop(columns=["product_id"])

            display_orders = display_orders.rename(columns={
                "order_id": "Order ID",
                "name": "Product",
                "quantity": "Quantity",
                "price": "Price",
                "total_price": "Total"
            })

            display_orders["Product"] = display_orders["Product"].str.title()

            st.dataframe(
                display_orders,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("❌ Cancel Order")

            order_ids = sorted(orders["order_id"].unique())

            selected_order = st.selectbox(
                "Select Order to Cancel",
                order_ids
            )

            if st.button("Cancel Selected Order"):
                result = delete_order_db(selected_order)

                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])

        else:
            st.info("No orders yet.")


