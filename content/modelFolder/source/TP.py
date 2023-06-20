import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from source.Sensor import Sensor
from typing import List

class TP(Sensor):

    def __init__ (self, time_step, duration, loop_rate=60):

        """
        mode tells the type of mode the sensor is in. Choices for TP are "TP_only"
        time_step would define at what intervals (and therefore time) the model will be running
        data at 0,1,2,3... seconds assuming start time of 0 seconds.
        """

        self.time_step = time_step
        self.duration = duration

        self.loop_rate = loop_rate
        """
        how fast the arduino loop will run. This value is kind of up in the air, but we predict that it may have an
        affect on how fast we can read from the sensors depending on how much code is run in the loop, in Hz.
        """
        self.time = np.arange(0,self.duration,self.time_step)
    

    def runSim(self, active_times: List[tuple]) -> int:
        """
        This function takes in the active times and ensures the power and data vectors to be graphed with the active times
        Args: Active times - A list of tuples that would define the time at which the sensor was running
        Returns: The vectors for the power usage, data usage and plots this data with respect to the active times
        """
        self.time = np.arange(0,self.duration,self.time_step)
        """time at which to collect data"""
        try:
            power, data = self.getVectors(active_times)
            self.plotData(power, data, self.time, active_times)
            return power, data, self.time
        except TypeError as e:
            print("A type error occurred. Your active times array may exceed the duration set in TP object.", e)
            return -1

    def getModePower(self, mode):
        """
        This function calculates power when sensor is active
        Args: We pass in the mode we want the sensor to run at
        Returns: A vector of when power is used. Units are in mW.
        """
        self.mode = mode
        power_used = 0
        TP_power_microamps = 0
        voltage = 3.3
        if(mode == "on"):
            TP_power_microamps = 15
            power_used = (TP_power_microamps * voltage) / 1000 
        elif(mode == "TP_off"):
            TP_power_microamps = 0
            power_used = (TP_power_microamps * voltage) / 1000 
        else:
            print("Invalid mode {} entered.".format(mode, ))
            return -1
        return power_used

    def getVectors(self, active_times: List[tuple]) -> tuple:
        """
        This function returns the power vector and the data vectors to send to runSim so it can be graphed
        Args: active times as a list of tuples. First two elements are start and end times
        Returns: The power array and the data array
        """
        length = len(self.time)
        powerarr = [0] * length 
        """ creating corresponding power array to time intervals, default values """
        dataarr = [0] * length
        """ check if the given start and end time is a valid value in the time array and round to nearest value """
        for times in active_times:
            start_index = int(times[0] / self.time_step) 
            """getting index of the closest value to active times """
            end_index = int(times[1] / self.time_step)
            if (start_index < 0): 
                print("Error. Starting index not valid.")
                return -1
            elif(end_index > len(self.time)):
                end_index = len(self.time)
                print("Warning. Active times is longer than the duration")
            
            
            curPower = self.getModePower(times[2])
            curData = self.getBytesPerSecond(times[2])
            for i in range(start_index, length):
                powerarr[i] = curPower
                if i == 0:
                    dataarr[i] = curData
                else:
                    dataarr[i] = dataarr[i-1] + curData
            
        return powerarr, dataarr

    def getBytesPerSecond(self, mode):
        """
        This function calculates the data being collected and how much
        Args: The mode the sensor is running on
        Result: We are returning the measure rate and how much data is being collected in Bytes
        """
        measure_rate = 0
        self.getModePower(mode)
        """ calculate sample rate. """
        sample_rate = 0.64 
        """
        how fast measurements are written to
        TP measurement registers, in Hz.
        """
        measure_rate = (self.loop_rate, sample_rate)[self.loop_rate > sample_rate]
        if(mode == "on"):
            return 6*measure_rate
        else:
            return 0*measure_rate
