"""Class used to simulate the power produced by a SM141K solar panel

    Slightly modified by Luke Roberson from work by James Bohn and John Aldrete.
    If this class is being used outside of a jupyter notebook, plt.show() is
    needed at the end of the script in order to show plots

    Usage Example:
    solar_panel_model = SM141K(start_time_hrs=0, duration_hrs=709, time_step_seconds=30, latitude=45)
    solar_panel_model.Available() #plots power produced throughout a lunar day
    plt.show() #needed if outside of jupyter notebook
"""
import numpy as np
from matplotlib import pyplot as plt
import sys as sys

class SM111K():
    def __init__(self, start_time_hrs, duration_hrs, time_step_seconds, latitude):

        self.start_time         = start_time_hrs
        self.duration           = duration_hrs
        self.end_time           = start_time_hrs+duration_hrs
        self.time_step          = time_step_seconds/3600
        self.latitude           = latitude
        self.lunar_day_length   = 656.7167 #hrs. Time from solar noon to solar noon on the moon
        self.lunar_dawn         = (self.lunar_day_length/4)
        self.lunar_dusk         = (self.lunar_day_length-((self.lunar_day_length/4)))

    # Assumptions:
    # Solar output is constant - real variance is ~.1% over 11 year cycles
    # Variance in moons distance to sun is negligable (constant 1 AU) - real daily variance is ~.5%, yearly ~3.5%
    # Solar panel power efficiency is not dependent on angle of incidence - not mentioned in datasheet
    # No effect on irradiance by moons atmosphere - atmosphere is practically non existant
    # No irradiance on the dark side - if there was any it would be EXTREMELY small

    def power(self, psi:float ) -> float:
        """
        Returns power produced by solar panel

        args:
            psi (float): angle [rad] of incidience of solar panel to Sun
        returns:
            power (float): power in milliwatts of power produced by solar panels
        """
        SOLAR_CONSTANT = 1360 # W/m^2
        SURFACE_AREA = .00072 #m^2
        CELL_EFFICIENCY = 0.25
        MAX_POWER_OUT = 146.9 #mW

        power = np.cos(psi) * SOLAR_CONSTANT * SURFACE_AREA * CELL_EFFICIENCY * 1000

        if power>MAX_POWER_OUT:
            power=MAX_POWER_OUT
            
        if power < 0:
            power = 0

        return power

    # Analytical Equation for the Dayside Temperature (from Hurley et al, 2015)
    def temp(self, psi: float) -> float:
        """
        returns temp of lunar surface given incidence angle

        args:
            psi (float): incidence angle with respect to sun
        returns:
            temp (float): temp in Kelvin of lunar surface
        """
        temp = (262*(np.sqrt(np.cos(psi)))) + 130
        return

    def psi(self, lat, time):
        """
        Returns the angle of the lunar surface . Solar
        panel facing directly toward the sun corresponds to psi = 0 rad

        args:
            lat (float): latitude [degrees] on Lunar surface from (-90,90)
            time (float): time [hrs] since Lunar midnight
        returns:
            psi (float): angle [rad] of Lunar surface with respect to sun.
        """

        # Bounds check latitude
        if (abs(lat)>90):
            sys.exit('Error. Latitude should be less than 90 degrees!')
        else:
            pass

        # Bounds check time
        if ((time < self.lunar_dawn) or (time > self.lunar_dusk)):
            sys.exit(f"Error. Time should be between sunrise({self.lunar_dawn} hrs) and sunset({self.lunar_dusk} hrs)  for the dayside!")
        else:
            pass

        time_angle_midnight = ((time/self.lunar_day_length)*(2*np.pi))%(2*np.pi)

        time_angle_noon = np.pi - time_angle_midnight

        # Define co-ordinate system
        # +z - out of the page (from the moon to the sun)
        # +y - from right to left in the page
        # +x - from bottom to top, in the page

        # Initial position vector - (x,y,z) triplet: [0,0,1]

        r = np.mat(np.array([[0],[0],[1]]))

        # 1. Latitudinal rotation

        # Given our co-ordinate system, latitudinal rotation is a rotation about the y-axis
        # Rotation matrix for rotation about the y-axis is:
        # [cos(theta), 0, sin(theta); 0, 1, 0; -sin(theta), 0, cos(theta)]

        lat_rad = (lat*np.pi/180)

        t11 = np.cos(lat_rad)
        t13 = np.sin(lat_rad)
        t31 = -t13
        t33 = t11

        R_y = np.mat(np.array([[t11,0,t13],[0,1,0],[t31,0,t33]]))

        r1 = R_y*r

        # 2. Longitudinal rotation

        # Rotate about the +x axis by the angle from noon.
        # R_x = [1, 0, 0; 0, cos(theta), -sin(theta); 0, sin(theta), cos(theta)]

        C = np.cos(time_angle_noon)
        S = np.sin(time_angle_noon)

        R_x = np.mat(np.array([[1,0,0],[0,C,-S],[0,S,C]]))
        r2 = R_x*r1

        # 3. Now taking the dot product, dividing by the square of the magnitudes of the vectors, and then taking cosine inverse.
        # Since we used unit vectors, we're basically only taking the cosine inverse.

        dot_product = r[0,0]*r2[0,0] + r[1,0]*r2[1,0] + r[2,0]*r2[2,0]
        psi = np.arccos(dot_product)

        return psi

    def model(self, start_time=None, end_time=None, time_step=None, latitude=None):
        """
        Run a simulation of the solar panel power production starting at
        start_time and going until end_time. Times are specified in hours since
        lunar midnight. If paramters are not specified, class variable times are
        used (specified during initialization).

        args:
            start_time (float): hours since lunar midnight of start time of model
            end_time (float): hours of end time
            time_step (float): seconds between simulation points
            latitude (float): latitude on Lunar surface in degrees from (-90,90)
        returns:
            times (list[float]): vector of times at which simulation was ran
            powers (list[float]): vector of power produced corresponding to time
                in times
        """

        if start_time==None: start_time = self.start_time
        if end_time==None: end_time = self.end_time
        if time_step==None: time_step = self.time_step
        if latitude==None: latitude = self.latitude

        times = np.arange(start_time, end_time, time_step)
        powers = np.zeros(len(times))

        for i in range(len(times)):
            time = times[i]
            time %= self.lunar_day_length
            if time >= self.lunar_dawn and time <= self.lunar_dusk:
                angle = self.psi(latitude, time)
                powers[i] = self.power(angle)


        return times, powers

    def plot_power_available(self):
        """
        runs model and plots it according to times specified in __init__

        args:
            None
        returns:
            None
        """
        times,output = self.model()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(times, output, color="steelblue")
        ax.set_title("Power Available", fontsize=20)
        ax.set_xlabel("Time (hours)", fontsize=16)
        ax.set_ylabel("Power (mW)", fontsize=16)

        ax.grid(True, alpha=0.25)


    def plot_power_and_times_possible(self,max_power):
        """
        Plots power available and times at which the solar panel produces power
        specified by max_power or greater

        args:
            max_power (float): max power consumed
        returns:
            1x2 list of times that the lunasat can be run
        """
        time,power = self.model()
        multiplier = int(np.ceil(len(power) / len(max_power)))
        if(multiplier==0):
            multiplier=1
        max_power = np.tile(max_power,multiplier)
        max_power = max_power[:len(power)]
        possiblePower = np.where(power>max_power,power,0)

        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(time, power, color="steelblue")
        ax.fill_between(time, possiblePower, step="pre", alpha=0.4)
        ax.set_title("Power Available", fontsize=20)
        ax.set_xlabel("Time Since Lunar Midnight (Earth hours)", fontsize=16)
        ax.set_ylabel("Power (mW)", fontsize=16)

        ax.grid(True, alpha=0.25)

        timePossible = np.where(power>max_power,time,None)
        timePossible = timePossible[timePossible!=None]
        if(len(timePossible)==0):
            print("ERROR! At least one of your configurations exceeds the maximum available power.")
            return "ERROR"
        print("Configurations possible in the interval:")
        print([min(timePossible),max(timePossible)])
        return "Configurations meet power requirements"
