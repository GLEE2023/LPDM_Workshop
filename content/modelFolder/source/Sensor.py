import matplotlib.pyplot as plt
import numpy as np
from typing import List
import random

class Sensor:
    """
        Parent class for all sensors. If there is some functionality needed for every sensor,
        put it here.

    """
    def __init__(self, **config):
        #optional init function for any sensor.
        self.__dict__.update(config)

    
    def plotData(self, power_vector: np.array, data_vector: np.array, time_vector: np.array, active_times: List[tuple]) -> None:
        """
            Creates plots given power, data, and time vectors. Active times is needed for the topmost plot.

            Arguments:
                power_vector: calculated values from getVectors() function. 
                data_vector: calculated values from getVectors() function. 
                time_vector: calculated values from getVectors() function. 
                active_times: active times list from generateActiveList() function.
        """
        colors = []
        #num_modes = len(set([time[2] for time in active_times]))#gets number of distinct modes in active_times
        num_modes = 3
        #generates number of random colors for active times plot, different color for each mode (usually).
        for i in range(num_modes):
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            colors.append(color)

        #plot setup/ manipulation.
        fig, (ax1,ax2,ax3) = plt.subplots(nrows=3,ncols=1,sharex=True,gridspec_kw={'height_ratios': [num_modes*0.3, 3, 3]},figsize=(7,7))
        ax1.set_title("Power and Data")
        ax1.set_xlim(0, active_times[-1][1])#set limit to be the last value of active_times.
        ax1.set_ylabel('Active times')
        ax1.grid()

        #active times plot. 
        ticks = {}
        for i,v in enumerate(active_times):
            if v[2] not in ticks.keys():#correspond a color for each mode.
                 ticks[v[2]] = i
            #set each bar with a corresponding color and height
            ax1.broken_barh([(v[0],v[1]-v[0])], (ticks[v[2]], 0.8), color=colors[ticks[v[2]]])#change 0.8 to change height of bars.
        ax1.set_yticks([x + 0.5 for x in ticks.values()], labels=ticks.keys())#set labels for each mode in active times chart

        power_plot, = ax2.plot(time_vector, power_vector)
        ax2.tick_params('y', labelsize=12)
        ax2.tick_params('x', labelbottom=False)
        ax2.set_ylabel('Power (mW)')
        ax2.grid()
        
        data_plot, = ax3.plot(time_vector, data_vector)
        ax3.tick_params('y', labelsize=12)
        ax3.tick_params('x', labelsize=12)
        ax3.set_ylabel('Data (Bytes)')
        ax3.set_xlabel('Seconds')
        ax3.grid()

        plt.ion()
        plt.tight_layout()
        plt.show()