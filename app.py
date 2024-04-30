from flask import Flask, jsonify,  render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:root@localhost/mydatabase'

db = SQLAlchemy(app)

class Fruit(db.Model):
    __tablename__ = 'fruit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
'''
with app.app_context():
    db.create_all()

    new_fruit = Fruit(name='mangoes', quantity=1)
    db.session.add(new_fruit)
    db.session.commit()
'''
@app.route('/get_fruit')
def get_data():
    fruits = Fruit.query.all()
    #data = [{'name': fruit.name, 'quantity': fruit.quantity} for fruit in fruits]
    names=[fruit.name for fruit in fruits]
    quantities=[fruit.quantity for fruit in fruits]
    data={'names': names, 'quantities': quantities}
    #data = [{'name': fruit.name, 'quantity': fruit.quantity} for fruit in fruits]
    return render_template('chart.html', data=data)

@app.route('/delete_fruit/<int:fruit_id>', methods=['POST', 'GET'])
def delete_fruit(fruit_id):
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        db.session.delete(fruit)
        db.session.commit()
        #return jsonify({'message': 'User deleted successfully'})
      #  flash('Delete successful', 'success')
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
        return redirect('/table')
        #return jsonify({'message': 'User updated successfully'})
    else:
        return jsonify({'message': 'User not found'})


@app.route('/add_fruit', methods=['POST'])
def add_user():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    new_fruit = Fruit(name=name, quantity=quantity)
    db.session.add(new_fruit)
    db.session.commit()
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
    return render_template('table.html',fruits=fruits)
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

@app.route('/login')
def login_form():
    return render_template('login.html')
