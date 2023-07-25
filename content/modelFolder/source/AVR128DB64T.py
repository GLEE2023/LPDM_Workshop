from source.Sensor import Sensor
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from source.helperFunctions import generate_active_list

VOLTAGE = 3.3 #V

class AVR128DB64T(Sensor):

    def __init__(self, duration, time_step, modes_MCR, loop_rate):
        self.duration = duration
        self.time_step = time_step
        self.modes_MCR = modes_MCR
        self.loop_rate = loop_rate
        self.time = np.arange(0, duration, time_step)
        self.active_time_params = generate_active_list(duration, modes_MCR)

    def generate_valid_configs_mcr(self):
        """
          Creates a list of all valid microcontroller configurations.

          Parameters
          ----------
            None

          Returns
          -------
            all_configs: list of tuples representing valid configurations
        """
        freq_options = [1, 2, 3, 4, 8, 12, 16, 20, 24]
        sd_options = [1, 2, 4, 8, 16, 32, 64, 6, 10, 12, 24, 48]
        modes = ["ACTIVE", "IDLE", "STANDBY", "POWER_DOWN"]
        clocks = ["OSCHF", "OSC32K", "XOSC32K", "EXTCLK"]
        lp = ["OFF","ON"]
        
        all_configs = []
        configs = [(mode, "OSCHF", freq, "OFF", sd) for mode in modes for freq in freq_options for sd in sd_options ]
        all_configs += configs
        configs = [(mode, "OSC32K", 32.768, "OFF", sd) for mode in modes for sd in sd_options ]
        all_configs += configs
        configs = [(mode, "XOSC32K", 32.768, l, sd) for mode in modes for l in lp for sd in sd_options ]
        all_configs += configs
        configs = [(mode, "EXTCLK", freq, "OFF", sd) for mode in modes for freq in freq_options for sd in sd_options ]
        all_configs += configs
        
        return all_configs
    
    def run_sim(self):
        try:
            self.error_check()
            power = self.get_all_modes_power()
            data = np.zeros(len(power))
            return power, data, self.time 
        except TypeError as e:
            print("A type error occurred. Your active times array may exceed the set duration.", e)
            return -1
    @staticmethod
    
    def compute_power(self, mode, clock, freq, lp, sd):
        power_used = 0
        freq_options = [1, 2, 3, 4, 8, 12, 16, 20, 24]
        sd_options = [1, 2, 4, 8, 16, 32, 64, 6, 10, 12, 24, 48]
        all_freq_options = [ x / y for x in freq_options for y in sd_options]
        all_freq_options = np.unique(all_freq_options)
        
        if mode == "ACTIVE":
            if clock == "OSCHF":
                a = np.where(all_freq_options == 4)[0]
                b = np.where(all_freq_options == 24)[0]
                rng_high = np.linspace(1.0,4.1,int(b-a+1))
                rng_low = np.linspace(0.1,1.0,int(a+1))
                rng_low = rng_low[:-1]
                rng = np.append(rng_low, rng_high)
                power_used = (rng[np.where(all_freq_options==freq/sd)])[0] * (VOLTAGE * 1000)
                
            elif clock == "OSC32K":
                power_used = (7.0 / 1000) * (VOLTAGE * 1000)
                
            elif clock == "XOSC32K":
                if lp=="ON":
                    power_used = (7.5 / 1000) * (VOLTAGE * 1000)
                    
                else:
                    power_used = (9.0 / 1000) * (VOLTAGE * 1000)
                    
            elif clock == "EXTCLK":
                rng = np.linspace(0.1,3.8,len(all_freq_options))
                power_used = (((rng[np.where(all_freq_options==freq/sd)])[0])) * (VOLTAGE * 1000)
                
        elif mode == "IDLE":
            if clock == "OSCHF":
                a = np.where(all_freq_options == 4)[0]
                b = np.where(all_freq_options == 24)[0]
                rng_high = np.linspace(0.58,1.9,int(b-a+1))
                rng_low = np.linspace(0.1,0.58,int(a+1))
                rng_low = rng_low[:-1]
                rng = np.append(rng_low, rng_high)
                power_used = (rng[np.where(all_freq_options==freq/sd)])[0] * (VOLTAGE * 1000)
                
            elif clock == "OSC32K":
                power_used = (4.0 / 1000) * (VOLTAGE * 1000)
                
            elif clock == "XOSC32K":
                if lp=="ON":
                    power_used = (6.0 / 1000) * (VOLTAGE * 1000)
                    
                else:
                    power_used = (7.5 / 1000) * (VOLTAGE * 1000)
                    
            elif clock == "EXTCLK":
                rng = np.linspace(0.1,1.7,len(all_freq_options))
                power_used = (((rng[np.where(all_freq_options==freq/sd)])[0])) * (VOLTAGE * 1000)
                
            else:
                power_used = (2.0 / 1000) * (VOLTAGE * 1000)
                
        elif mode == "STANDBY":
            if clock == "OSC32K":
                power_used = (1.2 / 1000) * (VOLTAGE * 1000)
                
            elif clock == "XOSC32K":
                if lp=="ON":
                    power_used = (3.2 / 1000) * (VOLTAGE * 1000)
                    
                else:
                    power_used = (1.6 / 1000) * (VOLTAGE * 1000)
                    
            else:
                power_used = (0.7 / 1000) * (VOLTAGE * 1000)
                
        elif mode == "POWER_DOWN":
            power_used = (0.7 / 1000) * (VOLTAGE * 1000)
        else: 
            print("ERROR. Invalid mode selected.")
            return -1
        
        peripheral_power_est = 4 #mW
        
        return power_used + peripheral_power_est

    
    def compute_data(self):
        return 0
    
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_MCR

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
            mode, clock, freq, lp, sd = params
            power = self.compute_power(self,mode, clock, freq, lp, sd)
            for i in range(start_index, end_index):
                power_arr[i] = power

        return np.array(power_arr)
    
    def error_check(self):
        """
          Checks if the configurations contained within self.modes_MCR are valid

          Parameters
          ----------
            None

          Returns
          -------
            error: True if a configuration is invalid, False otherwise
        """
        error = False
        all_configs = self.generate_valid_configs_mcr()
        for param in self.modes_MCR:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error