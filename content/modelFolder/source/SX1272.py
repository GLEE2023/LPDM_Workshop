import numpy as np
import matplotlib.pyplot as plt
import random 
from source.helperFunctions import generate_active_list
from source.Sensor import Sensor

VOLTAGE = 3.3 #Volts
MEASUREMENT_RATE = 0 #seconds

class SX1272(Sensor):
    def __init__(self, time_step, duration, modes_SX1, loop_rate): 
        self.time_step = time_step
        self.duration = duration
        self.time = np.arange(0, duration, time_step) #time at which to collect data
        self.active_time_params = generate_active_list(duration, modes_SX1)
        self.loop_rate = loop_rate
        self.modes_SX1 = modes_SX1
        
    def generate_valid_configs_sx1(self):
        """
          Creates a list of all valid SX1272 configurations.

          Parameters
          ----------
            None

          Returns
          -------
            all_configs: list of tuples representing valid configurations
        """
        all_configs = []
        output_power = [7, 13, 17, 20]
        bandwith = [125, 250, 500]
        lna_boost = ["ON", "OFF"]
        rx_mode = ["RXCONTINUOUS", "RXSINGLE"]
        for op in output_power:
            if op == 7:
                op_configs = [("TX",915,7,125,"OFF",12,6,ps) for ps in range(233)]
                all_configs += op_configs
            elif op == 13:
                op_configs = [("TX",915,13,125,"OFF",12,6,ps) for ps in range(233)]
                all_configs += op_configs
            elif op == 17:
                op_configs = [("TX",915,17,125,"OFF",12,6,ps) for ps in range(233)]
                all_configs += op_configs
            elif op == 20:
                op_configs = [("TX",915,20,125,"OFF",12,6,ps) for ps in range(233)]
                all_configs += op_configs
        for b in bandwith:
            if b == 125:
                bandwith_configs = [(mode,915,13,125,lna,12,6,ps) for mode in rx_mode for lna in lna_boost for ps in range(256)]
                cad_configs = [("CAD",915,13,125,"OFF",12,6,ps) for ps in range(233)]
                all_configs += bandwith_configs + cad_configs
            elif b == 250:
                bandwith_configs = [(mode,915,13,250,lna,12,6,ps) for mode in rx_mode for lna in lna_boost for ps in range(256)]
                cad_configs = [("CAD",915,13,250,"OFF",12,6,ps) for ps in range(233)]
                all_configs += bandwith_configs +cad_configs
            elif b == 500:
                bandwith_configs = [(mode,915,13,500,lna,12,6,ps) for mode in rx_mode for lna in lna_boost for ps in range(256)]
                cad_configs = [("CAD",915,13,500,"OFF",12,6,ps) for ps in range(233)]
                all_configs += bandwith_configs + cad_configs


        fstx_config = [("FSTX",915,13,125,"OFF",12,6,ps) for ps in range(233)]
        fsrx_config = [("FSRX",915,13,125,"OFF",12,6,ps) for ps in range(233)]
        sleep_config = [("SLEEP",915,13,125,"OFF",12,6,ps) for ps in range(233)]
        standby_config = [("STANDBY",915,13,125,"OFF",12,6,ps) for ps in range(233)]
        idle_config = [("IDLE",915,13,125,"OFF",12,6,ps) for ps in range(233)]
        all_configs += fstx_config + fsrx_config + sleep_config + standby_config + idle_config
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
        error = False
        all_configs = self.generate_valid_configs_sx1()
        for param in self.modes_SX1:
            if param[0] not in all_configs:
                print("Error. Invalid configuration {}. Valid Configurations to choose from: {}".format(param[0], all_configs))
                error = True

        return error
    
    def compute_power(self, mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size, transmission_reception_rate):
        """
          Computes power consumption of a given configuration.

          Parameters
          ----------

          Returns
          -------
            power: Float representing power in mW
        """    
        power = 0
        active_time_period = payload_size*8/4800
        standby_time = 1 - active_time_period #an estimate
        modes = ["SLEEP", "STANDBY", "TX", "RXCONTINUOUS", "RXSINGLE", "IDLE", "FSTX", "FSRX", "CAD"]
        if frequency == 915 and spreading_factor == 12 and coding_rate == 6:
          if mode == modes[0]:
              power = ((0.1*VOLTAGE)/1000)
          elif mode == modes[1]:
              power = (1.4*VOLTAGE)
          elif mode == modes[2]:
            if active_time_period < transmission_reception_rate:
                if output_power == 7:
                    power = (active_time_period)*(18*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                elif output_power == 13:
                    power = (active_time_period)*(28*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                elif output_power == 17:
                    power = (active_time_period)*(90*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                elif output_power == 20:
                    power = (active_time_period)*(125*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
            else:
                print('Your choice of transmission rate exceeded the speed of the SX1272 sensor.')
            
          elif mode == modes[3]:
            if active_time_period < transmission_reception_rate:
                if lna_boost == "OFF":
                    if bandwidth == 125:
                        power = (active_time_period)*(9.7*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 250:
                        power = (active_time_period)*(10.5*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 500:
                        power = (active_time_period)*(12*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                elif lna_boost == "ON":
                    if bandwidth == 125:
                        power = (active_time_period)*(10.8*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 250:
                        power = (active_time_period)*(11.6*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 500:
                        power = (active_time_period)*(13*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
            else:
                print('Your choice of reception rate exceeded the speed of the SX1272 sensor.')

          elif mode == modes[4]:
            if active_time_period < transmission_reception_rate:
                if lna_boost == "OFF":
                    if bandwidth == 125:
                        power = (active_time_period)*(9.7*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 250: 
                        power = (active_time_period)*(10.5*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 500:
                        power = (active_time_period)*(12*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                elif lna_boost == "ON":
                    if bandwidth == 125:
                        power = (active_time_period)*(10.8*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 250:
                        power = (active_time_period)*(11.6*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
                    elif bandwidth == 500:
                        power = (active_time_period)*(13*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
            else:
                print('Your choice of reception rate exceeded the speed of the SX1272 sensor.')
          elif mode == modes[5]:
              power = ((1.5*VOLTAGE)/1000)
          elif mode == modes[6]:
            if active_time_period < transmission_reception_rate:
                power = (active_time_period)*(4.5*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
            else:
                print('Your choice of transmission rate exceeded the speed of the SX1272 sensor.')
          elif mode == modes[7]:
            if active_time_period < transmission_reception_rate:
                power = (active_time_period)*(4.5*VOLTAGE) + (standby_time * ((1.5*VOLTAGE)/1000))
            else:
                print('Your choice of reception rate exceeded the speed of the SX1272 sensor.')
          elif mode == modes[8]:
              if bandwidth == 125:
                power = (active_time_period)*(10.8*VOLTAGE)
              elif bandwidth == 250:
                power = (active_time_period)*(11.6*VOLTAGE) 
              elif bandwidth == 500:
                power = (active_time_period)*(13*VOLTAGE) 
        else:
              print('Please keep the standard configuration for frequency, spreading factor and coding rate')  
        return power
    
    def compute_data(self, mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size, transmission_reception_rate):
        """
          Computes data usage of a given configuration.

          Parameters
          ----------
            

          Returns
          -------
            data: number of bytes used in 1 second
        """ 
        data = 0
        if (mode == "SLEEP" or mode == "STANDBY" or mode == "IDLE"):
            return data
        if (mode == "RXCONTINUOUS" or mode == "RXSINGLE" or mode == "FSRX"):
            data = payload_size / transmission_reception_rate
        if (mode == "TX" or mode == "FSTX"):
            data = payload_size / (-1*transmission_reception_rate)
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
        # Code here
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
            mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size = params
            sampling_rate = times[3]

                # if conv_cycle_time > 0:   
                #     if self.loop_rate < 1/conv_cycle_time:
                #         conv_cycle_time = 1/self.loop_rate

            power = self.compute_power(mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size, sampling_rate)

            for i in range(start_index, end_index):
                power_arr[i] = power

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
        length = len(self.time)
        data_arr = [0] * length
        data_accumulated = 0

        for times in self.active_time_params: # for each active period
            start_index = int(times[0] / self.time_step) 
            end_index = int(times[1] / self.time_step)
            params = times[2]
            mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size = params
            sampling_rate = times[3]
            data_per_second = self.compute_data(mode, frequency, output_power, bandwidth, lna_boost, spreading_factor, coding_rate, payload_size, sampling_rate)

            for i in range(start_index, length):
                if i < end_index:
                    data_accumulated += data_per_second
                data_arr[i] = data_accumulated 
        
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