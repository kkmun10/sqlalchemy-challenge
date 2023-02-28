import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)
# Flask Routes
#Start at homepage and list available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis retrieve only the last 12 months of data"""
    session = Session(engine)
    data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').\
    order_by(Measurement.date.desc()).all()
    session.close()
    
    prcp_list = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list) 

@app.route("/api/v1.0/stations")
def station():
    """ Return a JSON list of stations from the dataset."""
    session = Session(engine)
    station_info = session.query(Station.station, Station.id).all()
    session.close()
    
    all_stations = []
    for station, name in station_info:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)
        
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a JSON list of temperature observations for the previous year."""
    active_temps = session.query(Measurement.station, Measurement.tobs, Measurement.date)\
    .filter(Measurement.date >= '2016-08-23')\
    .filter(Measurement.date <= '2017-08-23')\
    .filter(Measurement.station == "USC00519281").all()
    session.close()
    
    active_last_year = []
    for station, tobs, date in active_temps:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        active_last_year.append(dates_tobs_dict)
        
    return jsonify(active_last_year) 

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date"""
    start_date_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    session.close() 
    
    start_date_temps =[]
    for min, avg, max in start_date_query:
        start_date_dict = {}
        start_date_dict["min"] = min
        start_date_dict["average"] = avg
        start_date_dict["max"] = max
        start_date_temps.append(start_date_dict)
    
    return jsonify(start_date_temps)


@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
  
  
    start_end_temps =[]
    for min, avg, max in start_end_query:
        start_end_dict = {}
        start_end_dict["min"] = min
        start_end_dict["average"] = avg
        start_end_dict["max"] = max
        start_end_temps.append(start_end_dict) 
    

    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)