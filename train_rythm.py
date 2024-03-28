import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Get rid of tenserflow warnings

from keras.preprocessing.sequence import pad_sequences
from utils import audio, osu, data_loader
import librosa
import numpy as np
import math

# Settings
training_path     = "./trainmaps"    # Training data path
signature         = 1/4              # How many ticks in a beat
normalized_bpm    = 180              # Like an average BPM for normalization

frame_length      = 256              # For spectrogram generation
frame_step        = 128              # For spectrogram generation
audio_max_len     = 0                # 0 = auto; 1000 = 1000ms

events = {
    "empty": 0,
    "circle": 1,
    "slider": 2,
    "spinner": 3,
    "hold": 4,
    "release": 5,
}



# Loading paths for training data
audios, maps = data_loader.load_training_data_paths(training_path)
srs = [0] * len(maps)

# Parse osu files 
print("\nParsing osu maps")
for i, osuf_path in enumerate(maps):
    pars_osu = osu.parse_osu_file(osuf_path)
    timings = [t for t in pars_osu.timingpoints if t[6] == 1]    # Get all uninhired points
    if len(set([t[1] for t in timings])) > 1: 
        maps[i] = None
        audios[i] = None
        srs[i] = None
        print(f"Warning: Removing {osuf_path}. BPM Variation: " + " -> ".join([str(osu.timing_to_bpm(i[1])) for i in timings]))
        continue
    print(f"{osuf_path}")
    
    pars_osu.general["bpm"] = osu.timing_to_bpm(timings[0][1])         # Calculate the map BPM
    pars_osu.general["norm_bpm"] = normalized_bpm

    pars_osu.timingpoints, pars_osu.hitobjects = osu.normalise_bpm(
        pars_osu.timingpoints, 
        pars_osu.hitobjects, 
        from_bpm = pars_osu.general["bpm"], 
        to_bpm   = pars_osu.general["norm_bpm"]
    )

    pars_osu.general["offset"] = timings[0][0]

    pars_osu.hitobjects = osu.replace_slider_length_with_time(pars_osu)

    maps[i] = pars_osu
    srs[i] = 0
    


# Remove the empty slots
maps = [i for i in maps if i]
audios = [i for i in audios if i]
srs = [i for i in srs if i != None]


# Extra check... just in case
if len(maps) != len(audios) :
    raise Exception(f"The list length of maps and audios are not equal. maps: {len(maps)}, audios: {len(audios)}")


# Convert audio files path to spectrograms
print("\nPreparing audio and converting audio bpm")
for i, audiof_path in enumerate(audios):
    waveform, sr = librosa.load(audiof_path)
    audio_bpm = maps[i].general["bpm"]
    print(f"{audio_bpm} -> {normalized_bpm}")
    norm_waveform = audio.update_waveform_bpm(waveform, audio_bpm, normalized_bpm)
    
    audios[i] = norm_waveform
    srs[i] = sr

for i, osu_map in enumerate(maps):
    mini_beats = [osu_map.general["offset"]]
    in_between = 60 / normalized_bpm * 1000 * signature
    while mini_beats[-1] < len(audios[i]) / srs[i] * 1000:
        mini_beats.append(round(mini_beats[-1] + in_between, 10))
    if i == 0:
        print(mini_beats)
        found = 0
        notFound = 0
        for ho in osu_map.hitobjects:
            if ho[2] in [math.floor(i) for i in mini_beats]:
                print(f"Found: {ho[2]}")
                found += 1
            else:
                print(f"Not Found: {ho[2]}")
                notFound += 1
        print(found, notFound)

    






# # Pad the waveforms and convert into spectrograms
# audio_max_len = audio_max_len or max(len(waveform) for waveform in audios)
# for i, waveform in enumerate(audios):
#     padded_waveform = np.pad(waveform[:audio_max_len], (0, max(0, audio_max_len - len(waveform))), mode='constant')
#     audios[i] = audio.waveform_to_spectrogram(padded_waveform, frame_length, frame_step)

# print(np.array(audios).shape)