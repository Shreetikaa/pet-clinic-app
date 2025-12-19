from flask import Flask, render_template, request, redirect, session, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Appointment
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

# SECURITY
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # If not logged in, always send back to the landing (login) page
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login():
    """This is now your landing page."""
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.username
            session["role"] = user.role
            return redirect(url_for('dashboard'))
        return "<h2>Invalid credentials</h2><a href='/'>Try again</a>"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if User.query.filter_by(username=username).first():
            return "<h2>Username exists!</h2><a href='/register'>Try again</a>"
        user = User(username=username, password=generate_password_hash(request.form["password"]), role=request.form["role"])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

#DASHBOARDS 
@app.route("/dashboard")
@login_required
def dashboard():
    if session["role"] == "owner":
        all_appts = Appointment.query.filter_by(owner=session["user"]).all()
        total_visits = len([a for a in all_appts if a.status == 'Approved'])
        num_appointments = len([a for a in all_appts if a.status == 'Pending'])
        return render_template("owner_dashboard.html", appointments=all_appts, total_visits=total_visits, num_appointments=num_appointments)
    
    appts = Appointment.query.all()
    return render_template("vet_dashboard.html", appointments=appts)

# THE UPDATE ROUTE 
@app.route("/update/<int:appt_id>/<string:status>")
@login_required
def update_status(appt_id, status):
    if session["role"] != "vet":
        abort(403)
    
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = status
    db.session.commit()
    return redirect(url_for('dashboard'))

# BOOKING ROUTES
@app.route("/request", methods=["GET", "POST"])
@login_required
def request_appointment():
    if request.method == "POST":
        appt = Appointment(pet_name=request.form["pet_name"], owner=session["user"], date=request.form["date"], reason=request.form["reason"], appt_type="General", status="Pending")
        db.session.add(appt)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template("request_appointment.html")

@app.route("/book-vaccination", methods=["GET", "POST"])
@login_required
def book_vaccination():
    if request.method == "POST":
        appt = Appointment(pet_name=request.form["pet_name"], owner=session["user"], date=request.form["date"], reason=f"Vaccine: {request.form['vax_type']}", appt_type="Vaccination", status="Pending")
        db.session.add(appt)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template("book_vaccination.html")

@app.route("/calendar")
@login_required
def calendar():
    appts = Appointment.query.all() if session["role"] == "vet" else Appointment.query.filter_by(owner=session["user"]).all()
    return render_template("calendar.html", appointments=appts)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)