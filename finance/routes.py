# finance/routes.py
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import db
from .models import User, Transaction

auth_bp = Blueprint('auth', __name__, url_prefix="")
main_bp = Blueprint('main', __name__, url_prefix="")

# Auth routes ----------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", register=False)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Provide username and password", "warning")
            return render_template("register.html", error=None)
        if User.query.filter_by(username=username).first():
            flash("User already exists", "danger")
            return render_template("register.html", error="User already exists")
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", error=None)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# Main functioning routes ----------
@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # recent 5 transactions for the current user
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()

    income = db.session.query(db.func.sum(Transaction.amount))\
        .filter_by(user_id=current_user.id, trans_type="income").scalar() or 0
    expense = db.session.query(db.func.sum(Transaction.amount))\
        .filter_by(user_id=current_user.id, trans_type="expense").scalar() or 0
    balance = income - expense

    return render_template("dashboard.html",
                           income=income,
                           expense=expense,
                           balance=balance,
                           transactions=transactions)

@main_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "0")
        trans_type = request.form.get("trans_type", "expense")  # default to expense if not provided
        try:
            amount = float(amount_raw)
        except ValueError:
            flash("Invalid amount", "warning")
            return redirect(url_for("main.transactions"))
        new_tx = Transaction(
            user_id=current_user.id,
            description=description,
            amount=amount,
            trans_type=trans_type,
            date=datetime.utcnow().date()
        )
        db.session.add(new_tx)
        db.session.commit()
        flash("Transaction added", "success")
        return redirect(url_for("main.transactions"))

    tx_list = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template("transactions.html", transactions=tx_list)


@main_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():

    # 🔹 ALWAYS calculate current savings first (before POST block)
    income_sum = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, trans_type="income"
    ).scalar() or 0

    expense_sum = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, trans_type="expense"
    ).scalar() or 0

    current_savings = income_sum - expense_sum   

    
    if request.method == "POST":

        trans_type = request.form.get("trans_type", "expense")
        date_str = request.form.get("date")
        description = request.form.get("description", "")
        amount_raw = request.form.get("amount", "0")

        try:
            amount = float(amount_raw)
        except ValueError:
            flash("Invalid amount", "warning")
            return redirect(url_for("main.add_transaction"))

        # Expense validation
        if trans_type == "expense" and amount > current_savings:
            flash(f"Insufficient Balance. Current Saving is ₹{current_savings}", "danger")
            return redirect(url_for("main.add_transaction"))

        # Parse date
        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            date_val = datetime.utcnow().date()

        new_trans = Transaction(
            trans_type=trans_type,
            date=date_val,
            description=description,
            amount=amount,
            user_id=current_user.id
        )
        db.session.add(new_trans)
        db.session.commit()
        flash("Transaction added successfully!", "success")
        return redirect(url_for("main.add_transaction"))

    
    return render_template("add_transaction.html", current_savings=current_savings)


@main_bp.route("/summary")
@login_required
def summary():
    # Total Income & Expense
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, trans_type="income"
    ).scalar() or 0

    total_expense = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=current_user.id, trans_type="expense"
    ).scalar() or 0

    savings = total_income - total_expense

    # Monthly Income / Expense (for Bar Chart)
    monthly_data = db.session.query(
        db.func.strftime("%Y-%m", Transaction.date),
        Transaction.trans_type,
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id
    ).group_by(
        db.func.strftime("%Y-%m", Transaction.date),
        Transaction.trans_type
    ).all()

    # Format monthly results
    monthly_income = {}
    monthly_expense = {}

    for month, ttype, amount in monthly_data:
        if ttype == "income":
            monthly_income[month] = amount
        else:
            monthly_expense[month] = amount

    # Get sorted months
    all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))

    income_list = [monthly_income.get(m, 0) for m in all_months]
    expense_list = [monthly_expense.get(m, 0) for m in all_months]

    # Savings trend (line chart)
    savings_list = [income_list[i] - expense_list[i] for i in range(len(all_months))]

    return render_template(
        "summary.html",
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        months=all_months,
        income_list=income_list,
        expense_list=expense_list,
        savings_list=savings_list
    )

@main_bp.route("/history", methods=["GET", "POST"])
@login_required
def history():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    query = Transaction.query.filter_by(user_id=current_user.id)
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date <= ed)
        except ValueError:
            pass

    transactions = query.order_by(Transaction.date.desc()).all()
    return render_template("history.html", transactions=transactions, start_date=start_date, end_date=end_date)


@main_bp.route("/export_csv")
@login_required
def export_csv():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = Transaction.query.filter_by(user_id=current_user.id)

    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date >= sd)
        except:
            pass

    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Transaction.date <= ed)
        except:
            pass

    transactions = query.order_by(Transaction.date.asc()).all()

    # Prepare CSV response
    from io import StringIO
    import csv
    from flask import make_response

    si = StringIO()
    writer = csv.writer(si)

    # CSV Header
    writer.writerow(["Date", "Type", "Description", "Amount"])

    # Data rows
    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.trans_type,
            t.description,
            t.amount
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
    output.headers["Content-Type"] = "text/csv"
    return output


@main_bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    results = []
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword == "":
            results = []
        else:
            # numeric search tries amount equality
            if keyword.replace(".", "", 1).isdigit():
                try:
                    amt = float(keyword)
                    results = Transaction.query.filter(Transaction.user_id == current_user.id).filter(
                        (Transaction.description.ilike(f"%{keyword}%")) |
                        (Transaction.amount == amt)
                    ).all()
                except ValueError:
                    results = []
            else:
                results = Transaction.query.filter(Transaction.user_id == current_user.id).filter(
                    (Transaction.description.ilike(f"%{keyword}%")) |
                    (db.cast(Transaction.date, db.String).ilike(f"%{keyword}%"))
                ).all()
    return render_template("search.html", results=results)
