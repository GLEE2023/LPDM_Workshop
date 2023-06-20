import numpy as np
import matplotlib.pyplot as plt
import random 
from source.helperFunctions import generate_active_list
from source.Sensor import Sensor

VOLTAGE = None #Volts
SHUTDOWN_CURRENT = None 
ACTIVE_CURRENT = None

class SX1272(Sensor):
    def __init__(self, time_step, duration, modes_SX1, loop_rate): 
        self.time_step = time_step
        self.duration = duration
        self.time = np.arange(0, duration, time_step) #time at which to collect data
        self.active_time_params = generate_active_list(duration, modes_SX1)
        self.loop_rate = loop_rate
        self.modes_SX1 = modes_SX1
        
    def generate_valid_configs_tmp(self):
        """
          Creates a list of all valid SX1272 configurations.

          Parameters
          ----------
            None

          Returns
          -------
            all_configs: list of tuples representing valid configurations
        """
        all_configs = None
        
        modes = ["SLEEP", "STANDBY", "TX", "RXCONTINUOUS", "RXSINGLE", "IDLE", "FSTX", "FSRX", "CAD"]
        
        
        return all_configs
    
    def error_check(self):
        """
          Checks if the configurations contained within self.modes_SX1 are valid

          Parameters
          ----------
            None

          Returns
          -------
            error: True if a configuration is invalid, False otherwise
        """
        error = None
        
        # Code here
        
        return error
    
    def compute_power(self, mode, frequency, output_power, bandwidth, spreading_factor, coding_rate, transmission_rate, reception_rate):
        """
          Computes power consumption of a given configuration.

          Parameters
          ----------

          Returns
          -------
            power: Float representing power in mW
        """    
        power = None
        
        modes = ["SLEEP", "STANDBY", "TX", "RXCONTINUOUS", "RXSINGLE", "IDLE", "FSTX", "FSRX", "CAD"]
        
        if mode == modes[0]:
            pass
        elif mode == modes[1]:
            pass
        elif mode == modes[2]:
            pass
        elif mode == modes[3]:
            pass
        elif mode == modes[4]:
            pass
        elif mode == modes[5]:
            pass
        elif mode == modes[6]:
            pass
        elif mode == modes[7]:
            pass
        elif mode == modes[8]:
            pass
        
        return power
    
    def compute_data(self, mode, frequency, output_power, bandwidth, spreading_factor, coding_rate, transmission_rate, reception_rate, packet_size = 256):
        """
          Computes data usage of a given configuration.

          Parameters
          ----------
            

          Returns
          -------
            data: number of bytes used in 1 second
        """ 
        data = 0
        
        return data
    
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_SX1

          Parameters
          ----------
            None

          Returns
          -------
            power_arr: list of all computed power consumptions
        """    
        power_arr = None
        
        # Code here
        
        return power_arr
    
    def get_all_modes_data(self):
        """
          Computes the data usage of all modes in modes_SX1

          Parameters
          ----------
            None

          Returns
          -------
            data_arr: list of all computed data usages
        """
        data_arr = None
        
        data_arr = [0] * length
        
        return data_arr
    
    def run_sim(self):
        """
          Checks if modes are valid before coputer the power and data usage of given configurations in modes_SX1. Plots results.

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