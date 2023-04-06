# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
       f"The available routes are:<br/>"
        f"<a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation</a><br/>"
        f"<a href=\"/api/v1.0/stations\">/api/v1.0/stations</a><br/>"
        f"<a href=\"/api/v1.0/tobs\">/api/v1.0/tobs</a><br/>"
        f"<a href=\"/api/v1.0/2016-07-24\">/api/v1.0/2016-07-24</a><br/>"
        f"<a href=\"/api/v1.0/2016-07-24/2016-07-31\">/api/v1.0/2016-07-24/2016-07-31</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert query results to Dictionary with date as key and prcp as value; return the JSON representation of dictionary."""

# Precipitation Query
    previous_twelve_months = session.query(Measurement.prcp, Measurement.date).filter((Measurement.date) >= '2016-08-23').filter((Measurement.date) <='2017.08-23')
    
    session.close()

 # Create a dictionary from the row data 
    all_prcps = {}
    for prcp, date in previous_twelve_months:   
        if not prcp:
            print(f'missing {date}')
            continue
        all_prcps[date]=prcp

    return jsonify(all_prcps)



@app.route("/api/v1.0/stations")
def stations():
    # Create session 
    session = Session(engine)

    # Station Query
    station_query = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_query))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year"""
    # Create session
    session = Session(engine)

    # tobs query for previous twelve months
    station_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(Measurement.date <='2017.08-23')

    session.close()

    # Convert list of tuples into normal list
    last_year_tobs = [station_tobs[1] for tobs in station_tobs]

    return jsonify(last_year_tobs)


@app.route("/api/v1.0/<start_date>")
def calc_temps(start_date):
    
    # Create session
    session = Session(engine)
    
    # query for date   
    temp_data = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()
    
    session.close()

    return jsonify(temp_data)


@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_week(start_date, end_date):
    
    # Create session
    session = Session(engine)
    
    # query for date   
    week_data = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    return jsonify(week_data)

    


if __name__ == '__main__':
    app.run(debug=True)