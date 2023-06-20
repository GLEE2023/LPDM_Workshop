from array import array
from source.MPU6000 import *
from source.CAP11NA import *
from source.BM1422 import *
from source.TMP117 import *
from source.TPIS1385 import *

def validate_configs(config_list):
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
    valid_ACC = MPU6000.generate_valid_configs_acc(MPU6000)
    valid_MAG = BM1422.generate_valid_configs_mag(BM1422)
    valid_TP = TPIS1385.generate_valid_configs_tp(TPIS1385)
    valid_CAP = [("CAP_ON"), ("CAP_OFF")]
    counter = 0
    for set_configs in config_list:
        counter+=1
        if set_configs[0] not in valid_TP:
            print('TP Configuration ' + counter + ' is invalid')
            return False
        if set_configs[1] not in valid_CAP:
            print('CAP Configuration ' + counter + ' is invalid')
            return False
        if set_configs[2] not in valid_CAP:
            print('TMP Configuration ' + counter + ' is invalid')
            return False
        if set_configs[3] not in valid_CAP:
            print('ACC Configuration ' + counter + ' is invalid')
            return False
        if set_configs[4] not in valid_CAP:
            print('MAG Configuration ' + counter + ' is invalid')
            return False
    print('All configurations are valid')
    return True
    
def generate_bitstrings(config_list):
    pass
        
    

def generateBitsTMP117(mode: str) -> str:  # TMP - 6 bits to encode 48 different configurations
    possTimes = {'0.0155': "000", '0.125': "001", '0.25': "010", '0.5': "011", '1': "100", '4': "101", '8': "110", '16': "111"}
    possAveraging = {'0': "00", '8': "01", '32': "10", '64': "11"}
    possModes = {"OS": "10", "CC": "00", "OFF": "01"}
    # "CC_64_1" : 0010011
    # "OS_8_0" : 1001000, mode, conv bits, averaging

    # do error check

    arr = mode.split("_")
    mode = arr[0]
    averages = arr[1]
    convTime = arr[2]

    if mode == "OFF": 
        return (possModes[mode] + "00000")
    else:
        string = possModes[mode] + possTimes[convTime] + possAveraging[averages]
        return string

def generateBitsMPU6050(mode: str) -> str:
    """
        modelist must be a numpy array. returns a list of integers representing the configuration bits.
    """
    bitmodedict = {
        "sleep":"0000","low_power_wakeup_1.25": "0001", "low_power_wakeup_5": "0010", "low_power_wakeup_20": "0011", 
        "low_power_wakeup_40": "0100", "accelerometer_only": "0101", "gyroscope_only": "0110",
        "gyroscope_accelerometer": "0111"
    }
    
    # bitstring is digital low pass (3 bit), then sample rate divisor (8 bits), then mode (4 bits) - 15 bits
    if mode != "sleep":
        low_pass = format(int(mode.split("_")[-2]), '03b')
        sample_rate = format(int(mode.split("_")[-1]), '08b')
        mode = bitmodedict['_'.join(mode.split("_")[0:-2])]
    else:
        low_pass = "000"
        sample_rate = "00000000"
        mode = "0000"
    string = low_pass + sample_rate + mode
    
    return string

# def generateBitsTP(mode):
#     bitmodedict = {"TP_only": "1","TP_off": "0"}
#     return int(bitmodedict[mode], 2)
# def generateBitsCAP11NA(mode):
#     bitmodedict = {"on": "1","off": "0"}
#     return int(bitmodedict[mode], 2)

def generateBitsBM1422(mode: str) -> str:
    # MSB bit mode, next bit CC or OS, last 2 bits are frequency
    modes = {"OS": "11", "CC": "10", "off": "00"} # standby is 0.00495
    frequency = {"10": "00", "20": "10", "100": "01", "1000": "11"} 

    if mode == "off": 
        return "0000"
    else:
        arr = mode.split("_")
        mode = arr[0]
        freq = arr[1]

        string = modes[mode] + frequency[freq]
        return string

def generateAllBitstrings(allConfigs: array) -> array: # takes in a 2d array
    configurationsInt = []
    for config in allConfigs:
        TMPint = generateBitsTMP117(config[0])
        ACCint= generateBitsMPU6050(config[1])
        MAGint = generateBitsBM1422(config[2])
        configurationsInt.append([TMPint, ACCint, MAGint, config[3]]) # an array of multiple bitstring arrays

    # bitstring order: tmp (7), acc (15), mag (4)
    allConfigsFullBitstrings = []
    for config in configurationsInt:
        config_bitstring = "0b" + config[0] + config[1] + config[2]
    #         if i == 0: # tmp sensor
    #             config_bitstring = 1 << 7 # need 1 as the MSB to keep the leading zeroes
    #             config_bitstring |= config[i] # masking to get tmp bits
    #         elif i == 1: # acc 
    #             config_bitstring <<= 15 # shifting to make space for acc bits
    #             config_bitstring |= config[i] # masking to get acc bits
    #         elif i == 2: # mag
    #             config_bitstring <<= 4 # shifting to make space for mag bits
    #             config_bitstring |= config[i] # masking to get mag bits
        allConfigsFullBitstrings.append((config_bitstring, config[3]))

        # for index in range(1,len(bits)):
        #     config_bitstring <<= bit_lengths[index] # shifting
        #     if bits[index] != None: # masking
        #         config_bitstring |= bits[index]
    return allConfigsFullBitstrings
    # for c in allConfigsFullBitstrings:
    #     print(len(c[0]))
    # return allConfigsFullBitstrings

def ArduinoConfigs(allConfigs, team_name):
    file_name = team_name + '.txt'
    f = open(file_name, 'w+')  # create file if doesn't exists otherwise open in overwrite mode
    allBitstrings = generateAllBitstrings(allConfigs)
    for index, config in enumerate(allBitstrings):
        bitstring = config[0]
        duration = config[1]
        f.write("#DEFINE CONFIGURATION_" + str(index+1) + " " + str(bitstring) + "\n")
        f.write("#DEFINE DURATION_" + str(index+1) + " " + str(duration)+ "\n\n")
    f.close()

def printArduinoConfigs(team_name):
    file_name = team_name + '.txt'
    f = open(file_name, 'r') 
    print(f.read())