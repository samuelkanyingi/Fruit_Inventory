from flask import Flask, jsonify,  render_template, request, redirect, flash, url_for, make_response
from io import BytesIO
import openpyxl
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import json
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'samuelkanyingi2016'
app.config['MAIL_PASSWORD'] = 'samuel2016'
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:root@localhost/mydatabase'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

LOW_INVENTORY_THRESHOLD = 10

class Fruit(db.Model):
    __tablename__ = 'fruit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    quantity = db.Column(db.Integer)

class Userz(db.Model):
    __tablename__ = 'userz'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50))
    details = db.Column(db.String(255))
'''
with app.app_context():
        db.create_all()

with app.app_context():
    db.create_all()

    new_fruit = Fruit(name='mangoes', quantity=1)
    db.session.add(new_fruit)
    db.session.commit()
'''
def reset_ids():
    # Fetch all fruits from the database
    fruits = Fruit.query.all()

    # Reset the IDs sequentially
    for i, fruit in enumerate(fruits, start=1):
        fruit.id = i

    # Commit the changes
    db.session.commit()
@app.route('/get_fruit')
def get_data():
    fruits = Fruit.query.all()
    #data = [{'name': fruit.name, 'quantity': fruit.quantity} for fruit in fruits]
    names=[fruit.name for fruit in fruits]
    quantities=[fruit.quantity for fruit in fruits]
    data={'names': names, 'quantities': quantities}
    #data = [{'name': fruit.name, 'quantity': fruit.quantity} for fruit in fruits]
    reset_ids()
    return render_template('chart.html', data=data)

@app.route('/delete_fruit/<int:fruit_id>', methods=['POST', 'GET'])
def delete_fruit(fruit_id):
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        db.session.delete(fruit)
        db.session.commit()
        #return jsonify({'message': 'User deleted successfully'})
      #  flash('Delete successful', 'success')
        reset_ids()
        return redirect('/table')
        flash('Delete successful', 'success')
    else:
        return jsonify({'message': 'User not found'})

@app.route('/update_user/<int:user_id>/<string:name>/<int:age>', methods=['POST'])
def update_user(user_id, name, age):
    user = User.query.get(user_id)
    if user:
        user.name = request.form.get('name', user.name)
        user.age = request.form.get('age', user.age)
        db.session.commit()
        reset_ids()
        return jsonify({'message': 'User updated successfully'})
    else:
        return jsonify({'message': 'User not found'})

@app.route('/update_fruit/<int:fruit_id>', methods=['GET','POST'])
def update_fruit(fruit_id):
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        fruit.name = request.form.get('name', fruit.name)
        fruit.quantity = request.form.get('quantity', fruit.quantity)
        db.session.commit()
        reset_ids()
        return redirect('/table')
        #return jsonify({'message': 'User updated successfully'})
    else:
        return jsonify({'message': 'User not found'})

LOW_INVENTORY_THRESHOLD = 10
@app.route('/add_fruit', methods=['POST'])
def add_fruit():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    
    existing_fruit = Fruit.query.filter_by(name=name).first()
    if existing_fruit:
        flash('Error: Fruit with this name already exists!', 'error')
        return redirect('/table')
    new_fruit = Fruit(name=name, quantity=quantity)
    db.session.add(new_fruit)
    db.session.commit()
    reset_ids()
    
    log_entry = AuditLog(user='example_user', action='Added', details=f'Added {quantity} {name}(s)')
    db.session.add(log_entry)
    db.session.commit()
    if quantity <= LOW_INVENTORY_THRESHOLD:
        flash(f'The quantity of {name} is too low. Please restock.', 'error')

    return redirect('/table')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table.html', methods=['POST'])
def action():
    fname = request.form['fname']  # Get the submitted fruit name
    lname = request.form['lname']  # Get the submitted fruit quantity
    return render_template('action.html', fname=fname, lname=lname)

