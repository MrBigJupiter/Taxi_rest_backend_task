from datetime import datetime
import pytz
from flask_restful import Resource, reqparse, marshal_with, fields
from flask import request
from models import db, Vehicle

# Specify the output fields for marshalling
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

# Define argument parser
vehicle_args = reqparse.RequestParser()
vehicle_args.add_argument('id', type=int, help='Vehicle ID.')
vehicle_args.add_argument('fuel_type', type=str, help='Type of fuel or mode a car uses.')
vehicle_args.add_argument('range', type=int, help='How far a car can go with one full tank.')
vehicle_args.add_argument('distance', type=int, help='Length of the trip by the passengers.')
vehicle_args.add_argument('seats', type=int, help='Number of available seats in the vehicle.')
vehicle_args.add_argument('license_plate_number', type=str, help='License plate number of the car.')
vehicle_args.add_argument('car_brand', type=str, help='Brand of the car.')
vehicle_args.add_argument('driver_name', type=str, help='Name of the driver.')
vehicle_args.add_argument('on_route', type=bool, help='Is it occupied for the time being?')

class GetAllFleet(Resource):
    @marshal_with(fleet_vehicles)
    def get(self):
        """
        Retrieve a list of all vehicles in the fleet.
        If on_route == False, set available_from to the current time in EET.
        """
        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)

        whole_fleet = Vehicle.query.all()

        # Update `available_from` for vehicles that are not on_route
        for vehicle in whole_fleet:
            if not vehicle.on_route:
                vehicle.available_from = current_time

        # Persist these changes so next time we query, they're updated
        db.session.commit()

        return whole_fleet, 200

    @marshal_with(fleet_vehicles)
    def post(self):
        """
        Add a new vehicle to the fleet.
        Automatically sets 'available_from' to current time in EET.
        """
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
        """
        Update a vehicle's information by ID or license plate.
        """
        args = vehicle_args.parse_args()
        eet = pytz.timezone("Europe/Bucharest")
        available_from = datetime.now(tz=eet)

        vehicle = None
        if args['id']:
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
        """
        Delete a vehicle by ID or license plate.
        """
        args = vehicle_args.parse_args()
        vehicle = None

        if args['id']:
            vehicle = Vehicle.query.get(args['id'])
        elif args['license_plate_number']:
            vehicle = Vehicle.query.filter_by(license_plate_number=args['license_plate_number']).first()

        if not vehicle:
            return {"message": "Vehicle not found."}, 404

        db.session.delete(vehicle)
        db.session.commit()
        return {"message": f"Vehicle with ID {args.get('id') or args['license_plate_number']} has been deleted."}, 200
