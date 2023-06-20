from source.Sensor import Sensor
import matplotlib.pyplot as plt
import numpy as np
from typing import List


#ATmega328P class. has code from accelerometer, doesnt work at the moment.
class ATmega328P(Sensor):
    """
        Modes: ACTIVE, IDLE, ADC_NOISE_REDUCTION, POWER_DOWN, POWER_SAVE, STANDBY, EXTENDED_STANDBY
        Disable Components: TWI, TIMER0, TIMER1, TIMER2, ADC, USART, SPI, AC, IVR, WATCHDOG, BOD, PINS, DEBUG
        
    """
    def __init__(self, duration, time_step, loop_rate, averaging=4, timing=10):
        self.timing = timing
        self.duration = duration
        self.time_step = time_step
        self.loop_rate = loop_rate

    def runSim(self, active_times: List[tuple]) -> int:
        """
            This function will call the errorCheck(), getAllModesPower(), getAllModesData() functions. It first checks if the params
            for this sensor are valid and then calls the functions to get the power and data info.

            Args: none

            Returns: 
                power (numpy array)
                data (numpy array)
                time (numpy array)
        """ 
        
        #active_times would be a list of tuples/list that would define the time at which the sensor was running
        # i.e. [[0,1],[4,5],[6,7]] would have the sensor running from time 0s to 1s,
        # 4s to 5s, 6s to 7s
        self.time = np.arange(0,self.duration,self.time_step) #time at which to collect data
        try:
            power, data = self.getVectors(active_times)
            self.plotData(power, data, self.time, active_times)
            return power, data, self.time 
        except TypeError as e:
            print("A type error occurred. Your active times array may exceed the duration set in MPU6050 object.", e)
            return -1
    @staticmethod
    
    def getModePower(mode):
        power_used = 0
        if mode == "off":
            standby_current = 5#microamps
            voltage = 3.3
            power_used = (standby_current * voltage) / 1000 #conversion to mW
        else:
            power_used = 3.3 * 3.3 #in mW, overestimation.
        return power_used
        #returns a vector of when power is used. Units are in mW.

    def getVectors(self, active_times: List[tuple]) -> tuple:
        length = len(self.time)
        powerarr = [0] * length # creating corresponding power array to time intervals, default values 
        dataarr = [0] * length
        # check if the given start and end time is a valid value in the time array and round to nearest value 
        for times in active_times:
            start_index = int(times[0] / self.time_step) # getting index of the closest value to active times 
            end_index = int(times[1] / self.time_step)
            if start_index < 0 or end_index > len(self.time): 
                print("Error. Index not valid.")
                return -1
            params = times[2].split("_")
            mode = params[0]
            if mode != "off": freq = params[1]
            
            curPower = BM1422.getModePower(mode)
            curData = self.getBytesPerSecond(freq)
            for i in range(start_index, length):
                powerarr[i] = curPower
                if i == 0:
                    dataarr[i] = curData
                else:
                    dataarr[i] = dataarr[i-1] + curData
            
        return np.array(powerarr), np.array(dataarr)