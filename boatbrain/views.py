#boatbrain/views.py
import json
import plotly.express as px
import plotly.utils
import plotly.graph_objects as go
from django.shortcuts import render
from django.db import connection
import pandas as pd

import numpy as np
import folium

####
import time
from datetime import datetime, timedelta
from django.utils import timezone  # Add this import

def log_page_view(request):
    # Query total log entries
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_log")
        log_entries = cursor.fetchone()[0]

    # Query total ERROR entries
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_log WHERE log_level='ERROR'")
        error_entries = cursor.fetchone()[0]

    # Query total entries grouped by stage
    with connection.cursor() as cursor:
        cursor.execute("SELECT stage, COUNT(*) FROM application_log GROUP BY stage")
        stage_count_data = cursor.fetchall()

    # Convert to DataFrame
    stage_count_df = pd.DataFrame(stage_count_data, columns=["Stage", "Entry Count"])

    # Query all possible stages
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT stage FROM application_log")
        all_stages = [row[0] for row in cursor.fetchall()]

    # Ensure all stages are included and sorted numerically
    stage_count_df = stage_count_df.set_index("Stage").reindex(all_stages, fill_value=0).reset_index()
    stage_count_df["Stage"] = pd.to_numeric(stage_count_df["Stage"], errors="coerce")
    stage_count_df = stage_count_df.sort_values(by="Stage").dropna()

    stage_list = stage_count_df["Stage"].astype(str).tolist()
    entry_count_list = stage_count_df["Entry Count"].astype(int).tolist()

    # Create Plotly bar chart for stage count
    fig_stage = go.Figure(
        data=[
            go.Bar(
                x=stage_list,
                y=entry_count_list,
                text=entry_count_list,
                textposition="auto"
            )
        ]
    )
    fig_stage.update_layout(
        title={"text": "LOG Entries by Stage", "x": 0.5},
        xaxis_title="Stage",
        yaxis_title="Log Entries Count"
    )
    graph_json_stage = json.dumps(fig_stage, cls=plotly.utils.PlotlyJSONEncoder)

    # Query total ERROR entries grouped by stage
    with connection.cursor() as cursor:
        cursor.execute("SELECT stage, COUNT(*) FROM application_log WHERE log_level='ERROR' GROUP BY stage")
        error_stage_count_data = cursor.fetchall()

    # Convert to DataFrame
    error_stage_count_df = pd.DataFrame(error_stage_count_data, columns=["Stage", "Error Count"])
    error_stage_count_df = error_stage_count_df.set_index("Stage").reindex(all_stages, fill_value=0).reset_index()
    error_stage_count_df["Stage"] = pd.to_numeric(error_stage_count_df["Stage"], errors="coerce")
    error_stage_count_df = error_stage_count_df.sort_values(by="Stage").dropna()

    error_stage_list = error_stage_count_df["Stage"].astype(str).tolist()
    error_count_list = error_stage_count_df["Error Count"].astype(int).tolist()

    # Create Plotly bar chart for ERROR entries by stage
    fig_error_stage = go.Figure(
        data=[
            go.Bar(
                x=error_stage_list,
                y=error_count_list,
                text=error_count_list,
                textposition="auto"
            )
        ]
    )
    fig_error_stage.update_layout(
        title={"text": "ERROR Entries by Stage", "x": 0.5},
        xaxis_title="Stage",
        yaxis_title="Error Log Count"
    )
    graph_json_error_stage = json.dumps(fig_error_stage, cls=plotly.utils.PlotlyJSONEncoder)

    # Query total entries grouped by date
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATE(timestamp), COUNT(*) FROM application_log GROUP BY DATE(timestamp)")
        date_count_data = cursor.fetchall()

    # Convert to DataFrame
    date_count_df = pd.DataFrame(date_count_data, columns=["Date", "Entry Count"])
    date_count_df["Date"] = pd.to_datetime(date_count_df["Date"]).dt.strftime("%b %d, %Y")
    date_count_df = date_count_df.sort_values(by="Date")

    date_list = date_count_df["Date"].tolist()
    entry_count_date_list = date_count_df["Entry Count"].astype(int).tolist()

    # Create Plotly bar chart for date count
    fig_date = go.Figure(
        data=[
            go.Bar(
                x=date_list,
                y=entry_count_date_list,
                text=entry_count_date_list,
                textposition="auto"
            )
        ]
    )
    fig_date.update_layout(
        title={"text": "LOG Entries by Date", "x": 0.5},
        xaxis_title="Date",
        yaxis_title="Log Entry Count"
    )
    graph_json_date = json.dumps(fig_date, cls=plotly.utils.PlotlyJSONEncoder)

    # Query total INFO entries
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_log WHERE log_level='INFO'")
        info_entries = cursor.fetchone()[0]

    # Create Plotly donut chart for INFO vs ERROR
    labels = ["INFO", "ERROR"]
    values = [info_entries, error_entries]

    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=labels, 
                values=values, 
                hole=0.4,  # Makes it a donut chart
                textinfo="label+percent"
            )
        ]
    )
    fig_donut.update_layout(title={"text": "INFO vs ERROR Log Entries", "x": 0.5})
    graph_json_donut = json.dumps(fig_donut, cls=plotly.utils.PlotlyJSONEncoder)

    # Query trip types TEST vs REAL from bb_trip_log
    with connection.cursor() as cursor:
        cursor.execute("SELECT trip_type, COUNT(*) FROM bb_trip_log GROUP BY trip_type")
        trip_type_data = cursor.fetchall()

    trip_type_df = pd.DataFrame(trip_type_data, columns=["Trip Type", "Count"])
    labels_trip = trip_type_df["Trip Type"].tolist()
    values_trip = trip_type_df["Count"].tolist()

    # Create Plotly donut chart for TEST vs REAL trips
    fig_trip_donut = go.Figure(
        data=[
            go.Pie(
                labels=labels_trip, 
                values=values_trip, 
                hole=0.4,
                textinfo="label+percent"
            )
        ]
    )
    fig_trip_donut.update_layout(title={"text": "TEST vs REAL Trips", "x": 0.5})
    graph_json_trip_donut = json.dumps(fig_trip_donut, cls=plotly.utils.PlotlyJSONEncoder)   


 # Query function_name counts
    with connection.cursor() as cursor:
        cursor.execute("SELECT function_name, COUNT(*) FROM application_log GROUP BY function_name")
        function_count_data = cursor.fetchall()
    
    # Convert to DataFrame
    function_count_df = pd.DataFrame(function_count_data, columns=["Function Name", "Entry Count"])
    function_count_df = function_count_df.sort_values(by="Entry Count", ascending=False)
    
    function_list = function_count_df["Function Name"].astype(str).tolist()
    entry_count_function_list = function_count_df["Entry Count"].astype(int).tolist()
    
    # Create Plotly bar chart for function_name count
    fig_function = go.Figure(
        data=[
            go.Bar(
                x=function_list,
                y=entry_count_function_list,
                text=entry_count_function_list,
                textposition="auto"
            )
        ]
    )
    fig_function.update_layout(
        title={"text": "LOG Entries by Function Name", "x": 0.5},
        xaxis_title="Function Name",
        yaxis_title="Log Entries Count"
    )
    graph_json_function = json.dumps(fig_function, cls=plotly.utils.PlotlyJSONEncoder)
    

    with connection.cursor() as cursor:
        cursor.execute("SELECT timestamp, log_level, stage, log_message FROM application_log ORDER BY timestamp DESC")
        columns = [col[0] for col in cursor.description]  # Extract column names
        log_table_data = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert tuples to dictionaries



    # Context for template
    context = {
        "log_entries": log_entries,
        "error_entries": error_entries,
        "graph_json_stage": graph_json_stage,
        "graph_json_error_stage": graph_json_error_stage,
        "graph_json_date": graph_json_date,
        "graph_json_donut": graph_json_donut,
        "graph_json_trip_donut": graph_json_trip_donut,
        "graph_json_function": graph_json_function,
        "log_table_data": log_table_data
    }
    return render(request, "log.html", context)



