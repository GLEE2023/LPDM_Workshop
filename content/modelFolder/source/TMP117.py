import numpy as np
import matplotlib.pyplot as plt
import random 
from source.helperFunctions import generate_active_list
from source.Sensor import Sensor

CONVERSION_DURATION = 0.0155 #seconds
VOLTAGE = 3.3 #Volts
SHUTDOWN_CURRENT = 0.15 #μA
ACTIVE_CURRENT = 135 #μA
STANDBY_CURRENT = 1.25 #μA
READ_BYTES = 6 #bytes, 2 for temperature data and 4 for timestamp

class TMP117(Sensor):
    def __init__(self, time_step, duration, modes_tmp, loop_rate): 
        self.time_step = time_step
        self.duration = duration
        self.time = np.arange(0, duration, time_step) #time at which to collect data
        self.active_time_params = generate_active_list(duration, modes_tmp)
        self.loop_rate = loop_rate
        self.modes_tmp = modes_tmp
    
    def generate_valid_configs_tmp(self):
        """
          Creates a list of all valid TMP117 configurations.

          Parameters
          ----------
            None

          Returns
          -------
            all_configs: list of tuples representing valid configurations
        """
        num_averages_options = [0, 8, 32, 64]
        conv_cycle_time_options = [0.0155, 0.125, 0.25, 0.5, 1, 4, 8, 16] 
        mode_options = ["CONTINUOUS_CONVERSION", "ONE_SHOT", "SHUTDOWN"]
        all_configs = []

        for averages in num_averages_options:
            if averages == 0:
                time_options_trunc = conv_cycle_time_options[0:]
                cc_configs = [("CONTINUOUS_CONVERSION", 0, time) for time in time_options_trunc]
                all_configs += cc_configs
            elif averages == 8:
                time_options_trunc = conv_cycle_time_options[1:]
                cc_configs = [("CONTINUOUS_CONVERSION", 8, time) for time in time_options_trunc]
                all_configs += cc_configs
            elif averages == 32:
                time_options_trunc = conv_cycle_time_options[3:]
                cc_configs = [("CONTINUOUS_CONVERSION", 32, time) for time in time_options_trunc]
                all_configs += cc_configs
            elif averages == 64:
                time_options_trunc = conv_cycle_time_options[4:]
                cc_configs = [("CONTINUOUS_CONVERSION", 64, time) for time in time_options_trunc]
                all_configs += cc_configs

        os_configs = [("ONE_SHOT",0,0.0155),("ONE_SHOT",8,0.0155),("ONE_SHOT",32,0.0155),("ONE_SHOT",64,0.0155)]
        all_configs += os_configs + [('SHUTDOWN',0,0)]

        return all_configs

    def error_check(self):
        """
          Checks if the configurations contained within self.modes_tmp are valid

          Parameters
          ----------
            None

          Returns
          -------
            error: True if a configuration is invalid, False otherwise
        """
        error = False
        all_configs = self.generate_valid_configs_tmp()
        for param in self.modes_tmp:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error

    def compute_power(self, mode, num_averages = 8, conv_cycle_time = 0.0155, sampling_rate = 1):
        """
          Computes power consumption of a given configuration.

          Parameters
          ----------
            mode: String representing mode of TMP117 sensor
            conv_cycle_time: Float representing how often conversions are accumulated (for Continuous)
            num_averages: Int representing how many conversions are averaged together for a data sample

          Returns
          -------
            power: Float representing power in mW
        """      
        sd_current = SHUTDOWN_CURRENT
        active_current_consumption = ACTIVE_CURRENT
        standby_current_consumption = STANDBY_CURRENT

        current = 0
        standby_time = 0
        active_conversion_time = num_averages * CONVERSION_DURATION

        # COMPUTE POWER FOR MODE
        if mode == "CONTINUOUS_CONVERSION":
            if num_averages == 0:
                active_conversion_time = CONVERSION_DURATION 

            if active_conversion_time < conv_cycle_time: 
                standby_time = conv_cycle_time - active_conversion_time
            else:
                conv_cycle_time = active_conversion_time
            current = (((active_current_consumption/1000)*active_conversion_time)+((standby_current_consumption/1000)*standby_time))/conv_cycle_time 
            
        elif mode == "ONE_SHOT":
            if num_averages == 0:
                active_conversion_time = CONVERSION_DURATION

            if active_conversion_time < sampling_rate: 
                standby_time = sampling_rate - active_conversion_time
            else:
                sampling_rate = active_conversion_time
                print('Your selected sampling rate exceeded the speed of the TMP117 sensor.')
            
            current = ((((active_current_consumption)/1000)*active_conversion_time)+(((sd_current)/1000)*standby_time)) / (sampling_rate)
        
        elif mode == "SHUTDOWN":
            current = sd_current/1000
            
        power = (current * (VOLTAGE * 1000)) 

        return power
    
    def compute_data(self, mode, conv_cycle_time = 0.0155, num_averages = 8, sampling_rate = 1):
        """
          Computes data usage of a given configuration.

          Parameters
          ----------
            mode: String representing mode of TMP117 sensor
            conv_cycle_time: Float representing how often conversions are accumulated (for Continuous)
            num_averages: Int representing how many conversions are averaged together for a data sample
            sampling_rate: Float representing the number of seconds between samples (for One_Shot)

          Returns
          -------
            data: number of bytes used in 1 second
        """ 
        #active_conversion_time = num_averages * CONVERSION_DURATION
        data = 0
        
        if (mode == "SHUTDOWN"):
            return data
        
        #if (active_conversion_time >= conv_cycle_time):
        #    conv_cycle_time = active_conversion_time
        
        data = READ_BYTES / sampling_rate
        
        return data
    
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_tmp

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
            if params != "SHUTDOWN":
                mode, conv_cycle_time, num_averages = params
                sampling_rate = times[3]

                # if conv_cycle_time > 0:   
                #     if self.loop_rate < 1/conv_cycle_time:
                #         conv_cycle_time = 1/self.loop_rate

                power = self.compute_power(mode, conv_cycle_time, num_averages, sampling_rate)

            for i in range(start_index, end_index):
                power_arr[i] = power

        return power_arr
            
    def get_all_modes_data(self):
        """
          Computes the data usage of all modes in modes_tmp

          Parameters
          ----------
            None

          Returns
          -------
            data_arr: list of all computed data usages
        """    
        length = len(self.time)
        data_arr = [0] * length # creating corresponding power array to time intervals, default values 
        data_accumulated = 0
        
        for times in self.active_time_params: # for each active period
            start_index = int(times[0] / self.time_step) 
            end_index = int(times[1] / self.time_step)
            params = times[2]
            mode, conv_cycle_time, num_averages = params
            sampling_rate = times[3]
            data_per_second = self.compute_data(mode, conv_cycle_time, num_averages, sampling_rate)

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
                
        return data_arr
    
    def run_sim(self):
        """
          Checks if modes are valid before coputer the power and data usage of given configurations in modes_tmp. Plots results.

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
# time_step = 0.0155
# active_time_params = [(0, 15, "OS_8_0.0155"), (5, 45, "CC_32_16"), (70, 75, "OS_64_1"), (75,100, "OS_8_0.0155")]
# tmp = TMP117(time_step, 100, active_time_params, loop_rate = 20) # creating TMP117 class
# tmp.run_sim(plot=True)