import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime
from flask import Flask, jsonify


#______________Setup database__________________#
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save references to the tables
Measurements = Base.classes.measurements
Stations = Base.classes.stations

# Create our session (link) from python to the db
session = Session(engine)

#______________Setup Flask__________________#
app = Flask(__name__)

#______________Flask Routes__________________#

@app.route("/")
def welcome():
    return (
        f"Weclome to Hawaii Weather Data Page!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"2016-2017 Precipitation* --------------------------------------------------  /api/v1.0/precipitation<br/><br/>"
        f"Weather Stations ------------------------------------------------------------  /api/v1.0/stations<br/><br/>"
        f"Temperature Observations* -----------------------------------------------  /api/v1.0/tobs<br/><br/>"
        f"Search Temperature Observations with Start Date** ----------------- /api/v1.0/[start]<br/><br/>"
        f"Search Temperature Observations with Start and End Date** ------ /api/v1.0/[start]/[end]<br/><br/>"
        f"*Note that 2016-2017 ranges from 08-23-2016 to 08-23-2017<br/>"
        f"**Please use YYYY-MM-DD format for start and end dates"
    )

# /api/v1.0/precipitation 
# Query for the dates and precipitation from last year
# Convert the query results in a Dictionary using date as the key
# and prcp as the value
# Return the json representation of your dictionary
@app.route("/api/v1.0/precipitation")
def prcp():
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_date = last_date[0]
    
    first_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    first_date = first_date.strftime("%Y-%m-%d")

    one_yr_prcp = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date.between(first_date, last_date)).all()

    prcp_list = []
    for result in one_yr_prcp:
        row = {}
        row["date"] = result[0]
        row["prcp"] = result[1]
        prcp_list.append(row)
    return jsonify(prcp_list)

# /api/v1.0/stations
# return a json list of stations from the dataset
@app.route("/api/v1.0/stations")
def weather_stations():
    stations = session.query(Stations.station, Stations.name).all()
    stations_list = []
    for station in stations:
        row = {}
        row["station"] = station[0]
        row["name"] = station[1]
        stations_list.append(row)
    return jsonify(stations_list)

# /api/v1.0/tobs
# Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    one_yr_tobs = session.query(Measurements.date, Measurements.station, Measurements.tobs).filter(Measurements.date.between('2016-08-23', '2017-08-23')).all()
    tobs_list = []
    for tob in one_yr_tobs:
        row = {}
        row["date"] = tob[0]
        row["station"] = tob[1]
        row["tobs"] = tob[2]
        tobs_list.append(row)
    return jsonify(tobs_list)


# /api/v1.0/<start> and /api/v1.0<start>/<end>
# Return a json list of temp min, temp avg, temp max for a given start or
# start to end date.
# When given the start only, calculate tmin, tavg, and tmax for all dates
# greater than and equal to the start date
# When given the start and the end date, calculate the tmin, tavg, and tmax
# for dates between the start and end date inclusive
@app.route("/api/v1.0/<start>")
def temp_info (start):
    start = datetime.strptime(start, "%Y-%m-%d")
    temp_queries = session.query(func.min(Measurements.tobs), func.round(func.avg(Measurements.tobs)), func.max(Measurements.tobs)).filter(Measurements.date >= start).all()
    temp_date_dict = {"Minimum": temp_queries[0][0], "Average": temp_queries[0][1], "Maximum": temp_queries[0][2]}
    return jsonify(temp_date_dict)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_info (start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    temp_range_queries = session.query(func.min(Measurements.tobs), func.round(func.avg(Measurements.tobs)), func.max(Measurements.tobs)).filter(Measurements.date.between(start, end)).all()
    temp_date_range_dict = {"Minimum": temp_range_queries[0][0], "Average": temp_range_queries[0][1], "Maximum": temp_range_queries[0][2]}
    return jsonify(temp_date_range_dict)


if __name__ == "__main__":
    app.run(debug = True)