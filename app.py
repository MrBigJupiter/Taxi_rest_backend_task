from flask import Flask
from flask_restful import Api
from config import Config
from models import db
from resources.get_all_fleet import GetAllFleet
from resources.best_combination import BestCombination
from resources.select_vehicle import SelectVehicle

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)  # Initialize SQLAlchemy with this app
    api = Api(app)

    # Register Resources
    api.add_resource(GetAllFleet, '/all/fleet')
    api.add_resource(BestCombination, '/combinations')
    api.add_resource(SelectVehicle, '/select/<string:license_plate_number>')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
