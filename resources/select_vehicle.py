from flask import request
from flask_restful import Resource
from models import db, Vehicle
from datetime import datetime, timedelta
import pytz

class SelectVehicle(Resource):
    def put(self, license_plate_number):
        """
        Select a vehicle for a ride by license plate.
        Query parameter: 'distance' (int)
        E.g., PUT /select/ABC123?distance=50
        """
        distance = request.args.get('distance', type=int)
        if not distance:
            return {"message": "Please provide distance parameter"}, 400

        vehicle = Vehicle.query.filter_by(license_plate_number=license_plate_number).first()
        if not vehicle:
            return {"message": "Vehicle not found"}, 404

        if vehicle.on_route:
            return {
                "message": "Vehicle is already on route",
                "available_from": vehicle.available_from.strftime("%Y-%m-%d %H:%M:%S")
            }, 400

        # Calculate travel time
        if distance <= 50:
            travel_time = distance * 2
            actual_distance = distance * 0.5 if vehicle.fuel_type == "hybrid" else distance
        else:
            travel_time = distance
            actual_distance = distance

        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)
        available_time = current_time + timedelta(minutes=travel_time)

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

    def patch(self, license_plate_number):
        """
        Mark a vehicle as available again (early return).
        PATCH /select/ABC123
        """
        vehicle = Vehicle.query.filter_by(license_plate_number=license_plate_number).first()
        if not vehicle:
            return {"message": "Vehicle not found"}, 404

        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)

        vehicle.on_route = False
        vehicle.available_from = current_time
        db.session.commit()

        return {
            "message": f"Vehicle {license_plate_number} is now available",
            "available_from": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }, 200
