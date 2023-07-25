import matplotlib.pyplot as plt
import numpy as np
import random

def generate_active_list(total_time: float, modelist: list) -> list:
    """
    Returns list similar to the form of active_times, but based off of modedict.
    active_times: [(int(start1), int(end1), "mode1"), (int(start2), int(end2), "mode2")]

    Parameters
        total_time (float): total active time of the sensor, ie 10 seconds or 10 hours.
        modelist (list): numpy array describing scheduling period

    returns:
        final_arr, list of active times of each mode
    """

    modelist = np.array(modelist,dtype=object)
    keys = modelist[:,0]
    final_arr = []
    curr_time = 0
    flag = False
    while curr_time < total_time:
        #for val in values:
        for item in modelist:
            mode_duration = int(item[1])
            if curr_time+mode_duration>total_time:
                flag = True
                break
            final_arr.append((curr_time, curr_time+mode_duration, item[0],item[2]))
            curr_time += mode_duration
        if flag: 
            break
    mode = len(final_arr) % len(modelist)
    if final_arr[-1][1] > total_time:
        final_arr[-1] = (final_arr[-1][0], total_time, keys[mode])
    elif final_arr[-1][1] < total_time:
        final_arr.append((final_arr[-1][1], total_time, keys[mode]))
    return final_arr
    #final_arr is a list of tuples in the form (start, stop, mode): [(start,stop, mode), ...]

def plot_total_data(time_list: np.array, data_list: np.array): 
    """
    Plot each line in data_list using time_list.
    
    Parameters
        time_list (numpy array): list of time vectors returned from run_sim for each sensor.
        data_list (numpy array): list of data vectors returned from run_sim for each sensor.

    Returns
        None
    """
    
    label_reference = {
        0:"Min. Data", 1:"Accelerometer Sensor", 2:"Magnetometer Sensor", 3:"Thermopile Sensor", 
        4:"Temperature Sensor", 5:"Capacitive Sensor", 6:"Microcontroller", 7:"Total Data"
    }
    
    for i in range(0,8):
        plt.plot(time_list[i],data_list[i],label=label_reference[i])

    datarate_limit = 1000
    max_datarate = np.ones(len(data_list[0]))
    for i in range(0,len(max_datarate)):
        max_datarate[i] = (i * datarate_limit) + datarate_limit
    plt.plot(time_list[0],max_datarate,label="Max. Datarate")
    plt.grid(visible=True)
    plt.xlabel("Time (s)",fontsize=16)
    plt.ylabel("Data (Bytes)",fontsize=16)
    plt.title("Data vs Time for all Components",fontsize=16)
    plt.ion()
    plt.tight_layout()
    plt.legend()
    
    timePossible = np.where(data_list[7]>max_datarate,time_list[0],None)
    for i in range(0,len(max_datarate)):
        if(timePossible[i]!=None and i!=0):
            print("ERROR! At least one of your configurations exceeds the maximum datarate at " + str(i) + " seconds.")
            return "ERROR"
    return "Configurations meet datarate requirements"
    
def plot_total_power(time_list: np.array, power_list: np.array):
    """
    Plot each line in power_list using time_list.
    
    Parameters
        time_list (numpy array): list of time vectors returned from run_sim for each sensor.
        power_list (numpy array): list of power vectors returned from run_sim for each sensor.

    Returns
        None
    """
    
    label_reference = {
        0:"Min. Power", 1:"Accelerometer Sensor", 2:"Magnetometer Sensor", 3:"Thermopile Sensor", 
        4:"Temperature Sensor", 5:"Capacitive Sensor", 6:"Microcontroller", 7:"Total Power"
    }
    
    for i in range(0,8):
        plt.plot(time_list[i],power_list[i],label=label_reference[i])

    plt.grid(visible=True)
    plt.xlabel("Time (s)",fontsize=16)
    plt.ylabel("Power (mW)",fontsize=16)
    plt.title("Power vs Time for all Components",fontsize=16)
    plt.ion()
    plt.tight_layout()
    plt.legend()
    
