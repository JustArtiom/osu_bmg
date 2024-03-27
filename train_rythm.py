import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Get rid of tenserflow warnings

from utils import audio, osu, data_loader
import librosa

# Settings
training_path     = "./trainmaps"    # Training data path
signature         = 1/4              # How many ticks in a beat
normalized_bpm    = 180              # Like an average BPM for normalization

frame_length      = 256              # For spectrogram generation
frame_step        = 128              # For spectrogram generation


# Loading paths for training data
print("\nLoading Data set paths\n")
train_pack = data_loader.load_training_data_paths(training_path)
for train_paths in train_pack:
    for train_path in train_paths:
        print(train_path)
print("")


# Parse osu files 
for i, train_paths in enumerate(train_pack):
    train_pack[i][1] = osu.parse_osu_file(train_paths[1])


# Convert audio files path to spectrograms
print("Preparing audio and converting audio bpm")
for i, train_paths in enumerate(train_pack):
    waveform, sr = librosa.load(train_paths[0])
    timings = [t[1] for t in train_paths[1].timingpoints if t[6] == 1]
    audio_bpm = osu.timing_to_bpm(timings[0])
    print(f"{audio_bpm} -> {normalized_bpm}")
    norm_waveform = audio.update_waveform_bpm(waveform, audio_bpm, normalized_bpm)
    specrogram = audio.waveform_to_spectrogram(norm_waveform, frame_length, frame_step)

    train_pack[i][0] = (specrogram, sr,)
print("")