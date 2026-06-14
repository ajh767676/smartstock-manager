# SmartStock Manager

![Python Badge](https://img.shields.io/badge/Python-3.11-blue)
![SQLite Badge](https://img.shields.io/badge/Database-SQLite-green)
![Streamlit Badge](https://img.shields.io/badge/UI-Streamlit-red)
![Scikit-Learn Badge](https://img.shields.io/badge/ML-Scikit--Learn-orange)

AI-powered inventory and order management system built with Python, SQLite, Streamlit, Plotly, and machine learning forecasting.

## Live Demo

https://smartstock-manager.streamlit.app/

Demo users can:
- Load sample store data
- Manage inventory
- Create customer orders
- Use a shopping cart checkout
- View analytics and AI forecasting

### Demo Access

Use the built-in Demo User option on the login page or create your own account.

---

## Features

### Inventory Management
- Add, edit, and delete products
- Inventory quantity tracking
- Product image support
- Low-stock alerts
- Inventory value calculations

### Order Management
- Create customer orders
- Automatic inventory updates
- Order history tracking
- Order cancellation with inventory restoration

### Analytics Dashboard
- Revenue tracking
- Best-selling product identification
- Inventory value metrics
- Sales analytics visualizations

### AI Forecasting
- Demand forecasting using Linear Regression
- Smart reorder recommendations
- Inventory planning support

### Data Import / Export
- CSV product import
- CSV product export
- Bulk inventory updates

### Security
- User registration
- User authentication
- Password hashing
- Session management

---

## Technologies Used

- Python
- SQLite
- Streamlit
- Pandas
- Plotly
- Scikit-Learn
- Git / GitHub

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ajh767676/smartstock-manager.git
cd smartstock-manager
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## Screenshots

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Product Management

![Products](screenshots/products.png)

### AI Forecasting

![AI Forecast](screenshots/ai-forecast.png)

---

## Project Purpose

SmartStock Manager was developed as a Computer Science capstone project to demonstrate:

- Software Development
- Database Design
- Data Analytics
- Machine Learning Integration
- User Authentication
- Business Process Automation

The project simulates a real-world inventory and order management platform for small businesses.

---

## Future Enhancements

- User role management (Admin / Employee)
- Enhanced forecasting models
- Cloud database integration
- Email notifications for low inventory
- REST API integration