import math
import pytz
from datetime import datetime
from flask import request
from flask_restful import Resource
from models import Vehicle

class BestCombination(Resource):
    def get(self):
        """
        Get the best combination and profits for each ride.
        Query parameters: 'passengers' (int), 'distance' (int)
        Example: GET /combinations?passengers=4&distance=75
        """
        passengers = request.args.get('passengers', type=int)
        distance = request.args.get('distance', type=int)

        if not passengers or not distance:
            return {"message": "Please provide both passengers and distance parameters"}, 400

        eet = pytz.timezone("Europe/Bucharest")
        current_time = datetime.now(tz=eet)

        fleet = Vehicle.query.filter(
            (Vehicle.on_route == False) |
            (Vehicle.available_from <= current_time)
        ).all()

        combinations = []
        for vehicle in fleet:
            # Must have enough seats for passengers
            if vehicle.seats >= passengers:
                if distance <= 50:
                    travel_time = distance * 2  # 2 minutes per km
                    # For hybrid, half the distance is electric or some custom logic
                    actual_distance = distance * 0.5 if vehicle.fuel_type == "hybrid" else distance
                else:
                    travel_time = distance  # 1 minute per km
                    actual_distance = distance

                half_hours = math.ceil(travel_time / 30)
                km_revenue = actual_distance * 2
                time_revenue = half_hours * 2
                total_revenue = km_revenue + time_revenue

                km_cost = actual_distance * (1 if vehicle.fuel_type == "hybrid" else 2)
                profit = total_revenue - km_cost

                status = ('Available now' if not vehicle.on_route
                          else f'Available from {vehicle.available_from.strftime("%Y-%m-%d %H:%M:%S")}')

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
                    'current_status': status
                })

        # Sort by profit descending
        combinations.sort(key=lambda x: x['profit'], reverse=True)

        return {
            'request_details': {
                'passengers': passengers,
                'distance': distance,
                'query_time': current_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            'possible_combinations': combinations
        }
