import os
import json
from urllib.parse import urlencode
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
app.secret_key = os.getenv("FLASK_SECRET", "supersecret1234567890")

GAS_WEBAPP_URL = os.getenv(
    "GAS_WEBAPP_URL",
    "https://script.google.com/macros/s/AKfycbwr_-DVY8tHVrZ0NwVKEAxk1a1Nj0KBrD-LrCeQHvKTY7RETCxvaJaixZM4kmeSYJhh/exec"
).strip()

def gas_call(params):
    try:
        url = f"{GAS_WEBAPP_URL}?{urlencode(params)}"
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        try:
            return r.json()
        except json.JSONDecodeError:
            print("RAW GAS RESPONSE:", r.text)
            return {"ok": False, "error": "Invalid JSON from GAS"}
    except Exception as e:
        print(f"GAS error: {e}")
        return {"ok": False, "error": str(e)}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pesel = request.form.get("pesel", "").strip()
        if not pesel:
            flash("Введите PESEL", "error")
            return render_template("login.html")
        res = gas_call({"mode": "auth", "pesel": pesel})
        if not res.get("ok"):
            flash(res.get("error", "Неверный PESEL"), "error")
            return render_template("login.html")
        session["pesel"] = pesel
        session["name"] = res.get("name", "Сотрудник")
        session["earned"] = res.get("earned", "0")
        session["months"] = res.get("months", [])
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "pesel" not in session:
        return redirect(url_for("login"))
    months = session.get("months", [])
    return render_template(
        "dashboard.html",
        name=session.get("name"),
        pesel=session.get("pesel"),
        months=sorted(months, reverse=True)
    )

@app.route("/view")
def view():
    if "pesel" not in session:
        return redirect(url_for("login"))
    month = request.args.get("month")
    view_type = request.args.get("type", "hours")
    months = session.get("months", [])
    if not month and months:
        month = sorted(months, reverse=True)[0]
    res = gas_call({"mode": view_type, "pesel": session["pesel"], "month": month})
    if not res.get("ok"):
        flash(res.get("error", "Ошибка загрузки"), "error")
        return redirect(url_for("dashboard"))
    if view_type == "hours":
        return render_template(
            "hours.html",
            name=session["name"],
            month=month,
            columns=res.get("columns", []),
            values=res.get("values", []),
            total=res.get("total")
        )
    return render_template(
        "salary.html",
        name=session["name"],
        month=month,
        columns=res.get("columns", []),
        row=res.get("row", []),
        note=res.get("note")
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
