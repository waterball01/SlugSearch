from flask import Flask, request, render_template, redirect, url_for, jsonify
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255))
    location = db.Column(db.String(50))
    time = db.Column(db.String(20))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)  # Add a description field

with app.app_context():
    db.drop_all()
    db.create_all()

# Get unique locations from items
locations = ['Cowell', "Stevenson", "Crown", "Merril", "College 9", "JRL", "Porter", "Kresge", "RCC", "Oakes", "McHenry", "S&E Library", "Other"]
categories = ['Headphones', 'Bottles', 'Jackets', 'Hats', "Keys", "Wallets", "Other"]

@app.route("/", methods=['GET', 'POST'])
def index():
    selected_location = request.form.get('location')
    selected_category = request.form.get('category')

    if selected_location == 'all':
        selected_location = None

    if selected_category == 'all':
        selected_category = None

    if selected_location and selected_category:
        filtered_items = Item.query.filter_by(location=selected_location, category=selected_category).all()
    elif selected_location:
        filtered_items = Item.query.filter_by(location=selected_location).all()
    elif selected_category:
        filtered_items = Item.query.filter_by(category=selected_category).all()
    else:
        filtered_items = Item.query.all()
    

    return render_template("index.html", items=filtered_items, locations=locations, categories=categories,
                           selected_location=selected_location, selected_category=selected_category)


@app.route("/add")
def add():
    return render_template('add.html', locations=locations, categories=categories) # Create a new HTML file for the "add" page

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get other form data
        location = request.form.get('selected_location')
        category = request.form.get('selected_category')
        description = request.form.get('description')  # Get description data
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to database
        new_item = Item(image_path=file_path, location=location, time=current_datetime, category=category, description=description)
        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('index'))

    return "Invalid file type"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/claim/<int:item_id>', methods=['POST'])
def claim_item(item_id):
    # Find the item by ID
    item = Item.query.get(item_id)

    if item:
        # Remove the item from the database
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def is_valid_image(file_path):
    # Add your image validation logic here
    # Example: check if the file is an actual image
    return True


def is_valid_location(location):
    return location in locations


def is_valid_category(category):
    return category in categories


if __name__ == '__main__':
    app.run(debug=True)
