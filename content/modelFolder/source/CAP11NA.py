from source.Sensor import Sensor
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from source.helperFunctions import generate_active_list
import math
#class for the capacative sensor. wont have too much functionality since 
#we only know of its data usage. However, the basis for a power module will be provided when that is known
class CAP11NA(Sensor):
    def __init__(self, time_step, duration, modelist, loop_rate):
        """
        Initilize object class
            arguments = [Time_step, duration_of_whole, modal, loop_rate]
            
        """
        self.time_step = time_step
        self.duration = duration
        self.active_time_params = generate_active_list(duration, modelist)
        self.loop_rate = loop_rate
        self.time = np.arange(0,self.duration,self.time_step)
        self.modelist = modelist
        
    def error_check(self,modelist):
        error = False
        for item in modelist:
            if item[0] != "CAP_ON" and item[0] != "CAP_OFF":
                print("Error. Invalid configuration {}. Valid m to choose from: [\"CAP_ON\",\"CAP_OFF\"]")
                error = True
            else:
                error = False
        return error
    
    def run_sim(self) -> int:
        """
        Returns time, power, data vectors and plot.

        args:
            none
        returns:
            time, power, data. plots and all vectors used in plotting
        """
        self.error_check(self.modelist)
        time_index = []
        Power = []
        Data = []
        Power_sec = []
        Data_sec = []
        time = 0
        i=0
        k = int(self.duration / self.time_step)
        time_index.append(0)
        #initialized parameters
        
        for item in self.modelist: #Create vectors for each configuration that say how much power and data they use
            i +=1
            time += item[1]* (1/self.time_step)
            time_index.append(time)
            power_sec = (self.get_Power_per_sec(item[0],item[2])*np.ones(int(time_index[i]-time_index[i-1])))
            data_sec = (self.get_Bytes_per_sec(item[0],item[2])*np.ones(int(time_index[i]-time_index[i-1])))
            Power_sec.append(power_sec)
            Data_sec.append(data_sec)
            
        Power_per_run = np.concatenate(Power_sec)
        Data_per_run = np.concatenate(Data_sec)
        runs = math.ceil(self.duration /(time_index[-1]*self.time_step))
        
        for ii in np.arange(0,runs,1):#Create vectors that copy the run power and data for the entire timeframe
            Power.append(Power_per_run)
            Data.append(Data_per_run)
            
        Power = (np.concatenate(Power))
        Data = (np.concatenate(Data))
        
        Power_Vec = Power[0:k+1]
        Time_Vec = np.arange(0,self.duration,self.time_step)
        Data_Vec = np.cumsum(Data[0:k+1])

        self.plotData(Power_Vec, Data_Vec, Time_Vec, self.active_time_params)
        return Power_Vec,Data_Vec,Time_Vec
    
    def get_Power_per_sec(self, mode, sampling_rate):
        """
        Returns estimated power usage per second

        args:
            mode [State, time, sample rate, loop rate]
        returns:
            An integer representation of mW.
        """
        
        cap_estimated_power_usage = 1 # mW
        cap_estimated_sample_time = 0.005 # s
        # These values are set up the way they were calculated in a previous version, and when its off this will return 0 usage. These values are likely to be modified in the future
        if mode == "CAP_ON":
            return cap_estimated_power_usage * (1 - (1/sampling_rate * cap_estimated_sample_time))
        elif mode == "CAP_OFF":
            return 0
        else:
            print("Error. Invalid configuration.")
            return -1
        
    def get_Bytes_per_sec(self, mode, sampling_rate):
        """
        Returns number of bytes per second based on loop rate.

        args:
            mode [State, time, sample rate, loop rate]
        returns:
            An integer representation of bytes per second.
        """
        cap_bytes_per_second = 6
        # These values are set up the way they were calculated in a previous version, and when its off this will return 0 usage. These values are likely to be modified in the future
            
        if mode == "CAP_ON":
            bit_sec = (cap_bytes_per_second) * (1/sampling_rate)
            return bit_sec
        elif mode == "CAP_OFF":
            return 0
        else:
            print("Error. Invalid configuration.")
            return -1