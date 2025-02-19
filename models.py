from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime

db = SQLAlchemy()

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
    available_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
