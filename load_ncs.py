#%% DEPENDENCIES
from neo.io import NeuralynxIO

#%% LOAD
file_path = "/home/adam/workspace/ucl/combinato_tutorial/"
file_name = "CSC29.ncs"
reader = NeuralynxIO(filename=file_name, dirname=file_path)
block = reader.read_block()

#%% EXTRACT
# Access continuous signals
signal = block.segments[0].analogsignals[0]
print(signal.shape)
print(signal.sampling_rate)