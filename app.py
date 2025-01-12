from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///needed_items.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    remaining_quantity = db.Column(db.Integer, nullable=False)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.filter(Item.remaining_quantity > 0).all()
    return jsonify([{'id': item.id, 'name': item.name, 'remaining_quantity': item.remaining_quantity} for item in items])

@app.route('/submit', methods=['POST'])
def submit_items():
    data = request.json.get('submissions', [])
    errors = []

    for submission in data:
        item = Item.query.get(submission['item_id'])
        quantity = submission['quantity']
        if item and item.remaining_quantity >= quantity:
            item.remaining_quantity -= quantity
            db.session.add(Submission(item_id=item.id, quantity=quantity))
        else:
            errors.append({'item_id': submission['item_id'], 'error': 'Invalid quantity or item not found'})

    db.session.commit()

    if errors:
        return jsonify({'message': 'Some submissions failed', 'errors': errors}), 400
    return jsonify({'message': 'All submissions successful'}), 200

if __name__ == '__main__':
    db.create_all()  # Initialize the database
    app.run(debug=True)
