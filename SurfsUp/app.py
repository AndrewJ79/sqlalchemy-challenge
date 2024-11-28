from flask import Flask, jsonify
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Create the engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database into a new model
Base = automap_base()

# Use the updated reflection method with autoload
Base.prepare(autoload_with=engine)

# List the available table names for debugging
print("Available tables:", Base.classes.keys())

# Map the tables to variables
Measurement = Base.classes.measurement  # Replace 'measurement' with the actual table name if different
Station = Base.classes.station          # Replace 'station' with the actual table name if different

# Create a session to link Python to the database
session = Session(engine)

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations = session.query(Station.station).all()

    # Convert to a list
    stations_list = [station[0] for station in stations]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.id))\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.id).desc())\
                                 .first()

    # Query temperature observations for the most active station
    tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station[0])\
                                               .filter(Measurement.date >= one_year_ago).all()

    # Convert to a list
    tobs_list = [temp[0] for temp in tobs_data]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Query min, avg, and max temperatures from the start date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()

    # Convert to a list
    temps = list(np.ravel(results))

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Query min, avg, and max temperatures for the specified date range
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert to a list
    temps = list(np.ravel(results))

    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
