import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#Creating the flask routes
#Source for html characters: https://www.w3schools.com/html/html_entities.asp
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )



# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all dates and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a loop to store the data
    prcp_data = []
    for date, prcp in results:
        results_dict = {}
        results_dict["date"] = date
        results_dict["prcp"] = prcp
        prcp_data.append(results_dict)

    return jsonify(prcp_data)



# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all station names
    results = session.query(Station.name).all()
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)



# Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query dates and tobs for most active station
    # Source: https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= '2016-08-23').all()
    session.close()

    # Create a loop to store the data
    year_data = []
    for date, tobs in results:
        results_dict = {}
        results_dict["Most active station"] = "USC00519281"
        results_dict["Date"] = date
        results_dict["TOBS"] = tobs
        year_data.append(results_dict)

    return jsonify(year_data)



# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def starts(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, and avg of the given date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    # Create a loop to store the data
    query_date = []
    for min, max, avg in results:
        results_dict = {}
        results_dict["Input_date"] = start
        results_dict["TMin"] = min
        results_dict["TMax"] = max
        results_dict["TAvg"] = avg
        query_date.append(results_dict)

    return jsonify(query_date)


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a start-end range.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query min, max, and avg of the date range
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Create a loop to store the data
    query_date = []
    for min, max, avg in results:
        results_dict = {}
        results_dict["Input_dates"] = start , end
        results_dict["TMin"] = min
        results_dict["TMax"] = max
        results_dict["TAvg"] = avg
        query_date.append(results_dict)

    return jsonify(query_date)

if __name__ == '__main__':
    app.run(debug=True)
