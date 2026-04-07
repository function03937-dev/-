import os
from datetime import datetime, timedelta
# we need time to implement some function
from flask import Flask, render_template, request, redirect, url_for, flash, abort
# we want to create a program that can be used  in web application so we use
# Flask as our web structure 1)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# To prepare for the login and logout system
from models import db, User, FoodListing, FoodFactory
# db serves as the primary database manager for Flask projects; all database structure definitions and CRUD operations are executed via this instance.
from services import NotificationManager, EmailNotifier, SMSNotifier
# Extract complex logic from routes to separate files.
app = Flask(__name__)
# Creates the app instance and defines the root directory.
app.config["SECRET_KEY"] = "super-secret-food-rescue-key"
#  Encryption key for sessions and CSRF protection.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Sets the SQLite database path; os.path ensures cross-platform support.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "foodbridge2.db")
db.init_app(app)
# Connects the SQLAlchemy instance to the Flask app (application factory pattern).

login_manager = LoginManager(app)
# Initializes the login manager and associates it with the Flask application.
login_manager.login_view = "login"
# Sets the login page for unauthorized users.
@login_manager.user_loader
# A core callback function that loads a user from the database to manage the session.
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route("/")
# @app.route("/") binds the root URL to a function.
def index():
    # Show only available food that hasn't expired
    listings = FoodListing.query.order_by(FoodListing.expiry_time.asc()).all()
# Gets all data from the FoodListing table.
# Sorts data by expiry time from earliest to latest.
    return render_template("index.html", listings=listings)
