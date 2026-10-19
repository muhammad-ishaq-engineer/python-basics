
from flask import Flask, request, redirect, url_for, render_template_string
from db import get_connection
from decimal import Decimal, InvalidOperation
from html import escape
from uuid import uuid4
import re

app = Flask(__name__)
app.secret_key = "change-this-local-secret"

STYLE = """
<style>
:root {
    --navy: #08172e;
    --gold: #d8b15a;
    --page-bg: #f4f6fa;
    --white: #ffffff;
    --text: #19283e;
    --muted: #778399;
    --border: #e3e8f0;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    background: var(--page-bg);
    color: var(--text);
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
}
header {
    background: linear-gradient(120deg, var(--navy), #16385e);
    color: white;
    padding: 27px max(5%, calc((100% - 1150px) / 2));
    border-bottom: 3px solid var(--gold);
}
.brand-row { display: flex; align-items: center; gap: 15px; }
.brand-mark {
    width: 49px; height: 49px; flex-shrink: 0;
    display: grid; place-items: center;
    border: 1px solid var(--gold); border-radius: 13px;
    color: #f3d991; font-size: 23px; font-weight: 800;
}
header h1 { margin: 0; font-size: clamp(22px, 3vw, 30px); }
header p { margin: 4px 0 0; color: #c6d3e5; font-size: 14px; }
nav {
    display: flex; flex-wrap: wrap; gap: 7px;
    padding: 12px max(5%, calc((100% - 1150px) / 2));
    background: white; border-bottom: 1px solid var(--border);
}
nav a {
    padding: 10px 13px; color: #34465f;
    text-decoration: none; font-weight: 650; border-radius: 8px;
}
nav a:hover { background: var(--navy); color: #f3d991; }
main {
    max-width: 1180px; margin: 32px auto;
    padding: 0 22px 35px; min-height: 55vh;
}
main > h2 { margin: 0 0 22px; font-size: 27px; color: var(--navy); }
h2, h3 { color: var(--navy); }
h3 { margin-top: 0; font-size: 19px; }
.card {
    background: white; border: 1px solid var(--border);
    border-radius: 15px; padding: 24px; margin-bottom: 22px;
    box-shadow: 0 7px 24px #10244308;
}
.cards {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 18px; margin-bottom: 24px;
}
.cards .card {
    margin-bottom: 0; padding: 23px;
    border-top: 3px solid var(--gold);
    color: var(--muted); font-weight: 650;
}
.stat { font-size: clamp(29px, 4vw, 36px); color: var(--navy); font-weight: 800; }
input, select {
    display: block; width: 100%; padding: 13px 14px;
    margin: 8px 0 20px; border: 1px solid #d5dce7;
    border-radius: 9px; background: white; color: var(--text);
    font: inherit; outline: none;
}
input:focus, select:focus {
    border-color: var(--gold); box-shadow: 0 0 0 3px #d8b15a30;
}
label { display: block; font-weight: 700; color: #2b3c54; }
button, .button {
    display: inline-block; background: var(--navy); color: #f3d991;
    border: 1px solid var(--gold); border-radius: 9px;
    padding: 12px 19px; cursor: pointer; font: inherit;
    font-weight: 750; text-decoration: none;
}
button:hover, .button:hover { background: #193b63; }
a { color: #805c12; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td {
    padding: 14px 13px; text-align: left;
    border-bottom: 1px solid var(--border); white-space: nowrap;
}
th { background: var(--navy); color: #f3d991; }
tbody tr:nth-child(even) { background: #f8f9fc; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; }
.table-wrap table { min-width: 520px; }
.message {
    padding: 14px 17px; background: #e8f7ef; color: #176640;
    border: 1px solid #c4ead4; border-left: 4px solid #29945e;
    border-radius: 9px; margin-bottom: 20px;
}
.message.error { background: #fff0f0; color: #a62d38; border-color: #f2c9ce; }
.muted { color: var(--muted); }
.phone-row { display: flex; gap: 8px; align-items: center; }
.phone-row input { flex: 1; min-width: 0; margin-bottom: 20px; }
.phone-row button { padding: 10px 13px; margin-bottom: 12px; }
@media (max-width: 650px) {
    header { padding: 22px 18px; }
    nav { padding: 10px 12px; gap: 4px; }
    nav a { padding: 9px 10px; font-size: 13px; }
    main { margin: 22px auto; padding: 0 13px 25px; }
    .card { padding: 18px; }
    .cards { grid-template-columns: 1fr; }
    main > h2 { font-size: 23px; }
}
</style>
"""

