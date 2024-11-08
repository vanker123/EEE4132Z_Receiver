import numpy as np
import matplotlib.pyplot as plt


#Functions 

def sky_source(freq, amp, phase, t):
    return amp * np.sin(2 * np.pi * freq * t + phase)

def receiver(t, delay1, delay2, source1, source2):
    signal1 = source1(t - delay1) 
    signal2 = source2(t - delay2)
    RFI = np.random.normal(0, 0.1, len(t))
    return signal1+ signal2 + RFI

# 4 bit ADC
def adc(signal, adc_levels):
    min_val = -1 
    max_val = 1   
    step = (max_val - min_val) / (adc_levels-1) 
    ADC_out = np.round((signal - min_val) / step).astype(int)
    ADC_out = np.clip(ADC_out, 0, adc_levels - 1) 
    return ADC_out

# Convert ADC output to 4-bit binary and ensure all are exactly 4 bits
def adc_to_binary(adc_output):
    return np.array([format(val, '04b') for val in adc_output])  # Format as 4-bit binary, with leading zeros if necessary
#---------------------------------------------------------------------------------------------------------------------------------
sampling_rate = 1e6  #1 MHz sampling
adc_levels = 16  #4bit ADC

t = np.linspace(0, 1, int(sampling_rate), endpoint=False)

source1 = lambda t: sky_source(50e3, 1.0, 0, t)  # 50 kHz signal
source2 = lambda t: sky_source(100e3, 0.5, np.pi / 4, t)  # 100 kHz signal,0.5 DC amplification, phase shifted by 45 degrees


delays = [0.0, 5e-6, 10e-6, 15e-6]  # delay for each receiver, determiend by distance between source and receiver

receiver_signals = []
for i in range(4):#4 receivers, therefore 4 delays
    signal = receiver(t, i, i/2, source1, source2)
    receiver_signals.append(signal)

adc_signals_binary = []
for i, signal in enumerate(receiver_signals):
    adc_output = adc(signal, adc_levels)  #ADC QUantisation
    adc_binary = adc_to_binary(adc_output)  # convert int to 4 bit binary
    adc_signals_binary.append(adc_binary)

def write_mif_files(adc_signals_binary, samples_per_receiver):
    for i, adc_signal_binary in enumerate(adc_signals_binary):
        # Generate a unique filename for each receiver
        filename = f"adc_output_receiver55_{i+1}.mif"
        
        with open(filename, 'w') as mif_file:
            
            mif_file.write(f"WIDTH=4;\n")
            mif_file.write(f"DEPTH={samples_per_receiver};\n\n")
            mif_file.write(f"ADDRESS_RADIX=BIN;\n")
            mif_file.write(f"DATA_RADIX=BIN;\n\n")
            mif_file.write(f"CONTENT BEGIN\n")
            
            for address, data in enumerate(adc_signal_binary):
                mif_file.write(f"\t{address:020b} : {data};\n")
            
            mif_file.write(f"END;\n")

samples = len(adc_signals_binary[0])
write_mif_files(adc_signals_binary, samples)