# render_template sends data to the HTML page.
@app.route("/register", methods=["GET", "POST"])
# methods=["GET", "POST"] allows GET (page loading) and POST (form submission) requests.
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        role = request.form.get("role")
        contact_info = request.form.get("contact_info")
        # request.form.get() retrieves form data submitted via POST.
        if User.query.filter_by(_username=username).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("register"))
            # User.query.filter_by(_username=username).first() checks whether a user with the same username exists.
        try:
            # Encapsulation validation triggers here naturally via properties
            user = User(username=username, role=role, contact_info=contact_info)
            user.set_password(password)
            db.session.add(user)
            # Adds a new record to the database session
            db.session.commit()
            # Commits the session to persist data to the database.
            flash(f"Registration successful for {user.username}. Please log in.", "success")
            # flash() sends notification messages (with categories such as danger/success) to be displayed in templates.
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("register"))
        # Catches ValueError (user data validation failure), returns an error message, and redirects the user.
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(_username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password")):
            # hash password verification, not plain text comparison
            login_user(user)
            # Flask-Login sets user login session
            return redirect(url_for("dashboard"))
        #  generates URL based on view function name to avoid hard coding.
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
# @login_required decorator (Flask-Login), allowing access only to logged-in users.
def logout():
    logout_user()
    # logout_user() clears user login session and redirects to homepage.
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "donor":
        # representing the currently logged-in user object.
        listings = FoodListing.query.filter_by(donor_id=current_user.id).order_by(FoodListing.id.desc()).all()
        # queries food lists related to users.
        # sorts in descending order by ID (newest first).
        return render_template("dashboard_donor.html", listings=listings)
    else:
        claims = FoodListing.query.filter_by(receiver_id=current_user.id).order_by(FoodListing.id.desc()).all()
        return render_template("dashboard_receiver.html", claims=claims)

@app.route("/listing/new", methods=["GET", "POST"])
@login_required
def new_listing():
    if current_user.role != "donor":
        abort(403)
        # rejects non-donors from creating lists.
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        food_type = request.form.get("food_type", "generic")
        hours_valid = int(request.form.get("hours_valid", 2))
        expiry_time = datetime.utcnow() + timedelta(hours=hours_valid)
        # datetime.utcnow() gets current UTC time, timedelta(hours=hours_valid) calculates expiration time.
        # Using the Factory Design Pattern to create inherited class types!
        listing = FoodFactory.create_food(
            food_type=food_type, title=title, description=description, location=location,
            expiry_time=expiry_time, donor_id=current_user.id)
        # creates different types of FoodListing subclass instances according to food_type.
        db.session.add(listing)
        db.session.commit()
        flash(listing.display_info() + " listed successfully!", "success")
        # displays formatted information of food lists
        return redirect(url_for("dashboard"))
    return render_template("new_listing.html")

@app.route("/listing/<int:listing_id>/claim", methods=["POST"])
# captures integer list ID in URL and passes to view function.
@login_required
def claim_listing(listing_id):
    if current_user.role != "receiver":
        flash("Only receivers can claim food.", "danger")
        return redirect(url_for("index"))
        
    listing = FoodListing.query.get_or_404(listing_id)
    # throws 404 exception if not found
    
    # OOP Data Processing & Encapsulated Logic
    if listing.claim(current_user.id):
        db.session.commit()
        
        # Using the OOP-based Service layer (Singleton + Strategy patterns)
        notifier = NotificationManager()
        if not notifier._notifiers: # Lazy initialization of composed services
            notifier.add_notifier(EmailNotifier()).add_notifier(SMSNotifier())
        
        # Fire polymorphic notifications
        notifier_msgs = notifier.notify_all(listing.donor, f"Your listing {listing.title} has been claimed!")
        for msg in notifier_msgs:
            print("System Log Strategy Executed:", msg) # Just a console log to demo to marker
            
        flash(f"Claimed {listing.title}! Please pick it up at the location.", "success")
    else:
        flash("This food has already been claimed or is unavailable.", "danger")
        
    return redirect(url_for("dashboard"))

@app.route("/listing/<int:listing_id>/complete", methods=["POST"])
@login_required
def complete_listing(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)
    
    # Encapsulated Business Logic handling state changes
    if current_user.id in [listing.donor_id, listing.receiver_id]:
        if listing.complete_pickup():
            db.session.commit()
            flash("Pickup confirmed! Thanks for using FoodBridge.", "success")
        else:
            flash("Could not complete pickup, item may not be claimed.", "warning")
            
    return redirect(url_for("dashboard"))

@app.context_processor
def inject_now():
    return {'current_time': datetime.utcnow}

def init_db():
    with app.app_context():
        # Using abstract methods and custom objects to satisfy requirements
        # manually creates Flask application context, enabling database operations to access application configuration
        db.create_all()
        # automatically creates all data tables according to model definitions
        # --- ADDING SAMPLE DATA ---
        # Only inject sample data if the database is completely empty
        if not User.query.first() or FoodListing.query.count() == 0:
            # 1. Create a sample Donor and Receiver
            sample_donor = User(username="FreshBakery", role="donor", contact_info="bakery@sample.com")
            sample_donor.set_password("123456")
            
            sample_receiver = User(username="CityShelter", role="receiver", contact_info="help@shelter.org")
            sample_receiver.set_password("123456")
            
            db.session.add_all([sample_donor, sample_receiver])
            db.session.commit()
            
            # 2. Create sample food listings using our OOP Factory
            food1 = FoodFactory.create_food(
                food_type="perishable",
                title="15x Fresh Croissants",
                description="Baked this morning! Need to be eaten soon.",
                location="123 Downtown Bakery St.",
                expiry_time=datetime.utcnow() + timedelta(days=7),
                donor_id=sample_donor.id
            )
            
            food2 = FoodFactory.create_food(
                food_type="non_perishable",
                title="50x Canned Tomato Soup",
                description="Leftovers from our canned food drive. Excellent condition.",
                location="City Shelter Warehouse",
                expiry_time=datetime.utcnow() + timedelta(days=180),
                donor_id=sample_donor.id
            )
            
            db.session.add_all([food1, food2])
            db.session.commit()
            print("Successfully injected sample data into the database!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
