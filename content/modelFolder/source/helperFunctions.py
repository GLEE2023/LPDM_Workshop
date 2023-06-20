import matplotlib.pyplot as plt
import numpy as np
import random

def generate_active_list(total_time: float, modelist: list) -> list:
    """
    Returns list similar to the form of active_times, but based off of modedict.
    active_times: [(int(start1), int(end1), "mode1"), (int(start2), int(end2), "mode2")]
    
    Example:
        modes = {"low_power_wakeup_5": 10, "accelerometer_only": 20, "gyroscope_accelerometer_DMP":30}
        #low_power_wakeup_5 for 10 seconds, accelerometer_only for 20 seconds, and so on.
        #10 + 20 + 30 = 60, so the period for this configuration is 60 seconds.


        active_times_list = generate_active_list(total_time = 600, modedict = modes)
        #for 600 seconds, repeat the configuration set in modedict.
    

    args:
        total_time (float): total active time of the sensor, ie 10 seconds or 10 hours.
        modelist (list): numpy array describing scheduling period based off of modedict. See example.
        modedict form: {string(mode1):int(duration1), string(mode2):int(duration2), ...}

    returns:
        final_arr, list of active times of each mode
    """
    #modedict has different modes and times that add up to a single cycle.
    #for accelerometer:
    #modedict = {"gyroscope_accelerometer_DMP":15, "accelerometer_only":15,"low_power_wakeup_5":40}
    #total period is 70 seconds (15+15+40)

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
    The last value of data_list must be total_data, and the last value of time_list
    can be any time vector returned from runSim.
    
    args:
        time_list (nparray): list of time vectors returned from runSim for each sensor.
        data_list (nparray): list of data vectors returned from runSim for each sensor.

    returns:
        nothing
    """
    
    label_reference = {
        0:"Accelerometer Sensor", 1:"Magnetometer Sensor", 2:"Thermopile Sensor", 
        3:"Temperature Sensor", 4:"Total data"
    }

    plt.figure(figsize=(10,4))
    #plot each line using zip().
    for index, value in enumerate(zip(data_list, time_list)):
        plt.plot(value[1], value[0], label = label_reference[index])

    #plot modification.
    plt.grid(visible=True)
    plt.xlabel("Time (s)",fontsize=16)
    plt.ylabel("Data",fontsize=16)
    plt.title("Data vs Time All Sensors (Bytes)",fontsize=16)
    plt.ion()
    plt.tight_layout()
    plt.legend();
    
def valid():
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
    lowpass = [str(s) for s in np.arange(0,8,1)] # digital low pass filter
    sample_rate = [str(s) for s in np.arange(0,256,1)] # 0-250 sample rate
    modes = ["low_power_wakeup_1.25", "low_power_wakeup_5", "low_power_wakeup_20", "low_power_wakeup_40", "accelerometer_only", "gyroscope_only", "gyroscope_accelerometer"]
    valid_ACC = [mode + "_" + p + "_" + sr for mode in modes for p in lowpass for sr in sample_rate] + ["sleep"]
    
    # # run this once to populate txt files with possible inputs
    # with open('sensorParams/accelerometerParams.txt', 'w') as f:
    #     for line in valid_ACC:
    #         f.write(line + "\n")
    # with open('sensorParams/magnetometerParams.txt', 'w') as f:
    #     for line in validMAG:
    #         f.write(line + "\n")
    # with open('sensorParams/tmpSensorParams.txt', 'w') as f:
    #     for line in validTMP:
    #         f.write(line + "\n")

    return valid_TMP, valid_ACC, valid_MAG
    
def validate_configs(configurations):
    configurations = np.array(configurations)
    tmp_modes = configurations[:,0]
    acc_modes = configurations[:,1]
    mag_modes = configurations[:,2]

    valid_TMP, valid_ACC, valid_MAG = valid()
    valid_config = True

    for mode in tmp_modes:
        if mode not in valid_TMP:
            print("Invalid temperature mode {}".format(mode))
            print("* Read description of inputs again or see tmpSensorParams.txt in the sensorParams folder for a list of possible inputs for the tmp sensor.\n")
            valid_config = False
            
    for mode in acc_modes:
        if mode not in valid_ACC:
            print("Invalid accelerometer mode {}".format(mode))
            print("* See accelerometerParams.txt in the sensorParams folder for a list of possible inputs for the accelerometer.\n")
            valid_config = False

    for mode in mag_modes:
        if mode not in valid_MAG:
            print("Invalid magnetometer mode {}".format(mode))
            print("* See magnetometerParams.txt in the sensorParams folder for a list of possible inputs for the magnetometer.\n")
            valid_config = False

    return valid_config
# [acc_power, mag_power, tp_power, tmp_power, cap_power, mic_power, rf_power, total_pow]
def plot_power_separate(time_list, power_list): 
    # PLOT POWER
    fig, axs = plt.subplots(1,5, figsize=(8,2))
    labels = ["Accelerometer Sensor", "Magnetometer Sensor", "Thermopile Sensor", "Temperature Sensor", "Capacitive Sensor", "Microcontroller", "Total"]
    
    for i, power in enumerate(power_list[0:6]):#have to split array because last value is total_power
        axs[i].plot(time_list[i], power, label = labels[i])
        axs[i].set_ylim([0, 70]) # normalize y limits
        axs[i].fill_between(time_list[i], power, where=((time_list[i] >= 0) & (time_list[i] <= len(power))), color='orange')
        #axs[i].legend(fontsize=5)
        axs[i].set_title(labels[i], fontsize = 8)
        axs[i].grid()

    #axs[4].plot([0, time_list[0][-1]], [chip_pow, chip_pow], label = "AT Mega")
    #axs[4].set_ylim([0, 70]) # normalize y limits
    #axs[4].fill_between(time_list[0], chip_pow, where=((time_list[0] >= 0) & (time_list[0] <= len(power))), color='orange')
    #axs[5].legend(fontsize=5)
    #axs[4].set_title("AT Mega", fontsize = 8)
    #axs[4].grid()
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
    plt.title("Power (mW) vs Time All Sensors");