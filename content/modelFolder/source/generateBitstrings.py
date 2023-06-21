from source.MPU6000 import *
from source.CAP11NA import *
from source.BM1422 import *
from source.TMP117 import *
from source.TPIS1385 import *

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
            error: True if a configuration is invalid, False otherwise
        """
    valid_TMP = TMP117.generate_valid_configs_tmp(TMP117)
    valid_ACC = MPU6000.generate_valid_configs_tp(MPU6000) #TODO: Fix name
    valid_MAG = BM1422.generate_valid_configs_mag(BM1422)
    valid_TP = TPIS1385.generate_valid_configs_tp(TPIS1385)

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
        if sr[0] < 0.00001: # TODO: Adjust to actual hardware sampling rate
            print('TP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[1] < 0.00001: # TODO: Adjust to actual hardware sampling rate
            print('TP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[2] < 0.0155: 
            print('TMP sampling rate ' + str(counter) + ' (time between samples) is too small')
            return False
        if sr[3] < 0.00001: # TODO: Adjust to actual hardware sampling rate
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
    
    # Retrieve all possible configurations
    valid_TMP = TMP117.generate_valid_configs_tmp(TMP117)
    valid_ACC = MPU6000.generate_valid_configs_tp(MPU6000) # TODO: Fix function name
    valid_MAG = BM1422.generate_valid_configs_mag(BM1422)
    valid_TP = TPIS1385.generate_valid_configs_tp(TPIS1385)
    valid_CAP = [("CAP_ON"), ("CAP_OFF")]
    
    dict_tmp = {}
    dict_acc = {}
    dict_mag = {}
    dict_tp = {}
    dict_cap = {}
    
    # Assign binary numbers to each possible configuration
    
    counter = 0
    for config in valid_TMP:
        dict_tmp[config] = convert_int_to_binary(counter)
        counter+=1
    counter = 0
    for config in valid_ACC:
        dict_acc[config] = convert_int_to_binary(counter)
        counter+=1
    counter = 0
    for config in valid_MAG:
        dict_mag[config] = convert_int_to_binary(counter)
        counter+=1
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
        bitstring+=dict_tp[config[0]]
        bitstring+=dict_cap[config[1]]
        bitstring+=dict_tmp[config[2]]
        bitstring+=dict_acc[config[3]]
        bitstring+=dict_mag[config[4]]
        bitstrings.append(bitstring)
    
    return bitstrings
        
def generate_dataset(config_list, duration_list, sampling_rates_list, team_name, team_no):
    bitstrings = generate_bitstrings(config_list)
    file_name = str(team_no) + '_' + str(team_name) + '.txt'
    f = open("outputs/" + file_name, 'w+')  # create file if doesn't exists otherwise open in overwrite mode
    f.write("team_no: " + str(team_no) + "\n")
    f.write("team_name: " + str(team_name) + "\n")
    f.write("Bitstrings: {")
    for i in range(0,len(bitstrings)-1):
        f.write("\"")
        f.write(bitstrings[i])
        f.write("\",")
    f.write("\"")
    f.write(bitstrings[-1])
    f.write("\"")
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