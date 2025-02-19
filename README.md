# Vehicle Fleet Management API

This API provides REST endpoints for managing a vehicle fleet, including:
- Adding and removing vehicles.
- Updating vehicle information.
- Retrieving fleet details.
- Calculating best vehicle combinations for trips based on distance and passenger count.
- Selecting a vehicle for a trip and marking it on-route.

## Table of Contents
1. [Overview](#overview)  
2. [Requirements & Installation](#requirements--installation)  
3. [Configuration](#configuration)  
4. [Database Schema](#database-schema)  
5. [Endpoints](#endpoints)  
6. [Example Usage](#example-usage)  
7. [Notes & Future Improvements](#notes--future-improvements)

---

## Overview

The API is built with **Flask**, **Flask-RESTful**, **SQLAlchemy**, and **pytz**:
- **Flask**: Main web framework.  
- **Flask-RESTful**: Simplifies creation of REST endpoints as `Resources`.  
- **SQLAlchemy**: Object-relational mapper for the database (`sqlite` by default).  
- **pytz**: Time zone utilities (e.g., “Europe/Bucharest”).

When querying the entire fleet, if a vehicle is **not on route** (`on_route == false`), its `available_from` field is automatically set to the current time (in EET). This ensures that any vehicle that’s free is updated to “now” availability.

---

## Requirements & Installation

1. **Python 3.9+** (recommended).
2. Create and activate a **virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\\Scripts\\activate   # On Windows
   ```
3. **Install dependencies** (after cloning this repo or placing `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```
5. The server is available at `http://127.0.0.1:5000`.

---

## Configuration

A simple example configuration (`config.py`):
```python
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///vehicle_fleet.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
```

In your main file (e.g., `app.py`), load config and initialize:
```python
app.config.from_object(Config)
db.init_app(app)
```

---

## Database Schema

**Table:** `vehicle`
| Column                | Type            | Description                                        |
|-----------------------|-----------------|----------------------------------------------------|
| **id**                | Integer (PK)    | Unique identifier.                                 |
| **fuel_type**         | Text            | E.g. `"gasoline"` or `"hybrid"`.                   |
| **range**             | Integer         | Distance (in km) a vehicle can travel on full tank.|
| **distance**          | Integer         | Last recorded trip distance (if applicable).       |
| **seats**             | Integer         | Number of passenger seats.                         |
| **license_plate_number** | Text (Unique) | Unique plate identifier.                           |
| **car_brand**         | Text            | E.g. `"Toyota"`, `"Honda"`.                        |
| **driver_name**       | Text            | Name of the driver.                                |
| **on_route**          | Boolean         | `True` if currently occupied.                      |
| **available_from**    | DateTime        | Next availability time. If `on_route == false`, updated to “now” on every GET of the whole fleet.

---

## Endpoints

**1. `GET /all/fleet`**  
   - **Description**: Retrieve **all vehicles** in the fleet.
   - **Behavior**: If `on_route == false`, the system automatically updates the vehicle’s `available_from` to the current EET time and commits that to the database.
   - **Response**: Returns an array of vehicles.

**2. `POST /all/fleet`**  
   - **Description**: Add a new vehicle to the fleet.
   - **Body (JSON)**: Must include `fuel_type`, `range`, `distance`, `seats`, `license_plate_number`, `car_brand`, `driver_name`, and `on_route`.
   - **Behavior**: Automatically sets `available_from` to the current EET time.

**3. `PUT /all/fleet`**  
   - **Description**: Update an existing vehicle’s details by either its `id` or `license_plate_number`.
   - **Body (JSON)**: Only send the fields you want to update (e.g., `car_brand`, `seats`, etc.).  
   - **Behavior**: Resets `available_from` to the current EET time.

**4. `DELETE /all/fleet`**  
   - **Description**: Remove a vehicle by `id` or `license_plate_number`.
   - **Body (JSON)**: Provide one of those keys to find the vehicle.

**5. `GET /combinations`**  
   - **Query Params**: `passengers` (int), `distance` (int).
   - **Description**: Returns vehicle combinations with profit calculations based on passenger count, distance, and whether the vehicle is `hybrid` or `gasoline`.

**6. `PUT /select/<license_plate_number>`**  
   - **Query Param**: `distance` (int).
   - **Description**: Mark a specific vehicle (by license plate) as in use; sets `on_route=true` and calculates `available_from` after the trip.

**7. `PATCH /select/<license_plate_number>`**  
   - **Description**: Mark a vehicle as available again (early return).

---

## Example Usage

1. **Add a Vehicle**:
   ```bash
   curl -X POST http://127.0.0.1:5000/all/fleet \
   -H "Content-Type: application/json" \
   -d '{
     "fuel_type": "gasoline",
     "range": 400,
     "distance": 0,
     "seats": 5,
     "license_plate_number": "ABC123",
     "car_brand": "Toyota",
     "driver_name": "John Smith",
     "on_route": false
   }'
   ```
2. **Get All Vehicles**:
   ```bash
   curl http://127.0.0.1:5000/all/fleet
   ```
   - If the vehicle is offline (`on_route=false`), `available_from` will be updated to now (in EET).

3. **Best Combinations**:
   ```bash
   curl http://127.0.0.1:5000/combinations?passengers=3&distance=60
   ```
   - Returns a list of possible vehicles, sorted by profit.

---

## Notes & Future Improvements
- **Timezones**: Everything updates `available_from` to **“Europe/Bucharest”** time. If you need strict UTC, store in UTC and convert on display.
- **Data Validation**: Consider using libraries like **Marshmallow** or performing stricter checks (e.g., `seats >= 1`).
- **Migrations**: To handle schema changes gracefully, use **Flask-Migrate**.
- **Production**: For deployment, use a WSGI server like `gunicorn` and consider a robust DB (e.g., PostgreSQL).

---

That’s the core documentation in Markdown form, highlighting the API’s usage, endpoint behaviors, and data model—**without** the full source code. Feel free to expand or modify as your project evolves!