import numpy as np
import matplotlib.pyplot as plt
from source.Sensor import Sensor
from source.helperFunctions import generate_active_list
from typing import List

VOLTAGE = 3.3 #Volts
ACTIVE_CURRENT = 15 #uA
SHUTDOWN_CURRENT = 0 #uA
MEASUREMENT_DURATION = 0.0005 #s


class TPIS1S1385(Sensor):

    def __init__ (self, time_step, duration, modes_tp, loop_rate = 60):
        self.time_step = time_step
        self.duration = duration
        self.active_time_params = generate_active_list(duration, modes_tp)
        self.modes_tp = modes_tp
        self.loop_rate = loop_rate
        self.time = np.arange(0,self.duration,self.time_step) #time at which to collect data
    
    def generate_valid_configs_tp(self):
        all_configs = [("TP_ON"), ("TP_OFF")]
        return all_configs
    def error_check(self):
        """
          Checks if the configurations contained within self.modes_tp are valid

          Parameters
          ----------
            None

          Returns
          -------
            error: True if a configuration is invalid, False otherwise
        """
        error = False
        all_configs = self.generate_valid_configs_tp()
        for param in self.modes_tp:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error

    def run_sim(self):
        """
          Checks if modes are valid before coputer the power and data usage of given configurations in modes_tp. Plots results.

          Parameters
          ----------
            None

          Returns
          -------
            Lists of power consumptions, data usages, and times. Empty lists if at least one mode is invalid
        """ 
        error = self.error_check()
        if error == False:
            power = self.get_all_modes_power()
            data = self.get_all_modes_data()
            self.plotData(power, data, self.time, self.active_time_params)
            return np.array(power), np.array(data), np.array(self.time)
        return [], [], []

    def get_mode_power(self, mode, sampling_rate):
        """
          This function calculates power when sensor is active

          Parameters
          ----------
            mode: String representing mode of TPIS1S1385 sensor

          Returns
          -------
            A vector of when power is used. Units are in mW.
        """ 
        self.mode = mode
        TP_power_microamps = 0
        power_used = 0
        voltage = VOLTAGE
        if(mode == "TP_ON"):
            if MEASUREMENT_DURATION < sampling_rate:
              TP_power_microamps = ACTIVE_CURRENT 
              power_used = ((TP_power_microamps * voltage / 1000))/sampling_rate
            else:
                print('Your choice of sampling rate exceeded the speed of the TPIS1S1385 sensor.')
        elif(mode == "TP_OFF"):
            if MEASUREMENT_DURATION < sampling_rate:
              TP_power_microamps = SHUTDOWN_CURRENT
              power_used = ((TP_power_microamps * voltage / 1000))/sampling_rate
            else:
                print('Your choice of sampling rate exceeded the speed of the TPIS1S1385 sensor.')
        else:
            print("Invalid mode entered.")
            return -1
        return power_used
    def get_bytes_per_second(self, mode, sampling_rate):
        """
          This function calculates the data being collected and how much

          Parameters
          ----------
            mode: String representing mode of TPIS1S1385 sensor

          Returns
          -------
            The measure rate and how much data is being collected in Bytes
        """
        measure_rate = 0 #how fast measurements are written to TP measurement registers, in Hz.
        if(sampling_rate < MEASUREMENT_DURATION):
            sampling_rate = MEASUREMENT_DURATION
        measure_rate = sampling_rate
        if(mode == "TP_ON"):
            return 6/measure_rate
        else:
            return 0 
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_tp

          Parameters
          ----------
            None

          Returns
          -------
            power_arr: list of all computed power consumptions
        """    
        length = len(self.time)
        power_arr = [0] * length # creating corresponding power array to time intervals, default values

        for times in self.active_time_params: # check if the given start and end time is a valid value in the time array and round to nearest value 
            start_index = int(times[0] / self.time_step) # getting index of the closest value to active times 
            end_index = int(times[1] / self.time_step)

            if start_index < 0 or end_index > len(self.time): # not valid time
                print("Error. Index not valid.")
                return
            params = times[2]
            power = 0
            power = self.get_mode_power(params,times[3])

            for i in range(start_index, end_index):
                power_arr[i] = power

        return power_arr
    def get_all_modes_data(self):
        """
          Computes the data usage of all modes in modes_tp

          Parameters
          ----------
            None

          Returns
          -------
            data_arr: list of all computed data usages
        """    
        length = len(self.time)
        data_arr = [0] * length 
        data_accumulated = 0
        
        for times in self.active_time_params: # for each active period
            start_index = int(times[0] / self.time_step) 
            end_index = int(times[1] / self.time_step)
            params = times[2]
            data_per_second = self.get_bytes_per_second(params,times[3])

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
                
        return data_arr