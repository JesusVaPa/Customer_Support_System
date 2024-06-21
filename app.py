import sys
import os

# Add the 'controller' directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Controllers'))

from flask import Flask, render_template, render_template, request, redirect, jsonify, url_for


#Auth lib
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


#Objects
from Database import db
from User import Users
from Admin import Admins
from Ticket import Tickets
from Category import Categories
import FAQ
import Authentication as Auth

# Create Flask app instance
app = Flask(__name__)
app.secret_key = '##Secret##' #for flash

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\vapaj\\Documents\\Customer_Support_System\\Database\\database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# The SQLAlchemy object
db.init_app(app)


# Initialize Flask-Login
user_login_manager = LoginManager(app)
admin_login_manager = LoginManager(app)

# Set custom login views
user_login_manager.login_view = 'login'
admin_login_manager.login_view = 'loginAdmin'

####### Aadmin Auth ######
@admin_login_manager.user_loader
def load_admin(admin_id):
    admin = Admins.query.get(int(admin_id))
    if admin:
        return Auth.Admin(id=admin.id, username=admin.username, email=admin.email, password=admin.password)
    return None

@app.route('/register-admin', methods=['GET', 'POST'])
def registerAdmin():
    form = Auth.RegistrationForm()
    if form.validate_on_submit():
        Auth.Admin.register(form)
        return redirect(url_for('loginAdmin')) 
    else:
        return render_template('Auth/admin/register.html', form=form)

@app.route('/login-admin', methods=['GET', 'POST'])
def loginAdmin():
    form = Auth.LoginForm()
    if form.validate_on_submit():
        Auth.Admin.login(form)
        return redirect(url_for('HomeAdmin'))
    else:
        return render_template('Auth/admin/login.html', form=form)
    

@app.route('/home-admin')
@login_required
def HomeAdmin():
    if current_user.is_authenticated:
        return render_template('Auth/admin/home.html')
    else:
        return render_template('Auth/admin/login.html')

@app.route('/logout-admin')
@login_required
def logoutAdmin():
    Auth.Admin.logout()
    return redirect(url_for('loginAdmin'))

####### User Auth ######
@user_login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    if user:
        return Auth.User(id=user.id, username=user.username, email=user.email, password=user.password)
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Auth.RegistrationForm()
    if form.validate_on_submit():
        Auth.User.register(form)
        return redirect(url_for('login')) 
    else:
        return render_template('Auth/user/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Auth.LoginForm()
    if form.validate_on_submit():
        Auth.User.login(form)
        return redirect(url_for('home'))
    else:
        return render_template('Auth/user/login.html', form=form)
    
@app.route('/logout')
@login_required
def logout():
    Auth.User.logout()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        return render_template('Auth/user/home.html')
    else:
        return render_template('Auth/user/login.html')

# Recent tickets Route
@app.route('/ticketShow')
@login_required
def ticketShow():
    data_ticket = Tickets.read()
    return render_template('tickets/index.html', data=data_ticket)


# New ticket Page Route
@app.route('/sendTicket')
@login_required
def sendTicket():
    category = Categories.read()
    return render_template('tickets/create.html', category = category)


# Write ticket to database
@app.route('/submitTickets', methods=['POST'])
@login_required
def submit_ticket():
    if request.method == 'POST':
        form_data = Tickets.read_form()
        Tickets.create(form_data)
        return redirect('/sendTicket')

# FAQ Route
@app.route('/faq')
def faq():
    data_faq  = faq_coll.find({})
    return render_template('faq/FAQ.html', data = data_faq)

# show ticket Page Route
@app.route('/faq_create')
def faq_create():
    category = faq_cat_coll.find({})
    return render_template('faq/create.html', category = category)


# Write faq to database
@app.route('/submitFAQ', methods=['POST'])
def submitFAQ():
    if request.method == 'POST':
        # Get FAQ data
        get_faq_data = FAQ.FAQ()
        # Save to DB
        get_faq_data.save_to_db(faq_coll)
        return redirect('/faq')


# Index Page
@app.route('/')
def index():
    return render_template('index.html')
    
    
####### End Routes #######


# Run the Flask application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
