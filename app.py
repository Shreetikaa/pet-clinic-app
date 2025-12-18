from flask import Flask, render_template, request, redirect, session, abort, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from reportlab.pdfgen import canvas
import smtplib, io
from email.mime.text import MIMEText

from config import Config
from models import db, User, Appointment, Vaccination

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

#  ROLE DECORATOR 
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if "role" not in session or session["role"] != role:
                abort(403)
            return fn(*args, **kwargs)
        return decorated
    return wrapper

# EMAIL FUNCTION 
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = app.config["MAIL_USERNAME"]
    msg["To"] = app.config["MAIL_USERNAME"]

    with smtplib.SMTP_SSL(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        server.send_message(msg)

#AUTH 
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.username
            session["role"] = user.role
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role=request.form["role"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# DASHBOARD 
@app.route("/dashboard")
def dashboard():
    if session["role"] == "owner":
        appts = Appointment.query.filter_by(owner=session["user"]).all()
        return render_template("owner_dashboard.html", appointments=appts)
    else:
        appts = Appointment.query.all()
        return render_template("vet_dashboard.html", appointments=appts)

#  OWNER ROUTES
@app.route("/request", methods=["GET", "POST"])
@role_required("owner")
def request_appointment():
    if request.method == "POST":
        appt = Appointment(
            pet_name=request.form["pet"],
            owner=session["user"],
            date=request.form["date"],
            reason=request.form["reason"]
        )
        db.session.add(appt)
        db.session.commit()

        send_email(
            "New Appointment Request",
            f"New appointment request for {appt.pet_name} on {appt.date}"
        )

        return redirect("/dashboard")
    return render_template("request_appointment.html")

# VET ROUTES 
@app.route("/update/<int:id>/<status>")
@role_required("vet")
def update_status(id, status):
    appt = Appointment.query.get_or_404(id)
    appt.status = status
    db.session.commit()

    send_email(
        "Appointment Status Updated",
        f"Appointment for {appt.pet_name} is {status}"
    )

    return redirect("/dashboard")

@app.route("/vaccination", methods=["GET", "POST"])
@role_required("vet")
def vaccination():
    if request.method == "POST":
        vac = Vaccination(
            pet_name=request.form["pet"],
            vaccine=request.form["vaccine"],
            given_date=request.form["given"],
            next_due=request.form["due"]
        )
        db.session.add(vac)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("vaccination.html")

# PDF REPORT 
@app.route("/report/<pet>")
@role_required("vet")
def report(pet):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(50, 800, f"Health Report: {pet}")

    y = 760
    for r in Vaccination.query.filter_by(pet_name=pet).all():
        pdf.drawString(50, y, f"{r.vaccine}: {r.given_date} → {r.next_due}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="health_report.pdf")

#  EXTRA 
@app.route("/calendar")
def calendar():
    return render_template("calendar.html", appointments=Appointment.query.all())

@app.route("/analytics")
@role_required("vet")
def analytics():
    return render_template(
        "analytics.html",
        pending=Appointment.query.filter_by(status="Pending").count(),
        approved=Appointment.query.filter_by(status="Approved").count(),
        rejected=Appointment.query.filter_by(status="Rejected").count()
    )

#ERROR
@app.errorhandler(403)
def forbidden(e):
    return "<h2>403 Access Denied</h2>", 403

if __name__ == "__main__":
    app.run(debug=True)