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

    def generate_valid_configs_acc(self):
        low_power_wakeup = [0, 1.25, 5, 20, 40]
        digital_low_pass = ["000", "001", "010", "011", "100", "101", "110", "111" ]
        mode_options = ["ACCELEROMETER", "ACCELEROMETER_LOW_POWER", "GYROSCOPE", "GYROSCOPE_DMP", "ACCELEROMETER_AND_GYROSCOPE", "ACCELEROMETER_AND_GYROSCOPE_DMP", "SHUTDOWN"]
        sample_rate_divisor = []
        all_configs = []

        for lpw in low_power_wakeup:
            if lpw == 1.25:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 1.25, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
                all_configs += lpw_configs
            elif lpw == 5:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 5, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
                all_configs += lpw_configs
            elif lpw == 20:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 20, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
                all_configs += lpw_configs
            elif lpw == 40:
                dlp_options_trunc = digital_low_pass[1:7]
                lpw_configs = [("ACCELEROMETER_LOW_POWER", 40, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
                all_configs += lpw_configs
        dlp_options_trunc = digital_low_pass[1:7]
        accelerometer_config = [("ACCELEROMETER",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
        gyroscope_config = [("GYROSCOPE",0, dlp, srd) for dlp in digital_low_pass for srd in range(256)]
        gyroscope_dmp_config = [("GYROSCOPE_DMP",0, dlp, srd) for dlp in digital_low_pass for srd in range(256)]
        accelerometer_gyroscope_config = [("ACCELEROMETER_AND_GYROSCOPE",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
        accelerometer_gyroscope_dmp_config = [("ACCELEROMETER_AND_GYROSCOPE_DMP",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
        all_configs += accelerometer_config + gyroscope_config + gyroscope_dmp_config + accelerometer_gyroscope_config +accelerometer_gyroscope_dmp_config + [('SHUTDOWN',0,"000", srd) for srd in range(256)]
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
        all_configs = self.generate_valid_configs_acc()
        for param in self.modes_mpu:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True
        return error
    
    def get_mode_power(self, mode, low_power_wakeup, digital_low_pass, sample_rate_divisor, sampling_rate):
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
        #this formula will be heavily influenced by sample_rate_divisor. See page 11 of the register map for the full equation.
            #https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf
        if len(digital_low_pass) == 3:
                gyroscope_output_rate = 8000 if digital_low_pass == "000" or digital_low_pass == "111" else 1000
        else:
                print("Error. Digital Low Pass needs to be a 3 bit number.")
        active_conversion_time = 1/((gyroscope_output_rate*1000) / (1 + sample_rate_divisor)) #how fast measurements are written to
        active_conversion_time *= 1000 # overestimation
        #accelerometer measurement registers, in Hz.
        if mode == "ACCELEROMETER_LOW_POWER":
            if digital_low_pass != "000" and digital_low_pass !="111":
                if active_conversion_time < sampling_rate:
                    if low_power_wakeup == 1.25:
                        power = ((10*VOLTAGE)/1000)/sampling_rate
                    elif low_power_wakeup == 5:
                        power = ((20*VOLTAGE)/1000)/sampling_rate
                    elif low_power_wakeup == 20:
                        power = ((70*VOLTAGE)/1000)/sampling_rate
                    elif low_power_wakeup == 40:
                        power = ((140*VOLTAGE)/1000)/sampling_rate
                    else:
                        print('This particular low_power_wakeup value does not exit')
                else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')
            else:
                print('Your choice of digital_low_pass does not exist for the MPU6000 sensor.')
        elif mode == "ACCELEROMETER_AND_GYROSCOPE":
            if digital_low_pass != "000" and digital_low_pass !="111":
                if active_conversion_time < sampling_rate:
                    power = ((3.8*VOLTAGE))/sampling_rate
                else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')
            else:
                print('Your choice of digital_low_pass does not exist for the MPU6000 sensor.')

        elif mode == "ACCELEROMETER":
            if digital_low_pass != "000" and digital_low_pass !="111":
                if active_conversion_time < sampling_rate:
                    power = ((500*VOLTAGE)/1000)/sampling_rate
                else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')
            else:
                print('Your choice of digital_low_pass does not exist for the MPU6000 sensor.')
        elif mode == "GYROSCOPE":
            if active_conversion_time < sampling_rate:
                power = ((3.6*VOLTAGE))/sampling_rate
            else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')   
        elif mode == "ACCELEROMETER_AND_GYROSCOPE_DMP":
            if digital_low_pass != "000" and digital_low_pass !="111":
                if active_conversion_time < sampling_rate:
                    power = ((3.9*VOLTAGE))/sampling_rate
                else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')
            else:
                print('Your choice of digital_low_pass does not exist for the MPU6000 sensor.')   
        elif mode == "GYROSCOPE_DMP":
            if active_conversion_time < sampling_rate:
                power = ((3.7*VOLTAGE))/sampling_rate
            else:
                    print('Your choice of sample frequency exceed the speed of the MPU6000 sensor.')
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
            mode, low_power_wakeup, digital_low_pass, sample_rate_divisor = params
            power = self.get_mode_power(mode, low_power_wakeup, digital_low_pass,sample_rate_divisor, times[3])

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
            mode, low_power_wakeup, digital_low_pass, sampling_rate_divisor = params
            data_per_second = self.get_bytes_per_second(mode, low_power_wakeup, digital_low_pass, sampling_rate_divisor, times[3])

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
                
        return data_arr


    def get_bytes_per_second(self, mode, low_power_wakeup, digital_low_pass, sampling_rate_divisor, sampling_rate):
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
                return (12+4)/sampling_rate
            else:
                return (6+4)/sampling_rate


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