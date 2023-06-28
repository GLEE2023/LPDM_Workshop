import numpy as np
from source.Sensor import Sensor
from typing import List
from source.helperFunctions import generate_active_list

VOLTAGE = 3.3 #Volts

class MPU6000(Sensor):
    def __init__ (self, time_step, duration, modes_mpu, loop_rate):
        self.time_step = time_step
        self.duration = duration
        self.low_power_wakeup = 0 #In Hz, determines how fast the sensor wakes up when in low power mode. More wakeups means more power used.
        self.active_time_params = generate_active_list(duration, modes_mpu)
        self.modes_mpu = modes_mpu
        self.loop_rate = loop_rate
        self.time = np.arange(0,self.duration,self.time_step)

    def generate_valid_configs_tp(self):
        low_power_wakeup = [1.25, 5, 20, 40]
        digital_low_pass = ["000", "001", "010", "011", "100", "101", "110", "111" ]
        mode_options = ["ACCELEROMETER", "ACCELEROMETER_LOW_POWER", "GYROSCOPE", "GYROSCOPE_DMP", "ACCELEROMETER_AND_GYROSCOPE", "ACCELEROMETER_AND_GYROSCOPE_DMP", "SHUTDOWN"]
        all_configs = []

        for lpw in low_power_wakeup:
            if lpw == 1.25:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 1.25, dlp) for dlp in dlp_options_trunc]
                all_configs += lpw_configs
            elif lpw == 5:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 5, dlp) for dlp in dlp_options_trunc]
                all_configs += lpw_configs
            elif lpw == 20:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 20, dlp) for dlp in dlp_options_trunc]
                all_configs += lpw_configs
            elif lpw == 40:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 40, dlp) for dlp in dlp_options_trunc]
                all_configs += lpw_configs

        os_configs = [("ACCELEROMETER",0,"001"), ("ACCELEROMETER",0,"010"), ("ACCELEROMETER",0,"011"), ("ACCELEROMETER",0,"100"), ("ACCELEROMETER",0,"101"), ("ACCELEROMETER",0,"110"),
                      ("GYROSCOPE",0,"000"), ("GYROSCOPE",0,"001"), ("GYROSCOPE",0,"010"), ("GYROSCOPE",0,"011"), ("GYROSCOPE",0,"100"), ("GYROSCOPE",0,"101"), ("GYROSCOPE",0,"110"), ("GYROSCOPE",0,"111"),
                      ("GYROSCOPE_DMP",0,"000"), ("GYROSCOPE_DMP",0,"001"), ("GYROSCOPE_DMP",0,"010"), ("GYROSCOPE_DMP",0,"011"), ("GYROSCOPE_DMP",0,"100"), ("GYROSCOPE_DMP",0,"101"), ("GYROSCOPE_DMP",0,"110"), ("GYROSCOPE_DMP",0,"111"),
                      ("ACCELEROMETER_AND_GYROSCOPE",0,"001"), ("ACCELEROMETER_AND_GYROSCOPE",0,"010"), ("ACCELEROMETER_AND_GYROSCOPE",0,"011"), ("ACCELEROMETER_AND_GYROSCOPE",0,"100"), ("ACCELEROMETER_AND_GYROSCOPE",0,"101"), ("ACCELEROMETER_AND_GYROSCOPE",0,"110"), 
                     ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"001"), ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"010"), ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"011"), ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"100"), ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"101"), ("ACCELEROMETER_AND_GYROSCOPE_DMP",0,"110")]
        all_configs += os_configs + [('SHUTDOWN',0,"000")]
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
        for param in self.modes_mpu:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error
    
    def get_mode_power(self, mode, low_power_wakeup, digital_low_pass):
        """
          This function calculates power when sensor is active

          Parameters
          ----------
            mode: String representing mode of MPU6000 sensor
            low_power_wakeup: Float representing how fast the sensor wakes up when in low power mode

          Returns
          -------
            A vector of when power is used. Units are in mW.
        """ 
        power = 0
        if mode == "ACCELEROMETER_LOW_POWER":
            if low_power_wakeup == 1.25:
                power = (10*VOLTAGE)/1000
            elif low_power_wakeup == 5:
                power = (20*VOLTAGE)/1000
            elif low_power_wakeup == 20:
                power = (70*VOLTAGE)/1000
            elif low_power_wakeup == 40:
                power = (140*VOLTAGE)/1000
            else:
                print('This particular low_power_wakeup value does not exit')
        elif mode == "ACCELEROMETER_AND_GYROSCOPE":
            power = (3.8*VOLTAGE)
        elif mode == "ACCELEROMETER":
            power = (500*VOLTAGE)/1000
        elif mode == "GYROSCOPE":
            power = (3.6*VOLTAGE)
        elif mode == "ACCELEROMETER_AND_GYROSCOPE_DMP":
            power = (3.9*VOLTAGE)
        elif mode == "GYROSCOPE_DMP":
            power = (3.7*VOLTAGE)
        elif mode == "SHUTDOWN":
            power = 0
        return power
        
    def run_sim(self) :
        """
          Checks if modes are valid before coputer the power and data usage of given configurations in modes_mpu. Plots results.

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
        
    def get_all_modes_power(self):
        """
          Computes the power consumption of all modes in modes_mpu

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
            mode, low_power_wakeup, digital_low_pass = params
            power = self.get_mode_power(mode, low_power_wakeup, digital_low_pass)

            for i in range(start_index, end_index):
                power_arr[i] = power

        return power_arr
    def get_all_modes_data(self):
        """
          Computes the data usage of all modes in modes_mpu

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
            mode, low_power_wakeup, digital_low_pass = params
            data_per_second = self.get_bytes_per_second(mode, low_power_wakeup, digital_low_pass, times[3])

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
                
        return data_arr


    def get_bytes_per_second(self, mode, low_power_wakeup, digital_low_pass, sampling_rate_divisor):
        """
          This function calculates the data being collected and how much

          Parameters
          ----------
            mode: String representing mode of MPU6000 sensor
            low_power_wakeup: Float representing how fast the sensor wakes up when in low power mode
            digital_low_pass: Int representing a way to lower the sample_rate of the sensor

          Returns
          -------
            The measure rate and how much data is being collected in Bytes
        """
        error = self.error_check()
        if error == False:
            if mode == "SHUTDOWN" :
                return 0
                          
            if mode == "ACCELEROMETER_AND_GYROSCOPE" or mode == "ACCELEROMETER_AND_GYROSCOPE_DMP":
                return (12+4)*sampling_rate_divisor
            else:
                return (6+4)*sampling_rate_divisor


"""
#this function will be heavily influenced by sample_rate_divisor. See page 11 of the register map for the full equation.
            #https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
            if len(digital_low_pass) == 3:
                gyroscope_output_rate = 8000 if digital_low_pass == "000" or digital_low_pass == "111" else 1000
            else:
                print("Error. Digital Low Pass needs to be a 3 bit number.")

            if (1/sampling_rate_divisor) > gyroscope_output_rate:
                sampling_rate_divisor = 1 / gyroscope_output_rate
                
            measure_rate = sampling_rate_divisor
            if mode == "ACCELEROMETER_LOW_POWER" : #accelerometer measurement registers, in Hz.
                measure_rate = low_power_wakeup
                return (6+4)*measure_rate
"""