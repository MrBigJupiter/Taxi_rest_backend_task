from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from flask_restful import reqparse, Resource, marshal_with, fields, Api

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vehicle_fleet.db" # Tells SQLAlchemy what database to connect to
db = SQLAlchemy(app=app)

api = Api(app=app)

class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fuel_type: Mapped[str] = mapped_column(nullable=False) # Either fuel or hybrid
    distance: Mapped[int] = mapped_column(nullable=False) # distance in km for how far a car can go
    seats: Mapped[int] = mapped_column(nullable=False) # number of seats available for passangers
    license_plate_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    car_brand: Mapped[str] = mapped_column(nullable=False)
    driver_name: Mapped[str] = mapped_column(nullable=False)

# Argument parsing

vehicle_args = reqparse.RequestParser()
vehicle_args.add_argument('fuel_type', type=str, help='Type of fuel or mode a car uses.')
vehicle_args.add_argument('distance', type=int, help='How far a car can go with one full tank.')
vehicle_args.add_argument('seats', type=int, help='Number of available seats in the vehicle.')
vehicle_args.add_argument('license_plate_number', type=str, help='License plate number of the car.')
vehicle_args.add_argument('car_brand', type=str, help='Brand of the car.')
vehicle_args.add_argument('driver_name', type=str, help='The name of the driver.')

fleet_vehicles = {
    'id': fields.Integer,
    'fuel_type': fields.String,
    'distance': fields.Integer,
    'seats': fields.Integer,
    'license_plate_number': fields.String,
    'car_brand': fields.String,
    'driver_name': fields.String
}


# Routing using the flask_restful package

# Get all information on the fleet
class GetAllFleet(Resource):
    @marshal_with(fleet_vehicles)
    def get(self):
        whole_fleet = Vehicle.query.all()
        return whole_fleet
    
    @marshal_with(fleet_vehicles)
    def post(self):
        args = vehicle_args.parse_args()
        new_entry = Vehicle(fuel_type = args['fuel_type'], 
                            distance = args['distance'], 
                            seats = args['seats'], 
                            license_plate_number = args['license_plate_number'],
                            car_brand = args['car_brand'],
                            driver_name = args['driver_name'])
        
        db.session.add(new_entry)
        db.session.commit()
        fleet = Vehicle.query.all()
        return fleet, 201

api.add_resource(GetAllFleet, '/all/fleet')


@app.route('/')
def name():
    return "Hello World"

if __name__ == '__main__':
    app.run(debug=True)