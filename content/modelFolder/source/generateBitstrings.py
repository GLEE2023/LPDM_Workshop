from source.MPU6000 import *
from source.CAP11NA import *
from source.BM1422 import *
from source.TMP117 import *
from source.TPIS1S1385 import *

def convert_int_to_binary(n):
    bin_n = bin(n)
    return str(bin_n)[2:]

def validate_configs(config_list, sampling_rates_list, duration_list):
    """
          Checks if all provided configurations are valid

          Parameters
          ----------
            config_list: nested list of configurations for TP, CAP, TMP, ACC, MAG sensors

          Returns
          -------
            True if a configuration is invalid, False otherwise
        """
    valid_TMP = TMP117.generate_valid_configs_tmp(TMP117)
    valid_ACC = MPU6000.generate_valid_configs_acc(MPU6000)
    valid_MAG = BM1422.generate_valid_configs_mag(BM1422)
    valid_TP = TPIS1S1385.generate_valid_configs_tp(TPIS1S1385)

    valid_CAP = [("CAP_ON"), ("CAP_OFF")]
    counter = 0
    for set_configs in config_list:
        counter+=1
        if set_configs[0] not in valid_TP:
            print('TP configuration ' + str(counter) + ' is invalid')
            return False
        if set_configs[1] not in valid_CAP:
            print('CAP configuration ' + str(counter) + ' is invalid')
            return False
        if set_configs[2] not in valid_TMP:
            print('TMP configuration ' + str(counter) + ' is invalid')
            return False
        if set_configs[3] not in valid_ACC:
            print('ACC configuration ' + str(counter) + ' is invalid')
            return False
        if set_configs[4] not in valid_MAG:
            print('MAG configuration ' + str(counter) + ' is invalid')
            return False
    counter = 0
    for sr in sampling_rates_list:
        counter+=1
        if sr[0] < 0.0005: 
            print('TP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[1] < 0.001: # Estimate
            print('TP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[2] < 0.0155: 
            print('TMP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        digital_low_pass = config_list[counter-1][3][2]
        sample_rate_divisor = config_list[counter-1][3][3]
        gyroscope_output_rate = 8000 if digital_low_pass == "000" or digital_low_pass == "111" else 1000
        active_conversion_time = 1/((gyroscope_output_rate*1000) / (1 + sample_rate_divisor)) #how fast measurements are written to
        active_conversion_time *= 1000 # overestimation
        if sr[3] < active_conversion_time:
            print('ACC sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[4] < 0.0005: 
            print('MAG sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
    counter = 0    
    for dr in duration_list:
        counter+=1
        if dr < 0:
            print('Duration ' + str(counter) + ' cannot be negative')
            return False
        if dr == 0:
            print('Warning: You have selected duration ' + str(counter) + ' to be 0. This configuration will be skipped over in code execution.')
        if dr < 10:
            print('Warning: You have selected duration ' + str(counter) + ' to be less than 10 seconds. Please consider choosing a longer duration to minimize downtime.')
        
    print('All configurations are valid')
    return True
    
def generate_bitstrings(config_list):
    """
      Creates bitstrings from a list of configurations

      Parameters
      ----------
        config_list: nested list of configurations for TP, CAP, TMP, ACC, MAG sensors

      Returns
      -------
        list of bitstrings
    """
    # Retrieve all possible configurations
    valid_TMP = TMP117.generate_valid_configs_tmp(TMP117)
    valid_ACC = MPU6000.generate_valid_configs_acc(MPU6000)
    valid_MAG = BM1422.generate_valid_configs_mag(BM1422)
    valid_TP = TPIS1S1385.generate_valid_configs_tp(TPIS1S1385)
    valid_CAP = [("CAP_ON"), ("CAP_OFF")]
    
    dict_tp = {}
    dict_cap = {}
    
    # Assign binary numbers to each possible configuration
    
    
    # TMP
    num_averages_options = [0, 8, 32, 64]
    dict_tmp_averages = {}
    conv_cycle_time_options = [0, 0.0155, 0.125, 0.25, 0.5, 1, 4, 8, 16] # 0 used only for SHUTDOWN
    dict_tmp_conv = {}
    mode_options = ["CONTINUOUS_CONVERSION", "ONE_SHOT", "SHUTDOWN"]
    dict_tmp_modes = {}
    
    counter = 0
    maxlength = len(convert_int_to_binary(len(num_averages_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in num_averages_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_tmp_averages[option] = bits
        
        counter+=1
        
    counter = 0
    maxlength = len(convert_int_to_binary(len(conv_cycle_time_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in conv_cycle_time_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_tmp_conv[option] = bits
        
        counter+=1
        
    counter = 0
    maxlength = len(convert_int_to_binary(len(mode_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in mode_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_tmp_modes[option] = bits
        
        counter+=1
    

        
    # MAG
    num_averages_options = [0, 1, 2, 4, 8, 16] # 0 only used for POWER_DOWN
    dict_mag_averages = {}
    freq_options = [0, 10, 20, 100, 1000] # 0 only used POWER_DOWN
    dict_mag_freq = {}
    mode_options = ["CONTINUOUS", "SINGLE", "POWER_DOWN"]
    dict_mag_modes = {}
    
    counter = 0
    maxlength = len(convert_int_to_binary(len(num_averages_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in num_averages_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_mag_averages[option] = bits
        
        counter+=1
        
    counter = 0
    maxlength = len(convert_int_to_binary(len(freq_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in freq_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_mag_freq[option] = bits
        
        counter+=1

    counter = 0
    maxlength = len(convert_int_to_binary(len(mode_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in mode_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_mag_modes[option] = bits
        
        counter+=1
    
    # ACC - TODO: Revise when sampling_rate_divisor becomes its own parameter
    low_power_wakeup = [0, 1.25, 5, 20, 40] # 0 used for all modes except ACCELEROMETER_LOW_POWER
    dict_acc_lowpower = {}
    digital_low_pass = ["000", "001", "010", "011", "100", "101", "110", "111" ]
    dict_acc_lowpass = {}
    sampling_rate_divisor = [i for i in range(256)]
    dict_acc_srd = {}
    mode_options = ["ACCELEROMETER", "ACCELEROMETER_LOW_POWER", "GYROSCOPE", "GYROSCOPE_DMP", "ACCELEROMETER_AND_GYROSCOPE", "ACCELEROMETER_AND_GYROSCOPE_DMP", "SHUTDOWN"]
    dict_acc_modes = {}
    
    counter = 0
    maxlength = len(convert_int_to_binary(len(low_power_wakeup)-1)) # Calculate length of longest binary string for parameter
    
    for option in low_power_wakeup:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_acc_lowpower[option] = bits
        
        counter+=1
    
    
    counter = 0
    maxlength = len(convert_int_to_binary(len(digital_low_pass)-1)) # Calculate length of longest binary string for parameter
    
    for option in digital_low_pass:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_acc_lowpass[option] = bits
        
        counter+=1
        
    counter = 0
    maxlength = len(convert_int_to_binary(len(sampling_rate_divisor)-1)) # Calculate length of longest binary string for parameter
    
    for option in sampling_rate_divisor:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_acc_srd[option] = bits
        
        counter+=1
        
    counter = 0
    maxlength = len(convert_int_to_binary(len(mode_options)-1)) # Calculate length of longest binary string for parameter
    
    for option in mode_options:
        bits = convert_int_to_binary(counter) # Find binary number for option
        
        for i in range(0,maxlength - len(bits)): # Append 0s to front so that all bitstrings are same length
            bits = "0" + bits
            
        dict_acc_modes[option] = bits
        
        counter+=1
    
    
    # Only two possible configs for these sensors, no need for complex bit assignments
    
    counter = 0
    for config in valid_TP:
        dict_tp[config] = convert_int_to_binary(counter)
        counter+=1
    counter = 0
    for config in valid_CAP:
        dict_cap[config] = convert_int_to_binary(counter)
        counter+=1
        
    # Create bitstrings
    bitstrings = []
    for config in config_list:
        bitstring = '0b'
        #bitstring+="|"
        bitstring+=dict_tp[config[0]] # Thermopile
        #bitstring+="|"
        bitstring+=dict_cap[config[1]] # Capacitive
        #bitstring+="|"
        
        bitstring+=dict_tmp_averages[config[2][1]] # Temperature
        #bitstring+="|"
        bitstring+=dict_tmp_conv[config[2][2]]
        #bitstring+="|"
        bitstring+=dict_tmp_modes[config[2][0]]
        #bitstring+="|"
              
        bitstring+=dict_acc_lowpower[config[3][1]]
        #bitstring+="|"
        bitstring+=dict_acc_lowpass[config[3][2]]
        #bitstring+="|"
        bitstring+=dict_acc_srd[config[3][3]]
        #bitstring+="|"
        bitstring+=dict_acc_modes[config[3][0]]
        #bitstring+="|"
        
        bitstring+=dict_mag_averages[config[4][2]] # Magnetometer
        #bitstring+="|"
        bitstring+=dict_mag_freq[config[4][1]]
        #bitstring+="|"
        bitstring+=dict_mag_modes[config[4][0]]
        #bitstring+="|"
        
        bitstrings.append(bitstring)
    
    return bitstrings

def divide_bitstring(): # Call to see how bitstring is divided up.
    """
      Prints format of a bitstring

      Parameters
      ----------
        None

      Returns
      -------
        None
    """
    print("Bitstring Format: 0b| TP Mode | CAP Mode | TMP No. Averages | TMP Conv. Cycle Time | TMP Mode | ACC Low Power | ACC Dig. Low Pass | ACC SRD | ACC Mode | Mag No. Averages | Mag Freq. | MAG Mode |")
    print("Bitstring Size: 0b| 1 bit | 1 bit | 2 bits | 4 bits | 2 bits | 3 bits | 3 bits | 8 bits | 3 bits | 3 bits | 3 bits | 2 bits |")
    
        
def generate_dataset(config_list, duration_list, sampling_rates_list, team_name, team_no):
    """
      Generates dataset of bitstrings, durations, and sampling rates, and writes dataset to file.

      Parameters
      ----------
        config_list: nested list of configurations for TP, CAP, TMP, ACC, MAG sensors
        duration_list: list of integers
        sampling_rates_list: nested list of floats
        team_name: string
        team_no: int

      Returns
      -------
        0 once complete
    """
    bitstrings = generate_bitstrings(config_list)
    file_name = str(team_no) + '_' + str(team_name) + '.txt'
    f = open("outputs/" + file_name, 'w+')  # create file if doesn't exists otherwise open in overwrite mode
    f.write("team_no: " + str(team_no) + "\n")
    f.write("team_name: " + str(team_name) + "\n")
    f.write("Bitstrings: {")
    for i in range(0,len(bitstrings)-1):
        f.write(bitstrings[i])
        f.write(",")
    f.write(bitstrings[-1])
    f.write("}\n")
    f.write("Durations: {")
    for i in range(0,len(bitstrings)-1):
        f.write(str(duration_list[i]))
        f.write(",")
    f.write(str(duration_list[-1]))
    f.write("}\n")
    f.write("Sampling Rates: {")
    for i in range(0,len(bitstrings)-1):
        f.write("{")
        for d in range(0,4):
            f.write(str(float(sampling_rates_list[i][d])))
            f.write(",")
        f.write(str(float(sampling_rates_list[i][4])) + "},")
    f.write("{")
    for d in range(0,4):
        f.write(str(float(sampling_rates_list[-1][d])))
        f.write(",")
    f.write(str(float(sampling_rates_list[-1][4])) + "}")
    f.write("}\n")
    f.close()
    f = open("outputs/" + file_name, 'r') 
    print("Your configuration information is located at outputs/" + str(file_name) + ". Check the directory tree on the left side of this screen to verify that it is there in the outputs folder.")
    print(f.read())
    return 0