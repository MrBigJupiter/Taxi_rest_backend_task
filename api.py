from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.orm import Mapped, mapped_column
from flask_restful import reqparse, Resource, marshal_with, fields, Api
import pytz
import math

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vehicle_fleet.db" # Tells SQLAlchemy what database to connect to
db = SQLAlchemy(app=app)

api = Api(app=app)

class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    fuel_type: Mapped[str] = mapped_column(nullable=False) 
    range: Mapped[int] = mapped_column(nullable=False)
    distance: Mapped[int] = mapped_column(nullable=False) 
    seats: Mapped[int] = mapped_column(nullable=False) 
    license_plate_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    car_brand: Mapped[str] = mapped_column(nullable=False)
    driver_name: Mapped[str] = mapped_column(nullable=False)
    on_route: Mapped[bool] = mapped_column(nullable=False)
    available_from: Mapped[datetime] = mapped_column(nullable=False)

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
#vehicle_args.add_argument('available_from', type =date, help= 'From when the car is available for use' )

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
        """Add a new vehicle to the fleet."""
        args = vehicle_args.parse_args()
        eet = pytz.timezone("Europe/Bucharest")
        available_from = datetime.now(tz=eet)

        new_vehicle = Vehicle(
            fuel_type=args['fuel_type'],
            range=args['range'],
            distance=args['distance'],
            seats=args['seats'],
            license_plate_number=args['license_plate_number'],
            car_brand=args['car_brand'],
            driver_name=args['driver_name'],
            on_route=args['on_route'],
            available_from=available_from
        )
        
        db.session.add(new_vehicle)
        db.session.commit()
        return new_vehicle, 201
    
    @marshal_with(fleet_vehicles)
    def put(self):
        """Update a vehicle's information by ID or license plate."""
        args = vehicle_args.parse_args()
        vehicle = None
        eet = pytz.timezone("Europe/Bucharest")
        available_from = datetime.now(tz=eet)
        
        if 'id' in args and args['id']:
            vehicle = Vehicle.query.get(args['id'])
        elif args['license_plate_number']:
            vehicle = Vehicle.query.filter_by(license_plate_number=args['license_plate_number']).first()

        if not vehicle:
            return {"message": "Vehicle not found."}, 404

        for field in ['fuel_type', 'range', 'distance', 'seats', 'car_brand', 'driver_name', 'on_route']:
            if args[field] is not None:
                setattr(vehicle, field, args[field])

        vehicle.available_from = available_from

        db.session.commit()
        return vehicle, 200

    @marshal_with(fleet_vehicles)
    def delete(self):
        """Delete a vehicle by ID or license plate."""
        args = vehicle_args.parse_args()
        
        vehicle = None
        if 'id' in args and args['id']:
            vehicle = Vehicle.query.get(args['id'])
        elif args['license_plate_number']:
            vehicle = Vehicle.query.filter_by(license_plate_number=args['license_plate_number']).first()
        
        if not vehicle:
            return {"message": "Vehicle not found."}, 404

        db.session.delete(vehicle)
        db.session.commit()
        return {"message": f"Vehicle with ID {args.get('id') or args['license_plate_number']} has been deleted."}, 200

class BestCombination(Resource):
    def get(self):
        """Get the best combination and profits for each ride"""
        passengers = request.args.get('passengers', type=int)
        distance = request.args.get('distance', type=int)
        
        if not passengers or not distance:
            return {"message": "Please provide both passengers and distance parameters"}, 400
        
        # Get current time in EET
        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)
        
        # Get all vehicles that are either available now or will be soon
        fleet = Vehicle.query.filter(
            (Vehicle.on_route == False) | 
            (Vehicle.available_from <= current_time)
        ).all()
        
        combinations = []
        
        for vehicle in fleet:
            if vehicle.seats >= passengers:
                # Calculate time and distance based on conditions
                if distance <= 50:
                    travel_time = distance * 2  # 2 minutes per km
                    if vehicle.fuel_type == "hybrid":
                        actual_distance = distance * 0.5
                    else:
                        actual_distance = distance
                else:
                    travel_time = distance  # 1 minute per km
                    actual_distance = distance
                
                half_hours = math.ceil(travel_time / 30)
                
                # Calculate revenue and costs
                km_revenue = actual_distance * 2
                time_revenue = half_hours * 2
                total_revenue = km_revenue + time_revenue
                
                km_cost = actual_distance * (1 if vehicle.fuel_type == "hybrid" else 2)
                profit = total_revenue - km_cost
                
                combinations.append({
                    'license_plate': vehicle.license_plate_number,
                    'car_brand': vehicle.car_brand,
                    'fuel_type': vehicle.fuel_type,
                    'seats': vehicle.seats,
                    'travel_time_minutes': travel_time,
                    'actual_distance': actual_distance,
                    'revenue': total_revenue,
                    'costs': km_cost,
                    'profit': profit,
                    'current_status': 'Available now' if not vehicle.on_route else f'Available from {vehicle.available_from.strftime("%Y-%m-%d %H:%M:%S")}'
                })
        
        combinations.sort(key=lambda x: x['profit'], reverse=True)
        
        return {
            'request_details': {
                'passengers': passengers,
                'distance': distance,
                'query_time': current_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            'possible_combinations': combinations
        }

class SelectVehicle(Resource):
    def put(self, license_plate_number):
        """Select a vehicle for a ride and schedule its availability"""
        distance = request.args.get('distance', type=int)
        if not distance:
            return {"message": "Please provide distance parameter"}, 400

        # Find vehicle with exact license plate format (e.g., "AAA-001")
        vehicle = Vehicle.query.filter_by(license_plate_number=license_plate_number).first()
        
        if not vehicle:
            return {"message": "Vehicle not found"}, 404
            
        if vehicle.on_route:
            return {
                "message": "Vehicle is already on route",
                "available_from": vehicle.available_from.strftime("%Y-%m-%d %H:%M:%S")
            }, 400
            
        # Calculate travel time and future availability
        if distance <= 50:
            travel_time = distance * 2
            if vehicle.fuel_type == "hybrid":
                actual_distance = distance * 0.5
            else:
                actual_distance = distance
        else:
            travel_time = distance
            actual_distance = distance
            
        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)
        available_time = current_time + timedelta(minutes=travel_time)
        
        # Update vehicle status
        vehicle.on_route = True
        vehicle.available_from = available_time
        db.session.commit()
        
        return {
            "message": f"Vehicle {license_plate_number} has been set on route",
            "trip_details": {
                "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "travel_time_minutes": travel_time,
                "actual_distance": actual_distance,
                "will_be_available": available_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, 200
        
    def patch(self, license_plate):
        """Mark vehicle as available again (early return)"""
        vehicle = Vehicle.query.filter_by(license_plate_number=license_plate).first()
        
        if not vehicle:
            return {"message": "Vehicle not found"}, 404
            
        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)
        
        vehicle.on_route = False
        vehicle.available_from = current_time
        db.session.commit()
        
        return {
            "message": f"Vehicle {license_plate} is now available",
            "available_from": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }, 200


api.add_resource(GetAllFleet, '/all/fleet')
api.add_resource(BestCombination, '/combinations')
api.add_resource(SelectVehicle, '/select/<string:license_plate_number>')

@app.route('/')
def name():
    return "Hello World"

if __name__ == '__main__':
    app.run(debug=True)