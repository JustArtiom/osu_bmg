from utils import audio, data_loader
import tensorflow as tf

# Settings
training_path     = "./trainmaps"    # Training data path
signature         = 1/4              # How many ticks in a beat
normalized_bpm    = 180              # Like an average BPM for normalization


# Loading paths for training data
print("\nLoading Data set paths\n")
train_pack = data_loader.load_training_data_paths(training_path)
for train_paths in train_pack:
    for train_path in train_paths:
        print(train_path)
print("")











# example_path = "trainmaps/template/audio.mp3"
# from_bpm = 184
# to_bpm = 180

# y, sr = librosa.load(example_path)
# waveform = audio.update_waveform_bpm(y, from_bpm, to_bpm)
# spectrogram = audio.waveform_to_spectrogram(waveform, 256, 128)

# print(spectrogram.shape)