@app.route('/table')
def table():
    fruits = Fruit.query.all()
    LOW_INVENTORY_THRESHOLD = 4
    return render_template('table.html',fruits=fruits, LOW_INVENTORY_THRESHOLD=LOW_INVENTORY_THRESHOLD)
@app.route('/chart')
def indexm():
    return render_template('chart.html')

@app.route('/edit_fruit/<int:fruit_id>', methods=['GET'])
def edit_fruit_form(fruit_id):
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        return render_template('edit_form.html', fruit=fruit)
    else:
        # Handle the case where the fruit is not found
        return "Fruit not found", 404
@app.route('/edit_form')
def edit_form():
    return render_template('edit_form.html')


@app.route('/signme', methods=['POST', 'GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signup',methods=['POST'])
def signup():
    username= request.form['username']
    email= request.form['email']
    password = request.form['password']

    if Userz.query.filter_by(username=username).first() or  Userz.query.filter_by(email=email).first():
        return "username or email already exist"

    db.create_all()
    new_user = Userz(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return "signup successful"
@app.route('/login', methods=['POST', 'GET'])
def login_form():
    return render_template('login.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    
    email = request.form.get('email')
    password = request.form.get('password')
    if Userz.query.filter_by(email=email).first() and  Userz.query.filter_by(password=password).first():
        #return jsonify({"message": "success"})
        return render_template('table.html')
    else:
        flash("Invalid login details")
        return redirect(url_for('login_form'))
        #return jsonify({"message": "invalid login"})
'''
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'login successful'}), 200
   ''' 
@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/forgot-password', methods=['POST'])
def send_password_reset_email():
    email = request.form.get('email')
    # Check if email exists in the user database
    user = Userz.query.filter_by(email=email).first()
    if user:
        token = 'abc123'
        print(f"Password reset token for {email}: {token}")
        #return "Password reset email sent!{email}: {token}"

        return render_template('reset_password.html', token=token)
    else:
        flash('Email address not found!', 'danger')
        #return "Email address not found!"
        return render_template('forgot_password.html')
        #return redirect(url_for('/forgot-password'))
@app.route('/reset-password', methods=['GET'])
def reset_password(token):
        return render_template('reset_password2.html')

@app.route('/reset-password/<token>', methods=['POST'])
def update_password(token):
    # Check if the token is valid (mocked here with a simple string comparison)
        email = request.form.get('email')
        new_password = request.form.get('password')
        user = Userz.query.filter_by(email=email).first()
        if user:
        # Update the password for the user
            user.password = new_password
            db.session.commit()
            #print(f"New password for user: {new_password}")
            #return "Password updated successfully!"
            flash("Password updated successfully!", "success")
            return redirect(url_for('login_form'))
        else:
            return "Invalid token! sammy"
LOW_INVENTORY_THRESHOLD = 4
@app.route('/search', methods=['POST'])
def search():
    # Retrieve the search query from the form submission
    LOW_INVENTORY_THRESHOLD = 4
    search_query = request.form['query']

    # Query the database to find items that match the search query
    matching_items = Fruit.query.filter(Fruit.name.ilike(f'%{search_query}%')).all()

    # Render the template with the matching items
    return render_template('table.html', fruits=matching_items, LOW_INVENTORY_THRESHOLD = LOW_INVENTORY_THRESHOLD )


@app.route('/export', methods=['GET', 'POST'])
def export_excel():
    # Fetch all fruit data from the database
    fruit_data = Fruit.query.all()

    # Create a new Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Name", "Quantity"])

    # Add fruit data to the Excel sheet
    for fruit in fruit_data:
        ws.append([fruit.id, fruit.name, fruit.quantity])

    # Save Excel workbook to BytesIO buffer
    excel_data = BytesIO()
    wb.save(excel_data)
    excel_data.seek(0)

    # Create response with Excel data
    response = make_response(excel_data.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=fruit_inventory.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response

@app.route('/audit_logs')
def audit_logs():
    logs = AuditLog.query.all()
    return render_template('audit.html', logs=logs)

@app.route('/landing')
def land():
    return render_template('landing.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