def valid():
    """
    Finds all valid configuration options
    
    Parameters
        None

    Returns
        Valid configurations for all 5 sensors (TODO: Add microcontroller and RF)
    """
    # getting all valid inputs for tmp
    
    num_averages_options = [0, 8, 32, 64]
    conv_cycle_time_options = [0.0155, 0.125, 0.25, 0.5, 1, 4, 8, 16] 
    mode_options = ["CONTINUOUS_CONVERSION", "ONE_SHOT", "SHUTDOWN"]
    valid_TMP = []

    for averages in num_averages_options:
        if averages == 0:
            time_options_trunc = conv_cycle_time_options[0:]
            cc_configs = [("CONTINUOUS_CONVERSION", 0, time) for time in time_options_trunc]
            valid_TMP += cc_configs
        elif averages == 8:
            time_options_trunc = conv_cycle_time_options[1:]
            cc_configs = [("CONTINUOUS_CONVERSION", 8, time) for time in time_options_trunc]
            valid_TMP += cc_configs
        elif averages == 32:
            time_options_trunc = conv_cycle_time_options[3:]
            cc_configs = [("CONTINUOUS_CONVERSION", 32, time) for time in time_options_trunc]
            valid_TMP += cc_configs
        elif averages == 64:
            time_options_trunc = conv_cycle_time_options[4:]
            cc_configs = [("CONTINUOUS_CONVERSION", 64, time) for time in time_options_trunc]
            valid_TMP += cc_configs

    os_configs = [("ONE_SHOT",0,0.0155),("ONE_SHOT",8,0.0155),("ONE_SHOT",32,0.0155),("ONE_SHOT",64,0.0155)]
    valid_TMP += os_configs + [('SHUTDOWN',0,0)]
    
    # getting all valid inputs for magnetometer
    num_averages_options = [1, 2, 4, 8, 16]
    freq_options = [10, 20, 100, 1000]
    mode_options = ["CONTINUOUS", "SINGLE", "POWER_DOWN"]
    valid_MAG = []

    for averages in num_averages_options:
        if averages == 1:
            freq_options_trunc = freq_options[0:]
            configs = [("CONTINUOUS", freq, 1) for freq in freq_options_trunc]
            valid_MAG += configs
        elif averages == 2:
            freq_options_trunc = freq_options[0:]
            configs = [("CONTINUOUS", freq, 2) for freq in freq_options_trunc]
            valid_MAG += configs
        elif averages == 4:
            freq_options_trunc = freq_options[:3]
            configs = [("CONTINUOUS", freq, 4) for freq in freq_options_trunc]
            valid_MAG += configs
        elif averages == 8:
            freq_options_trunc = freq_options[:3]
            configs = [("CONTINUOUS", freq, 8) for freq in freq_options_trunc]
            valid_MAG += configs
        elif averages == 16:
            freq_options_trunc = freq_options[:3]
            configs = [("CONTINUOUS", freq, 16) for freq in freq_options_trunc]
            valid_MAG += configs

    s_configs = [("SINGLE",1000,1),("SINGLE",1000,2),("SINGLE",1000,4),("SINGLE",1000,8),("SINGLE",1000,16)]
    valid_MAG += s_configs + [('POWER_DOWN',0,0)]

    # getting all valid inputs for acc
    low_power_wakeup = [0, 1.25, 5, 20, 40]
    digital_low_pass = ["000", "001", "010", "011", "100", "101", "110", "111" ]
    mode_options = ["ACCELEROMETER", "ACCELEROMETER_LOW_POWER", "GYROSCOPE", "GYROSCOPE_DMP", "ACCELEROMETER_AND_GYROSCOPE", "ACCELEROMETER_AND_GYROSCOPE_DMP", "SHUTDOWN"]
    sample_rate_divisor = []
    valid_ACC = []

    for lpw in low_power_wakeup:
        if lpw == 1.25:
            dlp_options_trunc = digital_low_pass[1:7]
            lpw_configs = [("ACCELEROMETER_LOW_POWER", 1.25, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
            valid_ACC += lpw_configs
        elif lpw == 5:
            dlp_options_trunc = digital_low_pass[1:7]
            lpw_configs = [("ACCELEROMETER_LOW_POWER", 5, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
            valid_ACC += lpw_configs
        elif lpw == 20:
            dlp_options_trunc = digital_low_pass[1:7]
            lpw_configs = [("ACCELEROMETER_LOW_POWER", 20, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
            valid_ACC += lpw_configs
        elif lpw == 40:
            dlp_options_trunc = digital_low_pass[1:7]
            lpw_configs = [("ACCELEROMETER_LOW_POWER", 40, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
            valid_ACC += lpw_configs
    dlp_options_trunc = digital_low_pass[1:7]
    accelerometer_config = [("ACCELEROMETER",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
    gyroscope_config = [("GYROSCOPE",0, dlp, srd) for dlp in digital_low_pass for srd in range(256)]
    gyroscope_dmp_config = [("GYROSCOPE_DMP",0, dlp, srd) for dlp in digital_low_pass for srd in range(256)]
    accelerometer_gyroscope_config = [("ACCELEROMETER_AND_GYROSCOPE",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
    accelerometer_gyroscope_dmp_config = [("ACCELEROMETER_AND_GYROSCOPE_DMP",0, dlp, srd) for dlp in dlp_options_trunc for srd in range(256)]
    valid_ACC += accelerometer_config + gyroscope_config + gyroscope_dmp_config + accelerometer_gyroscope_config +accelerometer_gyroscope_dmp_config + [('SHUTDOWN',0,"000", srd) for srd in range(256)]

    valid_TP = [("TP_OFF"),("TP_ON")]
    valid_CAP = [("CAP_OFF"),("CAP_ON")]

    return valid_TMP, valid_ACC, valid_MAG, valid_TP, valid_CAP
    
def plot_power_separate(time_list, power_list): 
    """
      Plots seperate power usage plots for sensors

      Parameters
      ----------
        time_list: np array
        power_list: np array

      Returns
      -------
        None
    """
    fig, axs = plt.subplots(1,5, figsize=(8,2))
    labels = ["Accelerometer Sensor", "Magnetometer Sensor", "Thermopile Sensor", "Temperature Sensor", "Capacitive Sensor", "Microcontroller", "Total"]
    
    for i, power in enumerate(power_list[0:6]):#have to split array because last value is total_power
        axs[i].plot(time_list[i], power, label = labels[i])
        axs[i].set_ylim([0, 70]) # normalize y limits
        axs[i].fill_between(time_list[i], power, where=((time_list[i] >= 0) & (time_list[i] <= len(power))), color='orange')
        axs[i].set_title(labels[i], fontsize = 8)
        axs[i].grid()

    fig.supxlabel('Time (s)')
    fig.supylabel('Power (mW)')
    plt.tight_layout();
    
    plt.figure(figsize=(10,5))
    plt.ion()
    plt.plot(time_list[0], power_list[-1], label = "Total Power (mW)")#last value of power_list must be total_power.
    plt.ylim([0, 70]) # normalize y limits
    plt.fill_between(time_list[0], power_list[-1], where=((power_list[-1] >= 0) & (power_list[-1] <= len(power))), color='orange')
    plt.legend()
    plt.grid()
    plt.ylabel("Power (mW)")
    plt.xlabel("Time (s)")
    plt.title("Power (mW) vs Time All Sensors")
    
def plot_rf_data(time_list: np.array, data_list: np.array): 
    """
    Plot each line in data_list using time_list.
    
    Parameters
        time_list (numpy array): list of time vectors returned from run_sim for each sensor.
        data_list (numpy array): list of data vectors returned from run_sim for each sensor.

    Returns
        None
    """
    
    label_reference = {
        0:"Min. Data", 1:"Microcontroller", 2:"RF", 3:"Total Data"
    }
    
    for i in range(0,4):
        plt.plot(time_list[i],data_list[i],label=label_reference[i])

    datarate_limit = 1000
    max_datarate = np.ones(len(data_list[0]))
    for i in range(0,len(max_datarate)):
        max_datarate[i] = (i * datarate_limit) + datarate_limit
    plt.plot(time_list[0],max_datarate,label="Max. Datarate")
    plt.grid(visible=True)
    plt.xlabel("Time (s)",fontsize=16)
    plt.ylabel("Data (Bytes)",fontsize=16)
    plt.title("Data vs Time for all Components",fontsize=16)
    plt.ion()
    plt.tight_layout()
    plt.legend()
    
    timePossible = np.where(data_list[3]>max_datarate,time_list[0],None)
    for i in range(0,len(max_datarate)):
        if(timePossible[i]!=None and i!=0):
            print("ERROR! At least one of your configurations exceeds the maximum datarate at " + str(i) + " seconds.")
            return "ERROR"
    return "Configurations meet datarate requirements"