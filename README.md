# Personal Finance Manager – Project Documentation

## 1. Project Overview
Personal Finance Manager is a Python Flask-based application that helps users manage income,
expenses, and financial records. The system allows users to record transactions, categorize them,
and analyze spending patterns. The project is designed for learning, portfolio use, and personal
financial tracking.

## 2. Setup Instructions
Prerequisites: Python 3.8+, pip, virtual environment, database (SQLite/MySQL/MongoDB).
Steps to run the project:
1 Clone the repository from GitHub
2 Create and activate a virtual environment
3 Install dependencies using requirements.txt
4 Configure database settings in config.py
5 Initialize the database
6 Run the Flask application
7 Open the browser at http://localhost:5000

## 3. Code Structure
The project follows a modular structure. app.py is the main Flask application file. The finance
module contains transaction, category, and user logic. Templates and static folders manage
frontend UI and assets.

## 4. Visual Documentation
The application includes UI screens such as Login, Dashboard, Transaction List, Add Transaction
Form, and Category Management. Screenshots can be added in the docs folder

## 5. Technical Details
Backend: Flask framework with REST APIs. Frontend: HTML, CSS, JavaScript. Database: SQLite
(default). Authentication: Session-based.

## 6. Testing Evidence
Manual testing was performed for user authentication, adding transactions, viewing summaries, and
logout functionality. All core features were tested successfully.

## 7. Future Enhancements
1 Add data visualization charts
2 Multi-currency support
3 Mobile-friendly UI
4 Advanced analytics and reports

#  8. License
This project is released under the MIT License