NAV = """
<header>
  <div class="brand-row">
    <div class="brand-mark">S</div>
    <div>
      <h1>Shiekh Bank Limited</h1>
      <p>Banking Services &amp; Account Management</p>
    </div>
  </div>
</header>
<nav>
  <a href="/">Dashboard</a>
  <a href="/add-customer">Add Customer</a>
  <a href="/customers">Customers</a>
  <a href="/accounts">Accounts</a>
  <a href="/cash">Cash Services</a>
  <a href="/transactions">Transactions</a>
</nav>
"""

EYE_SCRIPT = """
<script>
function togglePhone(id, button) {
    const field = document.getElementById(id);
    if (!field) return;
    if (field.type === "password") {
        field.type = "text";
        button.textContent = "Hide";
    } else {
        field.type = "password";
        button.textContent = "Show";
    }
}
</script>
"""


def page(title, content, message=None, error=False):
    notice = ""
    if message:
        cls = "message error" if error else "message"
        notice = f'<div class="{cls}">{escape(str(message))}</div>'

    return render_template_string(
        "<!doctype html><html lang='en'><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<meta name='theme-color' content='#08172e'>"
        "<title>{{ title }} - Shiekh Bank Limited</title>"
        + STYLE +
        "</head><body>" + NAV +
        "<main>" + notice + content +
        "</main>" + EYE_SCRIPT + "</body></html>",
        title=title
    )


def make_table(headers, rows, phone_column=None):
    if not rows:
        return "<p class='muted'>No records found.</p>"

    header_html = "".join(
        f"<th>{escape(str(h))}</th>" for h in headers
    )
    body_html = ""

    for row in rows:
        cells = ""
        for index, value in enumerate(row):
            if value is None:
                cell = ""
            elif index == phone_column:
                phone = escape(str(value), quote=True)
                field_id = "phone_" + uuid4().hex
                cell = (
                    f'<div class="phone-row">'
                    f'<input id="{field_id}" type="password" '
                    f'value="{phone}" readonly '
                    f'aria-label="Customer phone number" '
                    f'style="margin:0;min-width:130px;">'
                    f'<button type="button" '
                    f'onclick="togglePhone(\'{field_id}\',this)">Show</button>'
                    f'</div>'
                )
            else:
                cell = escape(str(value))
            cells += f"<td>{cell}</td>"
        body_html += f"<tr>{cells}</tr>"

    return (
        "<div class='table-wrap'><table><thead><tr>"
        + header_html +
        "</tr></thead><tbody>" + body_html +
        "</tbody></table></div>"
    )


ADD_CUSTOMER_FORM = """
<div class="card">
  <h2>Add Customer</h2>
  <form method="post">
    <label>Customer Full Name</label>
    <input name="full_name" maxlength="100" required>

    <label>Phone Number (11 digits)</label>
    <div class="phone-row">
      <input name="phone" type="tel" inputmode="numeric"
             maxlength="11" minlength="11"
             pattern="[0-9]{11}" placeholder="03XXXXXXXXX"
             title="Enter exactly 11 digits"
             autocomplete="tel" required>
    </div>

    <label>City</label>
    <input name="city" maxlength="50" required>

    <label>Account Type</label>
    <select name="account_type" required>
      <option value="Savings">Savings</option>
      <option value="Current">Current</option>
    </select>

    <label>Opening Balance</label>
    <input name="opening_balance" type="number" min="0"
           step="0.01" required>

    <button type="submit">Add Customer</button>
  </form>
</div>
"""

CUSTOMER_SEARCH_FORM = """
<div class="card">
  <h2>Search Customer</h2>
  <form method="get" action="/customers">
    <label>Search By</label>
    <select name="search_by" required>
      <option value="name">Customer Name</option>
      <option value="customer_id">Customer ID</option>
      <option value="account_id">Account ID</option>
    </select>

    <label>Enter Search Value</label>
    <input name="q" type="text" maxlength="100"
           placeholder="Name or ID enter karein" required>

    <button type="submit">Search</button>
    <a class="button" href="/customers">Show All</a>
  </form>
</div>
"""

