from django.db import models


class BBTripLog(models.Model):
    TRIP_TYPES = [
        ('REAL', 'Real Trip'),
        ('TEST', 'Test Data'),
    ]

    trip_id = models.AutoField(primary_key=True)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPES, default='REAL', db_index=True,null=True, blank=True)
    trip_timestamp = models.DateTimeField(null=True, blank=True, db_index=True) #### stage 0 begins
    trip_date = models.DateField(null=True, blank=True, db_index=True)
    
    trip_start_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    trip_start_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    trip_lake = models.CharField(max_length=100, null=True, blank=True)

    weather_forecast_description = models.CharField(max_length=255, null=True, blank=True)
    weather_forecast_temperature = models.FloatField(null=True, blank=True)
    weather_forecast_pressure = models.FloatField(null=True, blank=True)
    weather_measured_home_temperature = models.FloatField(null=True, blank=True)
    weather_measured_home_pressure = models.FloatField(null=True, blank=True)

    trip_time_prep_starts = models.DateTimeField(null=True, blank=True) #### stage 1 begins
    trip_time_left_house = models.DateTimeField(null=True, blank=True) #### stage 2 begins
    trip_time_at_ramp = models.DateTimeField(null=True, blank=True) #### stage 3 begins
    trip_coordinates_ramp_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    trip_coordinates_ramp_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    weather_measured_ramp_temperature = models.FloatField(null=True, blank=True)
    weather_measured_ramp_pressure = models.FloatField(null=True, blank=True)

    trip_time_in_water = models.DateTimeField(null=True, blank=True) #### stage 4 begins
    trip_time_fishing_begins = models.DateTimeField(null=True, blank=True) #### stage 5 begins
    trip_time_return_to_ramp = models.DateTimeField(null=True, blank=True) 
    trip_time_boat_on_trailer = models.DateTimeField(null=True, blank=True) #### stage 7 begins
    trip_time_leave_ramp = models.DateTimeField(null=True, blank=True) #### stage 8 begins
    trip_time_return_home = models.DateTimeField(null=True, blank=True) #### stage 9 begins
    trip_time_cleanup_at_home_complete = models.DateTimeField(null=True, blank=True) #### stage 10 begins
    trip_time_pull_away_ramp = models.DateTimeField(null=True, blank=True) #### not sure if this is used
    trip_time_prep_done_to_go_home = models.DateTimeField(null=True, blank=True) #### stage 6 begins

    class Meta:
        db_table = 'bb_trip_log'  # Custom table name
        ordering = ['trip_id']  # 🔹 Ensures ascending order by trip_id

    def __str__(self):
        return f"Trip {self.trip_id} on {self.trip_date}"
    

class BBOnWaterLog(models.Model):
    onwater_log_id = models.AutoField(primary_key=True)
    trip_log = models.ForeignKey('BBTripLog', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    onwater_timestamp = models.DateTimeField(null=True, blank=True, db_index=True)
    onwater_date = models.DateField(null=True, blank=True, db_index=True)
    
    onwater_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    onwater_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    onwater_event_entry = models.TextField(blank=True, null=True)
    
    onwater_batteryone_voltage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    onwater_batterytwo_voltage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    onwater_batterythree_voltage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    onwater_air_temp = models.FloatField(null=True, blank=True)
    onwater_air_press = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'bb_onwater_log'
        indexes = [
            models.Index(fields=['onwater_date']),
            models.Index(fields=['onwater_timestamp']),
        ]

    def __str__(self):
        return f"On-Water Log {self.onwater_log_id} - {self.onwater_date}"
    

    class ApplicationLog(models.Model):
        timestamp = models.DateTimeField(auto_now_add=True)  # Log time
        log_level = models.CharField(max_length=10, choices=[
            ('INFO', 'Info'),
            ('WARNING', 'Warning'),
            ('ERROR', 'Error'),
            ('DEBUG', 'Debug')
        ])
        source_file = models.CharField(max_length=255, blank=True, null=True)  # File where log originated
        stage= models.CharField(max_length=255, blank=True, null=True)
        function_name = models.CharField(max_length=255, blank=True, null=True)  # Function where log occurred
        log_message = models.TextField()  # Error or log message

        class Meta:
            db_table = 'application_log'  # PostgreSQL table name
            ordering = ['-timestamp']  # Show latest logs first

        def __str__(self):
            return f"[{self.timestamp}] {self.log_level}: {self.log_message[:50]}"

