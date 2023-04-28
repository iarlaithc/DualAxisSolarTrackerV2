import numpy as np
import matplotlib.pyplot as plt
import ephem
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import datetime
import tkinter as tk

#model class
class SolarTracker:
	def __init__(self, panel_length, panel_width, panel_tilt, latitude, longitude):
		self.panel_length = panel_length
		self.panel_width = panel_width
		self.panel_tilt = panel_tilt
		self.tilt_angle = None
		self.azimuth_angle = None
		self.times = []
		self.solar_energy_output = []
		
		#error handling and input validation
		self.set_latitude(latitude)
		self.set_longitude(longitude)

	def set_latitude(self, latitude):
		try:
			self.latitude = float(latitude)
		except ValueError:
			raise ValueError("Latitude must be a float value")
		if self.latitude < -90 or self.latitude > 90:
			raise ValueError("Latitude must be between -90 and 90 degrees")

	def set_longitude(self, longitude):
		try:
			self.longitude = float(longitude)
		except ValueError:
			raise ValueError("Longitude must be a float value")
		if self.longitude < -180 or self.longitude > 180:
			raise ValueError("Longitude must be between -180 and 180 degrees")


	def calculate_solar_energy(self, time):
		observer = ephem.Observer()
		observer.lat = self.latitude
		observer.lon = self.longitude
		observer.date = time

		sun = ephem.Sun(observer)
		sun.compute(observer)

		sun_azimuth = sun.az
		sun_elevation = sun.alt

		# Calculate the angle between the solar panel normal and the direction of the sun
		incidence_angle = np.arccos(np.sin(self.panel_tilt) * np.sin(sun_elevation) + np.cos(self.panel_tilt) * np.cos(sun_elevation) * np.cos(sun_azimuth - self.azimuth_angle))

		# Calculate the fraction of solar radiation that is absorbed by the solar panel
		panel_efficiency = 0.15  # Assume an efficiency of 15%
		absorbed_fraction = np.cos(incidence_angle) ** 3 * panel_efficiency

		# Calculate the amount of solar energy that hits the solar panel
		solar_constant = 1367  # W/m^2
		solar_energy = absorbed_fraction * solar_constant * np.cos(sun_elevation)

		return solar_energy

	def simulate(self, start_time, end_time, time_step):
		time = start_time
		while time <= end_time:
			# Calculate the optimal tilt and azimuth angles for the current time and position
			observer = ephem.Observer()
			observer.lat = self.latitude
			observer.lon = self.longitude
			observer.date = time

			sun = ephem.Sun(observer)
			sun.compute(observer)

			sun_azimuth = sun.az
			sun_elevation = sun.alt

			# Calculate the optimal tilt angle
			self.tilt_angle = np.arcsin(np.cos(sun_elevation) * np.cos(sun_azimuth - np.pi) / np.cos(np.pi / 2 - self.latitude))
			# Calculate the optimal azimuth angle
			self.azimuth_angle = np.pi + np.arctan2(-np.sin(sun_azimuth), -np.cos(sun_azimuth) * np.sin(self.latitude) + np.tan(sun_elevation) * np.cos(self.latitude))
			# Calculate the solar energy output for the current time and position
			solar_energy = self.calculate_solar_energy(time)
			# Add the solar energy output and time to the respective lists
			self.times.append(time)
			self.solar_energy_output.append(solar_energy)
			# Increment the time by the time step
			time += time_step

	def plot_basic(self):
		plt.plot(self.times, self.solar_energy_output)
		plt.xlabel('Time')
		plt.ylabel('Solar Energy Output (W/m^2)')
		plt.show()

	def plot_average(self):
		# Calculate the number of time steps in 24 hours
		steps_in_day = 24 * 60
		# Calculate the number of days in the simulation
		days_in_simulation = len(self.times) / steps_in_day
		# Calculate the average solar energy output for each day in the simulation
		avg_energy_output = []
		for i in range(int(days_in_simulation)):
				start_index = i * steps_in_day
				end_index = start_index + steps_in_day
				avg_energy_output.append(np.mean(self.solar_energy_output[start_index:end_index]))

		# Plot the average solar energy output over the entire simulation
		plt.plot(range(int(days_in_simulation)), avg_energy_output)
		plt.xlabel('Days')
		plt.ylabel('Average Solar Energy Output (W/m^2)')
		plt.show()

##gui class
class SolarTrackerGUI:
	def __init__(self, master):
		self.master = master
		master.title("Solar Tracker GUI")
		self.all_entries_valid = tk.BooleanVar(value=True)
		
		# Create labels and entry widgets for panel geometry and location
		tk.Label(master, text="Panel length (m)").grid(row=0)
		tk.Label(master, text="Panel width (m)").grid(row=1)
		tk.Label(master, text="Panel tilt angle (degrees)").grid(row=2)
		tk.Label(master, text="Latitude").grid(row=3)
		tk.Label(master, text="Longitude").grid(row=4)
		tk.Label(master, text="Duration").grid(row=5)

		self.panel_length_entry = tk.Entry(master)
		self.panel_width_entry = tk.Entry(master)
		self.panel_tilt_entry = tk.Entry(master)
		self.latitude_entry = tk.Entry(master)
		self.longitude_entry = tk.Entry(master)
		self.duration_entry = tk.Entry(master)

		self.panel_length_entry.grid(row=0, column=1)
		self.panel_width_entry.grid(row=1, column=1)
		self.panel_tilt_entry.grid(row=2, column=1)
		self.latitude_entry.grid(row=3, column=1)
		self.longitude_entry.grid(row=4, column=1)
		self.duration_entry.grid(row=5,column=1)
		# Create button widget to start the simulation
		tk.Button(master, text="Start simulation", command=self.start_simulation).grid(row=6)
		# Create a matplotlib figure and axes for the solar energy output graph
		plot_frame = tk.Frame(master)
		plot_frame.grid(row=0,column=2,rowspan=20,columnspan=6)
		self.fig, self.ax = plt.subplots(figsize=(8.5,7))
		self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
		self.canvas.get_tk_widget().pack(padx=10,pady=10)

	def start_simulation(self):
		# Retrieve the panel geometry and location from the entry widgets
		panel_length = float(self.panel_length_entry.get())
		panel_width = float(self.panel_width_entry.get())
		panel_tilt = float(self.panel_tilt_entry.get()) * np.pi / 180
		latitude = self.latitude_entry.get()
		longitude = self.longitude_entry.get()
		simulation_duration = float(self.duration_entry.get())

		# Instantiate a solar tracker object with the specified panel geometry and location
		solar_tracker = SolarTracker(panel_length, panel_width, panel_tilt, latitude, longitude)
		# Define the current date and time
		current_time = datetime.datetime.now()		
		start_time = current_time
		end_time = current_time + datetime.timedelta(days=simulation_duration)
		time_step = datetime.timedelta(minutes=1)
		solar_tracker.simulate(start_time, end_time, time_step)
		# Clear the axes and plot the solar energy output over time
		self.ax.clear()
		self.ax.plot(solar_tracker.times, solar_tracker.solar_energy_output)
		self.ax.set_xlabel('Time')
		self.ax.set_ylabel('Solar Energy Output (W/m^2)')
		self.ax.tick_params(axis="x",rotation=90 )
		self.canvas.draw()
