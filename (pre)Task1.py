from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foodbridge.db"
db = SQLAlchemy(app)

# DATABASE MODELS

class User(db.Model):
    """
    Function 2: Collecting Company Information
    Stores details for food donors (companies) or receivers.
    """
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20)) # 'donor' (company) or 'receiver'
    
    # Company Specific Details
    company_name = db.Column(db.String(100), nullable=True)
    manager_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(200))

class FoodListing(db.Model):
    """
    Function 1, 3, & 4: Food Information, Categorization, and Tracking
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Function 3: Categorizing by expiration date and dietary properties
    expiry_date = db.Column(db.DateTime, nullable=False)
    dietary_properties = db.Column(db.String(100)) # e.g., "Vegetarian, Halal"
    
    # Function 4: Tracking pickup status
    status = db.Column(db.String(20), default="Available") # 'Available', 'Claimed', 'Picked Up'
    
    # Relationships
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# CORE ROUTES 

#Function 1: Listing the food information (Receiving and Distributing) ---
# Function 3: Categorizing based on expiry and dietary ---
@app.route("/")
def view_food_listings():
    # Aim: 
    # 1. Fetch all food listings where status == "Available"
    # 2. Filter or sort them by 'expiry_date'
    # 3. Filter by 'dietary_properties' category if user requested
    # 4. Render HTML page passing the listings
    pass

@app.route("/listing/add", methods=["POST"])
def add_listing():
    # Aim:
    # 1. Take food details from the donor form (title, expiry_date, dietary_properties)
    # 2. Save new FoodListing to the database
    # 3. Redirect back to donor dashboard
    pass

# Function 2: Collecting company info 
@app.route("/register_company", methods=["POST"])
def register_company():
    # Aim:
    # 1. Get company name, manager name, phone number from form
    # 2. Create new User with role="donor"
    # 3. Save to database
    pass

# Function 4: Tracking food pickup status 
@app.route("/listing/<int:listing_id>/claim", methods=["POST"])
def claim_food(listing_id):
    # Aim: Receiver claims food. Change status -> 'Claimed'
    pass

@app.route("/listing/<int:listing_id>/pickup", methods=["POST"])
def complete_pickup(listing_id):
    # Aim: Pickup is completed. Change status -> 'Picked Up'
    pass

@app.route("/dashboard")
def dashboard():
    # Aim: 
    # Display lists tracking all food items categorised by their status 
    # ("Available", "Claimed", "Picked Up") for both donors and receivers.
    pass

if __name__ == "__main__":
    app.run(debug=True)