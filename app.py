import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, desc
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"<strong><u>Available Routes:</u></strong><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/> <br/>"
        f"<strong><u>Temperature Search by Date: (YYYY-MM-DD)</u></strong><br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of all precipitation values"""
    # Perform a query to retrieve the date and precipitation score for the last 12 months
    query = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation = []
    for date, prcp in query:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.name, Station.station).all()

    session.close()

    return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temperatures for the most active station over the last year of data"""
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return the most active station
    active_station = session.query(Station.station, Station.name, func.count(Measurement.station)).\
    filter(Measurement.station == Station.station).\
    group_by(Station.name).\
    order_by(desc(func.count(Measurement.station))).all()[0][0]   
    print(active_station)

    # Data over the last twelve months
    twelve_months = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == active_station).\
    filter(Measurement.date >= dt.date(2017, 8, 23) - (dt.timedelta(days=365))).\
    order_by(Measurement.date).all()

    session.close()

    return jsonify(twelve_months)


@app.route("/api/v1.0/<start>")
def temp_by_start_date(start):
    """Fetch the TMIN, TAVG and TMAX for all dates grater than and equal to the date that matches
       the path variable supplied by the user."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = start.replace("/", "-")

    start_temp = session.query(Measurement.date, Station.name, Measurement.station, func.min(Measurement.tobs).label("Min"), func.max(Measurement.tobs).label("Max"), func.avg(Measurement.tobs).label("Average")).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).\
    group_by(Measurement.station).all()
    
    start_list = []
    for date, name, station, Min, Max, Average in start_temp:
        end_dict = {}
        end_dict["Date"] = date
        end_dict["Name"] = name
        end_dict["Station"] = station
        end_dict["Min"] = Min
        end_dict["Max"] = Max
        end_dict["Average"] = Average
        start_list.append(end_dict)
    
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_by_dates(start, end):
    """Fetch the TMIN, TAVG and TMAX for all dates between the start and end date inclusive, that matches
       the path variable supplied by the user."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = start.replace("/", "-")
    end_date = end.replace("/", "-")

    start_temp = session.query(Measurement.date, Station.name, Measurement.station, func.min(Measurement.tobs).label("Min"), func.max(Measurement.tobs).label("Max"), func.avg(Measurement.tobs).label("Average")).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).\
    group_by(Measurement.station).all()
    
    end_list = []
    for date, name, station, Min, Max, Average in start_temp:
        end_dict = {}
        end_dict["Date"] = date
        end_dict["Name"] = name
        end_dict["Station"] = station
        end_dict["Min"] = Min
        end_dict["Max"] = Max
        end_dict["Average"] = Average
        end_list.append(end_dict)
    
    return jsonify(end_list)

if __name__ == '__main__':
    app.run(debug=True)