CASH_FORM = """
<div class="card">
  <h2>Cash Services</h2>
  <p class="muted">Enter the account number and select a service.</p>
  <form method="post">
    <label>Account Number</label>
    <input name="account_id" type="number" min="1"
           placeholder="Enter account number" required>

    <label>Select Service</label>
    <select name="transaction_type" required>
      <option value="Deposit">Deposit Cash - Jama Karwana</option>
      <option value="Withdrawal">Withdraw Cash - Paise Nikalna</option>
    </select>

    <label>Amount</label>
    <input name="amount" type="number" min="0.01"
           step="0.01" placeholder="Enter amount" required>
    <button type="submit">Submit Transaction</button>
  </form>
</div>
"""


@app.route("/")
def dashboard():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM dbo.Customers")
        customers_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dbo.Accounts")
        accounts_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dbo.Transactions")
        transactions_count = cur.fetchone()[0]
        cur.execute("""
            SELECT TOP 10 TransactionID, AccountID, TransactionType,
                   Amount, TransactionDate
            FROM dbo.Transactions
            ORDER BY TransactionDate DESC, TransactionID DESC
        """)
        recent = cur.fetchall()
    finally:
        conn.close()

    content = f"""
    <h2>Dashboard</h2>
    <div class="cards">
      <div class="card">Total Customers
        <div class="stat">{customers_count}</div>
      </div>
      <div class="card">Total Accounts
        <div class="stat">{accounts_count}</div>
      </div>
      <div class="card">Total Transactions
        <div class="stat">{transactions_count}</div>
      </div>
    </div>
    <div class="card">
      <h3>Recent Transactions</h3>
      {make_table(["Transaction ID", "Account Number", "Type",
                   "Amount", "Date"], recent)}
    </div>
    """
    return page("Dashboard", content)


