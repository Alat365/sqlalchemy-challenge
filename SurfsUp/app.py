# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    """Listing routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date/<start_date><br/>"
        f"/api/v1.0/start-date/<start_date>/end-date/<end_date>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return results as dictionary from precipitation analysis"""
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(
        Measurement.date,
        Measurement.prcp
    ).filter(
        Measurement.date >= prev_year
    ).all()
    precip_dict = [{date:prcp} for date, prcp in precipitation]

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return JSON list of stations"""
    station_query = session.query(Station.station).all()
    stations_list = [station[0] for station in station_query]

    return jsonify({"stations":stations_list})

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperature observations in previous year for most active station"""
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station_temp = session.query(
        Measurement.date,
        Measurement.tobs
    ).filter(
        Measurement.date >= prev_year,
        Measurement.station == 'USC00519281'
    ).all()
    active_temp_dict = [{date:tobs} for date, tobs in active_station_temp]

    return jsonify({'USC00519281':active_temp_dict})

@app.route("/api/v1.0/start-date/<start_date>")
@app.route("/api/v1.0/start-date/<start_date>/end-date/<end_date>")
def start_end(start_date=None, end_date=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return min, max and average temperature observations starting at a specified date or within a date range"""
    try:
        # Convert start and end dates to datetime objects
        start = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = dt.datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else dt.date.today()

        # Query temperature statistics based on date range
        query = session.query(
            Measurement.date,
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(
            Measurement.date >= start,
            Measurement.date <= end if end else dt.date.today()
        ).group_by(Measurement.date).all()

        if query:
            results = []
            for stats in query:
                result = {stats[0]: {
                    "TMIN": stats[1],
                    "TMAX": stats[2],
                    "TAVG": stats[3]
                }}
                results.append(result)

            return jsonify(results)

        return jsonify({"error": "No temperature data found within the specified date range."}), 404

    except ValueError:
        return jsonify({"error": "Invalid date format. Please use the format YYYY-MM-DD."}), 400

if __name__ == '__main__':
    app.run(debug=True)