##################################################################################################
#################################### other functions  ############################################
##################################################################################################

from datetime import datetime, timedelta

def format_time_12hr(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").strftime("%I:%M:%S %p")

def safe_fetchone(cursor):
    result = cursor.fetchone()
    return timezone.localtime(result[0]) if result and result[0] else None

def current_trip_page_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM bb_trip_log")
        number_trips = cursor.fetchone()[0]

        cursor.execute("SELECT trip_id FROM bb_trip_log ORDER BY bb_trip_log DESC LIMIT 1")
        # last_trip_id = cursor.fetchone()[0]  ***** UNCOMMENT THIS LINE *****
        this_trip_id=145 ### comment out this line to restore northerly functionality
        last_trip_id=145 ### comment out this line to restore northerly functionality

        cursor.execute("SELECT trip_timestamp FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        last_trip_date = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_prep_starts FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_prep_starts = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_left_house FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_left_house = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_at_ramp FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_at_ramp = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_in_water FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_in_water = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_fishing_begins FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_fishing_begins = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_return_to_ramp FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_return_to_ramp = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_boat_on_trailer FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_boat_on_trailer = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_prep_done_to_go_home FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_prep_done_to_go_home = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_leave_ramp FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_leave_ramp = safe_fetchone(cursor)

        cursor.execute("SELECT trip_time_return_home FROM bb_trip_log WHERE trip_id = %s", [last_trip_id])
        trip_time_return_home = safe_fetchone(cursor)

        # Initialize current stage number
        current_stage = 0



        stages = [
            {
                'stage': 0,
                'start_time': format_time_12hr(last_trip_date.strftime("%H:%M:%S")) if last_trip_date else None,
                'end_time': format_time_12hr(trip_time_prep_starts.strftime("%H:%M:%S")) if trip_time_prep_starts else None,
                'duration': calculate_duration(last_trip_date, trip_time_prep_starts) if last_trip_date and trip_time_prep_starts else None,
                'Description': 'BoatBrain started, waiting to start stage 1'
            },
            {
                'stage': 1,
                'start_time': format_time_12hr(trip_time_prep_starts.strftime("%H:%M:%S")) if trip_time_prep_starts else None,
                'end_time': format_time_12hr(trip_time_left_house.strftime("%H:%M:%S")) if trip_time_left_house else None,
                'duration': calculate_duration(trip_time_prep_starts, trip_time_left_house) if trip_time_prep_starts and trip_time_left_house else None,
                'Description': 'Preparing to leave house'
            },
            {
                'stage': 2,
                'start_time': format_time_12hr(trip_time_left_house.strftime("%H:%M:%S")) if trip_time_left_house else None,
                'end_time': format_time_12hr(trip_time_at_ramp.strftime("%H:%M:%S")) if trip_time_at_ramp else None,
                'duration': calculate_duration(trip_time_left_house, trip_time_at_ramp) if trip_time_left_house and trip_time_at_ramp else None,
                'Description': 'Leaving house to go to ramp'
            },
            {
                'stage': 3,
                'start_time': format_time_12hr(trip_time_at_ramp.strftime("%H:%M:%S")) if trip_time_at_ramp else None,
                'end_time': format_time_12hr(trip_time_in_water.strftime("%H:%M:%S")) if trip_time_in_water else None,
                'duration': calculate_duration(trip_time_at_ramp, trip_time_in_water) if trip_time_at_ramp and trip_time_in_water else None,
                'Description': 'At ramp, preparing to launch boat'
            },
            {
                'stage': 4,
                'start_time': format_time_12hr(trip_time_in_water.strftime("%H:%M:%S")) if trip_time_in_water else None,
                'end_time': format_time_12hr(trip_time_fishing_begins.strftime("%H:%M:%S")) if trip_time_fishing_begins else None,
                'duration': calculate_duration(trip_time_in_water, trip_time_fishing_begins) if trip_time_in_water and trip_time_fishing_begins else None,
                'Description': 'Boat in water, preparing to fish'
            },
            {
                'stage': 5,
                'start_time': format_time_12hr(trip_time_fishing_begins.strftime("%H:%M:%S")) if trip_time_fishing_begins else None,
                'end_time': format_time_12hr(trip_time_return_to_ramp.strftime("%H:%M:%S")) if trip_time_return_to_ramp else None,
                'duration': calculate_duration(trip_time_fishing_begins, trip_time_return_to_ramp) if trip_time_fishing_begins and trip_time_return_to_ramp else None,
                'Description': 'Fishing'
            },
            {
                'stage': 6,
                'start_time': format_time_12hr(trip_time_return_to_ramp.strftime("%H:%M:%S")) if trip_time_return_to_ramp else None,
                'end_time': format_time_12hr(trip_time_boat_on_trailer.strftime("%H:%M:%S")) if trip_time_boat_on_trailer else None,
                'duration': calculate_duration(trip_time_return_to_ramp, trip_time_boat_on_trailer) if trip_time_return_to_ramp and trip_time_boat_on_trailer else None,
                'Description': 'Returning to ramp'
            },
            {
                'stage': 7,
                'start_time': format_time_12hr(trip_time_boat_on_trailer.strftime("%H:%M:%S")) if trip_time_boat_on_trailer else None,
                'end_time': format_time_12hr(trip_time_prep_done_to_go_home.strftime("%H:%M:%S")) if trip_time_prep_done_to_go_home else None,
                'duration': calculate_duration(trip_time_boat_on_trailer, trip_time_prep_done_to_go_home) if trip_time_boat_on_trailer and trip_time_prep_done_to_go_home else None,
                'Description': 'Boat on trailer'
            },
            {
                'stage': 8,
                'start_time': format_time_12hr(trip_time_prep_done_to_go_home.strftime("%H:%M:%S")) if trip_time_prep_done_to_go_home else None,
                'end_time': format_time_12hr(trip_time_leave_ramp.strftime("%H:%M:%S")) if trip_time_leave_ramp else None,
                'duration': calculate_duration(trip_time_prep_done_to_go_home, trip_time_leave_ramp) if trip_time_prep_done_to_go_home and trip_time_leave_ramp else None,
                'Description': 'Preparing to go home'
            },
            {
                'stage': 9,
                'start_time': format_time_12hr(trip_time_leave_ramp.strftime("%H:%M:%S")) if trip_time_leave_ramp else None,
                'end_time': format_time_12hr(trip_time_return_home.strftime("%H:%M:%S")) if trip_time_return_home else None,
                'duration': calculate_duration(trip_time_leave_ramp, trip_time_return_home) if trip_time_leave_ramp and trip_time_return_home else None,
                'Description': 'Leaving ramp to go home'
            },
            {
                'stage': 10,
                'start_time': format_time_12hr(trip_time_return_home.strftime("%H:%M:%S")) if trip_time_return_home else None,
                'end_time': None,
                'duration': 0,
                'Description': 'Home, cleaning up from trip'
            }
        ]


        # Determine current stage based on which trip times have values
        for i, stage in enumerate(stages):
            if stage['start_time'] and stage['end_time']:
                current_stage = i + 1

        # Store the description for the current stage
        current_stage_description = stages[current_stage]['Description'] if current_stage < len(stages) else "Unknown stage"


        # Query all records from bb_onwater_log where trip_log_id matches last_trip_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM bb_onwater_log WHERE trip_log_id = %s", [last_trip_id])
            columns = [col[0] for col in cursor.description]  # Extract column names
            onwater_log_data = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert tuples to dictionaries

        # latitude = onwater_lat
        # longitude = onwater_lon

        # Create a Folium map centered at the first log entry's coordinates
        if onwater_log_data:
            first_entry = onwater_log_data[0]
            map_center = [float(first_entry['onwater_lat']), float(first_entry['onwater_lon'])]
            folium_map = folium.Map(location=map_center, zoom_start=12)

            # Collect all marker coordinates to adjust the map bounds
            marker_coordinates = []

            # Add red dot markers for each log entry
            for entry in onwater_log_data:
                marker_coordinates.append([float(entry['onwater_lat']), float(entry['onwater_lon'])])
                folium.CircleMarker(
                    location=[float(entry['onwater_lat']), float(entry['onwater_lon'])],
                    radius=2,  # Size of the dot
                    color='red',  # Outline color
                    fill=True,
                    fill_color='red',  # Fill color
                    fill_opacity=0.8,
                    popup=f"Timestamp: {entry['onwater_timestamp']}",
                ).add_to(folium_map)

            # Adjust the map to fit all markers
            folium_map.fit_bounds(marker_coordinates)

            # Convert the Folium map to HTML
            map_html = folium_map._repr_html_()
        else:
            map_html = None





    context = {
        "number_trips": number_trips,
        "last_trip_id": last_trip_id,
        "last_trip_date": last_trip_date,
        "stages": stages,
        "current_stage": current_stage,
        "current_stage_description": current_stage_description,
        "onwater_log_data": onwater_log_data,
        "map_html": map_html,
        "this_trip_id": this_trip_id
    }
    return render(request, "current_trip.html", context)

def calculate_duration(start_time, end_time):
    time_difference = abs(end_time - start_time)
    total_seconds = int(time_difference.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds:02}"

# Create your views here.
def home_page_view(request): # new
    return render(request, "home.html", {"timestamp": int(time.time())})

def about_page_view(request): # new
    return render(request, "about.html")



