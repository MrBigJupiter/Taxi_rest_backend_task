class Config:
    """
    Configuration for the Vehicle Fleet API.
    Add environment variable usage if you like: 
    e.g., SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///vehicle_fleet.db")
    """
    SQLALCHEMY_DATABASE_URI = "sqlite:///vehicle_fleet.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

