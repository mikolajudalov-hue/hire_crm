import os
import json
from urllib.parse import urlencode
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, NewsArticle, Course
from datetime import datetime

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
app.secret_key = "supersecret1234567890"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwr_-DVY8tHVrZ0NwVKEAxk1a1Nj0KBrD-LrCeQHvKTY7RETCxvaJaixZM4kmeSYJhh/exec"

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

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pesel = request.form.get("pesel", "").strip()
        if not pesel:
            flash("Введите PESEL", "error")
            return render_template("login.html")
        if pesel == "97021115999":
            session["pesel"] = pesel
            session["name"] = "Admin"
            return redirect(url_for("news"))
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

@app.context_processor
def inject_globals():
    return {
        "earned": session.get("earned", 0),
        "name": session.get("name", ""),
        "pesel": session.get("pesel", "")
    }

@app.route("/news")
def news():
    if "pesel" not in session:
        return redirect(url_for("login"))
    news_list = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    return render_template("news.html", news_list=news_list)

@app.route("/news/add", methods=["GET", "POST"])
def add_news():
    if "pesel" not in session or session["pesel"] != "97021115999":
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title")
        short_description = request.form.get("short_description")
        full_description = request.form.get("full_description")
        if not title or not short_description or not full_description:
            flash("Все поля должны быть заполнены", "error")
            return render_template("add_news.html")
        new_article = NewsArticle(title=title, short_description=short_description, full_description=full_description)
        db.session.add(new_article)
        db.session.commit()
        flash("Новость успешно добавлена", "success")
        return redirect(url_for("news"))
    return render_template("add_news.html")

@app.route("/news/<int:article_id>")
def view_news(article_id):
    if "pesel" not in session:
        return redirect(url_for("login"))
    article = NewsArticle.query.get_or_404(article_id)
    return render_template("view_news.html", article=article)

@app.route("/news/edit/<int:article_id>", methods=["GET", "POST"])
def edit_news(article_id):
    if "pesel" not in session or session["pesel"] != "97021115999":
        return redirect(url_for("login"))
    article = NewsArticle.query.get_or_404(article_id)
    if request.method == "POST":
        article.title = request.form.get("title")
        article.short_description = request.form.get("short_description")
        article.full_description = request.form.get("full_description")
        db.session.commit()
        flash("Новость успешно обновлена", "success")
        return redirect(url_for("view_news", article_id=article.id))
    return render_template("edit_news.html", article=article)

@app.route("/news/delete/<int:article_id>", methods=["POST"])
def delete_news(article_id):
    if "pesel" not in session or session["pesel"] != "97021115999":
        return redirect(url_for("login"))
    article = NewsArticle.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash("Новость успешно удалена", "success")
    return redirect(url_for("news"))

@app.route("/driver-panel")
def driver_panel():
    if "pesel" not in session:
        return redirect(url_for("login"))
    pesel = session["pesel"]
    active_course = Course.query.filter_by(pesel=pesel, end_time=None).first()
    completed_courses = Course.query.filter(Course.pesel == pesel, Course.end_time != None).order_by(Course.start_time.desc()).all()
    return render_template("driver_panel.html", active_course=active_course, completed_courses=completed_courses, now=datetime.now())

@app.route("/course/start", methods=["POST"])
def start_course():
    if "pesel" not in session:
        return redirect(url_for("login"))
    pesel = session["pesel"]
    active_course = Course.query.filter_by(pesel=pesel, end_time=None).first()
    if active_course:
        flash("У вас уже есть активный курс. Завершите его перед началом нового.", "error")
        return redirect(url_for("driver_panel"))
    new_course = Course(pesel=pesel, start_time=datetime.now())
    db.session.add(new_course)
    db.session.commit()
    flash("Курс начат", "success")
    return redirect(url_for("driver_panel"))

@app.route("/course/end/<int:course_id>", methods=["POST"])
def end_course(course_id):
    if "pesel" not in session:
        return redirect(url_for("login"))
    course = Course.query.get_or_404(course_id)
    if course.pesel != session["pesel"]:
        flash("Вы не можете завершить чужой курс", "error")
        return redirect(url_for("driver_panel"))
    comment = request.form.get("comment", "")
    course.end_time = datetime.now()
    course.comment = comment
    db.session.commit()
    flash("Курс завершен", "success")
    return redirect(url_for("driver_panel"))

@app.route("/admin/courses")
def admin_courses():
    if "pesel" not in session or session["pesel"] != "97021115999":
        return redirect(url_for("login"))
    filter_pesel = request.args.get("filter_pesel", "")
    if filter_pesel:
        courses = Course.query.filter_by(pesel=filter_pesel).order_by(Course.start_time.desc()).all()
    else:
        courses = Course.query.order_by(Course.start_time.desc()).all()
    unique_pesels = db.session.query(Course.pesel).distinct().all()
    return render_template("admin_courses.html", courses=courses, unique_pesels=unique_pesels, filter_pesel=filter_pesel)

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

if __name__ == "__main__":
    app.run(debug=True)
