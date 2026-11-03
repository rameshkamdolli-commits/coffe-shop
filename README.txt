# ☕ CHAI & COFFEE SHOP – FLASK PROJECT

A full-stack Chai & Coffee Shop web application developed using **Python Flask, HTML, CSS, JavaScript, and SQLite**. It provides an interactive shopping experience with menu browsing, cart management, checkout, billing, chatbot assistance, and an admin dashboard.

## 🚀 Features

### Customer Features
- Attractive home page
- Browse tea, coffee, snacks, desserts, and other products
- Search and filter menu items
- Add products to cart
- Update product quantities and remove items
- Separate shopping cart page
- Checkout and order placement
- Separate bill page with print option
- About Us page
- Contact page
- Interactive chatbot assistant

### Admin Features
- Admin login
- Admin dashboard
- Add and manage products
- Activate or deactivate products
- View customer orders
- Update order status
- View dashboard statistics

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| HTML | Frontend structure |
| CSS | Website styling |
| JavaScript | Interactive functionality |
| SQLite | Database |
| Jinja2 | Dynamic HTML templates |

## 📥 Installation and Setup

### Requirements
- Python 3.10 or above
- Visual Studio Code (recommended)
- Internet connection for remote product images

### Steps to Run Locally

**1. Extract the project ZIP file.**

**2. Open the extracted project folder in VS Code.**

**3. Open the terminal in the project folder.**

**4. Create a virtual environment:**

```bash
python -m venv .venv
```

**5. Activate the virtual environment (Windows):**

```powershell
.venv\Scripts\activate
```

**6. Install the required packages:**

```bash
pip install -r requirements.txt
```

**7. Start the Flask application:**

```bash
python app.py
```

**8. Open the application in your browser:**

http://127.0.0.1:5000

## 🔐 Admin Login (Demo Credentials)

| Field | Value |
|---|---|
| Username | admin |
| Password | admin123 |

## 🤖 Chatbot Information

The project includes a menu-aware, rule-based chatbot that provides predefined responses and product recommendations. It is not connected to a hosted LLM or ChatGPT API.

## 🗄️ Database

SQLite is used to store product and order information during local development. The database is initialized when the application starts.

## ⚠️ Important Notes

- Change the Flask secret key and demo admin credentials before deployment.
- The chatbot is rule-based, not a real AI-powered LLM integration.
- Orders are stored in SQLite locally.
- Checkout is a demo feature and does not process real payments.
- Product photos use remote Unsplash URLs and require an internet connection.
- Vercel deployment requires a persistent database solution such as hosted PostgreSQL and suitable application configuration.
- This project is intended for educational and portfolio purposes.

## 👨‍💻 Developer

**Ramesh**

BCA Student | Python Developer | Full-Stack Web Development

## 📌 Project Purpose

This project was developed to demonstrate practical knowledge of Python web development, Flask, frontend technologies, database operations, and full-stack application development.

---

⭐ If you find this project interesting, feel free to explore the repository!