@app.route("/add-customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "GET":
        return page("Add Customer", ADD_CUSTOMER_FORM)

    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    account_type = request.form.get("account_type", "").strip()
    balance_text = request.form.get("opening_balance", "").strip()

    if not all([full_name, phone, city, account_type, balance_text]):
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Please fill in every field.", True)

    if len(full_name) > 100 or len(city) > 50:
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Name or city is too long.", True)

    if not re.fullmatch(r"[0-9]{11}", phone):
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Enter a phone number containing exactly 11 digits.", True)

    if account_type not in ("Savings", "Current"):
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Please select a valid account type.", True)

    try:
        balance = Decimal(balance_text)
        if (not balance.is_finite() or balance < 0
                or balance.as_tuple().exponent < -2
                or balance > Decimal("9999999999.99")):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Enter a valid opening balance with up to 2 decimal places.", True)

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Check duplicate phone number before registration.
        cur.execute("""
            SELECT TOP 1 CustomerID
            FROM dbo.Customers
            WHERE Phone = ?
        """, phone)

        if cur.fetchone():
            return page("Add Customer", ADD_CUSTOMER_FORM,
                        "This phone number is already registered. Enter another number.", True)

        cur.execute("""
            EXEC dbo.usp_RegisterCustomer
                @FullName = ?,
                @Phone = ?,
                @City = ?,
                @AccountType = ?,
                @OpeningBalance = ?
        """, full_name, phone, city, account_type, balance)

        while cur.nextset():
            pass

        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Customer registration failed")
        return page("Add Customer", ADD_CUSTOMER_FORM,
                    "Customer could not be registered. Check the server terminal.", True)
    finally:
        conn.close()

    return redirect(url_for("customers", added="1"))


@app.route("/customers")
def customers():
    search_by = request.args.get("search_by", "name").strip()
    search_value = request.args.get("q", "").strip()

    message = (
        "Customer added successfully."
        if request.args.get("added") == "1" else None
    )

    conn = get_connection()

    try:
        cur = conn.cursor()

        sql = """
            SELECT TOP 100
                c.CustomerID,
                c.FullName,
                c.Phone,
                c.City,
                a.AccountID,
                a.AccountType,
                a.Balance
            FROM dbo.Customers AS c
            LEFT JOIN dbo.Accounts AS a
                ON c.CustomerID = a.CustomerID
        """

        if search_value:
            if search_by == "name":
                sql += " WHERE c.FullName LIKE ?"
                params = ("%" + search_value + "%",)

            elif search_by == "customer_id":
                if not search_value.isdigit() or int(search_value) < 1:
                    return page(
                        "Customers", CUSTOMER_SEARCH_FORM,
                        "Enter a valid Customer ID.", True
                    )

                sql += " WHERE c.CustomerID = ?"
                params = (int(search_value),)

            elif search_by == "account_id":
                if not search_value.isdigit() or int(search_value) < 1:
                    return page(
                        "Customers", CUSTOMER_SEARCH_FORM,
                        "Enter a valid Account ID.", True
                    )

                sql += " WHERE a.AccountID = ?"
                params = (int(search_value),)

            else:
                return page(
                    "Customers", CUSTOMER_SEARCH_FORM,
                    "Please select a valid search option.", True
                )

            sql += " ORDER BY c.CustomerID DESC"
            cur.execute(sql, params)

        else:
            sql += " ORDER BY c.CustomerID DESC"
            cur.execute(sql)

        rows = cur.fetchall()

    finally:
        conn.close()

    content = (
        CUSTOMER_SEARCH_FORM +
        "<div class='card'><h3>Customer Search Results</h3>" +
        make_table(
            [
                "Customer ID",
                "Full Name",
                "Phone",
                "City",
                "Account ID",
                "Account Type",
                "Balance"
            ],
            rows,
            phone_column=2
        ) +
        "</div>"
    )

    return page("Customers", content, message)


@app.route("/accounts")
def accounts():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.AccountID, a.CustomerID, c.FullName,
                   a.AccountType, a.Balance
            FROM dbo.Accounts AS a
            LEFT JOIN dbo.Customers AS c
                ON c.CustomerID = a.CustomerID
            ORDER BY a.AccountID DESC
        """)
        rows = cur.fetchall()
    finally:
        conn.close()

    content = (
        "<div class='card'><h2>Accounts</h2>" +
        make_table(
            ["Account Number", "Customer ID", "Customer Name",
             "Account Type", "Balance"], rows
        ) +
        "</div>"
    )
    return page("Accounts", content)


@app.route("/cash", methods=["GET", "POST"])
def cash_services():
    if request.method == "GET":
        return page("Cash Services", CASH_FORM)

    account_text = request.form.get("account_id", "").strip()
    transaction_type = request.form.get("transaction_type", "").strip()
    amount_text = request.form.get("amount", "").strip()

    if not account_text.isdigit() or int(account_text) < 1:
        return page("Cash Services", CASH_FORM,
                    "Enter a valid account number.", True)

    if transaction_type not in ("Deposit", "Withdrawal"):
        return page("Cash Services", CASH_FORM,
                    "Select a valid service.", True)

    try:
        amount = Decimal(amount_text)
        if (not amount.is_finite() or amount <= 0
                or amount.as_tuple().exponent < -2
                or amount > Decimal("9999999999.99")):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return page("Cash Services", CASH_FORM,
                    "Enter a positive amount with up to 2 decimal places.", True)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT AccountID
            FROM dbo.Accounts
            WHERE AccountID = ?
        """, int(account_text))

        if not cur.fetchone():
            conn.rollback()
            return page("Cash Services", CASH_FORM,
                        "Account number was not found.", True)

        reference = "SBL-" + uuid4().hex[:12].upper()

        cur.execute("""
            INSERT INTO dbo.Transactions
                (AccountID, TransactionType, Amount,
                 TransactionDate, TransferRef)
            VALUES (?, ?, ?, GETDATE(), ?)
        """, int(account_text), transaction_type, amount, reference)

        # Existing SQL Server trigger is expected to update the balance.
        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Cash transaction failed")
        return page(
            "Cash Services", CASH_FORM,
            "Transaction failed. Check the server terminal for the database error.",
            True
        )
    finally:
        conn.close()

    label = (
        "Cash deposited successfully."
        if transaction_type == "Deposit"
        else "Cash withdrawal recorded successfully."
    )

    return page("Cash Services", CASH_FORM,
                f"{label} Reference: {reference}")


@app.route("/funds")
def old_funds_page():
    return redirect(url_for("cash_services"))


@app.route("/transactions")
def transactions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 100 TransactionID, AccountID, TransactionType,
                   Amount, TransactionDate, TransferRef
            FROM dbo.Transactions
            ORDER BY TransactionDate DESC, TransactionID DESC
        """)
        rows = cur.fetchall()
    finally:
        conn.close()

    content = (
        "<div class='card'><h2>Transactions</h2>" +
        make_table(
            ["Transaction ID", "Account Number", "Type",
             "Amount", "Date", "Reference"], rows
        ) +
        "</div>"
    )
    return page("Transactions", content)


if __name__ == "__main__":
    app.run(debug=False)
