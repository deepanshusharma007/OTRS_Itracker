from app import app
from models import db


with app.app_context():
    db.init_app(app)  # Ensure the app is initialized
    db.create_all()
    print("Tables created")