from source.Sensor import Sensor
import matplotlib.pyplot as plt
import numpy as np
from typing import List
from source.helperFunctions import generate_active_list

VOLTAGE = 3.3 #Volts
STANDBY_CURRENT_OVER = 5 #μA, overestimation
ACTIVE_CURRENT_OVER = 300 #μA, overestimation
STANDBY_CURRENT = 1.5 #μA
ACTIVE_CURRENT= 150 #μA
READ_BYTES = 9 #bytes, 5 for temperature data and 4 for timestamp
MEASUREMENT_DURATION = 0.0005 #s

#Magnetometer class. has code from accelerometer, doesnt work at the moment.
class BM1422(Sensor):
    def __init__(self, duration, time_step, loop_rate, modelist):
        self.duration = duration
        self.time_step = time_step
        self.time = np.arange(0, duration, time_step) #time at which to collect data
        self.loop_rate = loop_rate
        self.modes_mag = modelist
        self.active_time_params = generate_active_list(duration, self.modes_mag)
        
    def generate_valid_configs_mag(self):
        """
          Creates a list of all valid BM1422 configurations.

          Parameters
          ----------
            None

          Returns
          -------
            all_configs: list of tuples representing valid configurations
        """
        num_averages_options = [1, 2, 4, 8, 16]
        freq_options = [10, 20, 100, 1000]
        mode_options = ["CONTINUOUS", "SINGLE", "POWER_DOWN"]
        all_configs = []

        for averages in num_averages_options:
            if averages == 1:
                freq_options_trunc = freq_options[0:]
                configs = [("CONTINUOUS", freq, 1) for freq in freq_options_trunc]
                all_configs += configs
            elif averages == 2:
                freq_options_trunc = freq_options[0:]
                configs = [("CONTINUOUS", freq, 2) for freq in freq_options_trunc]
                all_configs += configs
            elif averages == 4:
                freq_options_trunc = freq_options[:3]
                configs = [("CONTINUOUS", freq, 4) for freq in freq_options_trunc]
                all_configs += configs
            elif averages == 8:
                freq_options_trunc = freq_options[:3]
                configs = [("CONTINUOUS", freq, 8) for freq in freq_options_trunc]
                all_configs += configs
            elif averages == 16:
                freq_options_trunc = freq_options[:3]
                configs = [("CONTINUOUS", freq, 16) for freq in freq_options_trunc]
                all_configs += configs

        s_configs = [("SINGLE",1000,1),("SINGLE",1000,2),("SINGLE",1000,4),("SINGLE",1000,8),("SINGLE",1000,16)]
        all_configs += s_configs + [('POWER_DOWN',0,0)]

        return all_configs
    
    def run_sim(self):
        """
            This function will call the error_check(), get_all_modes_power(), get_all_modes_data() functions. It first checks if the params
            for this sensor are valid and then calls the functions to get the power and data info.

        Parameters
        ----------
            None

        Returns
        -------
            power (numpy array)
            data (numpy array)
            time (numpy array)
        """ 
        
        #active_times would be a list of tuples/list that would define the time at which the sensor was running
        # i.e. [[0,1],[4,5],[6,7]] would have the sensor running from time 0s to 1s,
        # 4s to 5s, 6s to 7s
        error = self.error_check()
        if error == False:
            power = self.get_all_modes_power()
            data = self.get_all_modes_data()
            self.plotData(power, data, self.time, self.active_time_params)

            return np.array(power), np.array(data), np.array(self.time)
        return [], [], []


    def compute_data(self, mode, sample_freq, averaging, sampling_rate):
        """
          Computes data usage of a given configuration.

          Parameters
          ----------
            mode: String representing mode of BM1 sensor
            conv_cycle_time: Float representing how often conversions are accumulated (for Continuous)
            num_averages: Int representing how many conversions are averaged together for a data sample
            sampling_rate: Float representing the number of seconds between samples (for One_Shot)

          Returns
          -------
            data: number of bytes used in 1 second
        """ 
        if mode == "POWER_DOWN":
            return 0
        return READ_BYTES / sampling_rate # bytes
    
    def compute_power(self, mode, sample_freq, averaging, sampling_rate):
        """
          Computes power consumption of a given configuration.

          Parameters
          ----------
            mode: String representing mode of BM1 sensor
            sample_freq: Float representing how often samples are taken (for CONTINUOUS)
            averaging: Int representing how many samples are averaged together for a outputted data sample
            sampling_rate: Float representing the time between samples being requested

          Returns
          -------
            power: Float representing power in mW
        """      
        active_current_consumption = ACTIVE_CURRENT
        standby_current_consumption = STANDBY_CURRENT

        current = 0
        standby_time = 0
        active_conversion_time = averaging * MEASUREMENT_DURATION

        # COMPUTE POWER FOR MODE
        if mode == "CONTINUOUS":

            if active_conversion_time < 1 / sample_freq: 
                standby_time = 1 / sample_freq - active_conversion_time
            else:
                print('Your choice of sample frequency & selectable averaging exceed the speed of the BM1 sensor.')

            current = (((active_current_consumption/1000)*active_conversion_time)+((standby_current_consumption/1000)*standby_time)) * sample_freq
            
        elif mode == "SINGLE":

            if active_conversion_time < sampling_rate: 
                standby_time = sampling_rate - active_conversion_time
            else:
                sampling_rate = active_conversion_time
                print('Your choice of sampling rate & selectable averaging exceeded the speed of the BM1 sensor.')

            current = ((((active_current_consumption)/1000)*active_conversion_time)+(((standby_current_consumption)/1000)*standby_time)) / (sampling_rate)
        
        elif mode == "POWER_DOWN":
            current = standby_current_consumption / 1000
            
        power = (current * (VOLTAGE * 1000)) 

        return power
    
    def compute_power_overest(self, mode, sample_freq, averaging, sampling_rate):
        """
          Computes overestimated power consumption of a given configuration.

          Parameters
          ----------
            mode: String representing mode of BM1 sensor
            sample_freq: Float representing how often samples are taken (for CONTINUOUS)
            averaging: Int representing how many samples are averaged together for a outputted data sample
            sampling_rate: Float representing the time between samples being requested

          Returns
          -------
            power: Float representing power in mW
        """      
        active_current_consumption = ACTIVE_CURRENT_OVER
        standby_current_consumption = STANDBY_CURRENT_OVER

        current = 0
        standby_time = 0
        active_conversion_time = averaging * MEASUREMENT_DURATION

        # COMPUTE POWER FOR MODE
        if mode == "CONTINUOUS":

            if active_conversion_time < 1 / sample_freq: 
                standby_time = 1 / sample_freq - active_conversion_time
            else:
                print('Your choice of sample frequency & selectable averaging exceed the speed of the BM1 sensor.')

            current = (((active_current_consumption/1000)*active_conversion_time)+((standby_current_consumption/1000)*standby_time)) * sample_freq
            
        elif mode == "SINGLE":

            if active_conversion_time < sampling_rate: 
                standby_time = sampling_rate - active_conversion_time
            else:
                sampling_rate = active_conversion_time
                print('Your choice of sampling rate & selectable averaging exceeded the speed of the BM1 sensor.')

            current = ((((active_current_consumption)/1000)*active_conversion_time)+(((standby_current_consumption)/1000)*standby_time)) / (sampling_rate)
        
        elif mode == "POWER_DOWN":
            current = standby_current_consumption / 1000
            
        power = (current * (VOLTAGE * 1000)) 

        return power
    
    
    def error_check(self):
        """
          Checks if the configurations contained within self.modes_mag are valid

          Parameters
          ----------
            None

          Returns
          -------
            error: True if a configuration is invalid, False otherwise
        """
        error = False
        all_configs = self.generate_valid_configs_mag()
        for param in self.modes_mag:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error
    
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_mag

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
            mode, sample_freq, num_averages = params
            sampling_rate = times[3]

            power = self.compute_power_overest(mode, sample_freq, num_averages, sampling_rate)

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
            mode, sample_freq, num_averages = params
            sampling_rate = times[3]
            data_per_second = self.compute_data(mode, sample_freq, num_averages, sampling_rate)

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
                
        return data_arr