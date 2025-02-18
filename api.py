from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from datetime import date, datetime
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
    on_route: Mapped[bool] = mapped_column(nullable=False)
    available_from: Mapped[date] = mapped_column(Date, nullable=False)

# Argument parsing

vehicle_args = reqparse.RequestParser()
vehicle_args.add_argument('fuel_type', type=str, help='Type of fuel or mode a car uses.')
vehicle_args.add_argument('range', type=int, help='How far a car can go with one full tank.')
vehicle_args.add_argument('distance', type=int, help= 'Length of the trip by the passansgers.')
vehicle_args.add_argument('seats', type=int, help='Number of available seats in the vehicle.')
vehicle_args.add_argument('license_plate_number', type=str, help='License plate number of the car.')
vehicle_args.add_argument('car_brand', type=str, help='Brand of the car.')
vehicle_args.add_argument('driver_name', type=str, help='The name of the driver.')
vehicle_args.add_argument('on_route', type = bool, help= 'Is it occupied for the time being')
vehicle_args.add_argument('available_from', type =date, help= 'From when the car is available for use' )

fleet_vehicles = {
    'id': fields.Integer,
    'fuel_type': fields.String,
    'range': fields.Integer,
    'distance': fields.Integer,
    'seats': fields.Integer,
    'license_plate_number': fields.String,
    'car_brand': fields.String,
    'driver_name': fields.String,
    'on_route': fields.Boolean,
    'available_from': fields.DateTime
}

# Get all information on the fleet
class GetAllFleet(Resource):
    @marshal_with(fleet_vehicles)
    def get(self):
        whole_fleet = Vehicle.query.all()
        return whole_fleet
    
    @marshal_with(fleet_vehicles)
    def post(self):
        args = vehicle_args.parse_args()

        try:
            available_from = datetime.strptime(args['available_from'], '%Y-%m-%d %H:%M:%S') if args['available_from'] else datetime.utcnow()
        except ValueError:
            return {"message": "Invalid datetime format for available_from. Use YYYY-MM-DD HH:MM:SS."}, 400
        
        new_entry = Vehicle(fuel_type = args['fuel_type'], 
                            range = args['range'],
                            distance = args['distance'], 
                            seats = args['seats'], 
                            license_plate_number = args['license_plate_number'],
                            car_brand = args['car_brand'],
                            driver_name = args['driver_name'],
                            on_route = args['on_route'],
                            available_from = available_from)
        
        db.session.add(new_entry)
        db.session.commit()
        fleet = Vehicle.query.all()
        return fleet, 201
    
    @marshal_with(fleet_vehicles)
    def put(self):
        """Update a vehicle's information by license plate."""
        args = vehicle_args.parse_args()
        vehicle = Vehicle.query.filter_by(license_plate_number=args['license_plate_number']).first()

        if not vehicle:
            return {"message": "Vehicle not found."}, 404

        for field in ['fuel_type', 'range', 'distance', 'seats', 'car_brand', 'driver_name', 'on_route']:
            if args[field] is not None:
                setattr(vehicle, field, args[field])

        if args['available_from']:
            vehicle.available_from = args['available_from']

        db.session.commit()
        return vehicle, 200

    def delete(self):
        """Delete a vehicle by license plate."""
        args = vehicle_args.parse_args()
        vehicle = Vehicle.query.filter_by(license_plate_number=args['license_plate_number']).first()

        if not vehicle:
            return {"message": "Vehicle not found."}, 404

        db.session.delete(vehicle)
        db.session.commit()
        return {"message": f"Vehicle with license plate {args['license_plate_number']} has been deleted."}, 200

api.add_resource(GetAllFleet, '/all/fleet')


@app.route('/')
def name():
    return "Hello World"

if __name__ == '__main__':
    app.run(debug=True)