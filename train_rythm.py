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
audios, maps = data_loader.load_training_data_paths(training_path)


# Parse osu files 
print("\nParsing osu maps")
for i, osuf_path in enumerate(maps):
    pars_osu = osu.parse_osu_file(osuf_path)
    timings = [t[1] for t in pars_osu.timingpoints if t[6] == 1]    # Get all uninhired points
    if len(set(timings)) > 1: 
        maps[i] = None
        audios[i] = None
        print(f"Warning: Removing {osuf_path}. BPM Variation: " + " -> ".join([str(osu.timing_to_bpm(i)) for i in timings]))
        continue
    print(f"{osuf_path}")
    
    pars_osu.general["bpm"] = osu.timing_to_bpm(timings[0])         # Calculate the map BPM
    pars_osu.general["norm_bpm"] = normalized_bpm

    pars_osu.timingpoints, pars_osu.hitobjects = osu.normalise_bpm(
        pars_osu.timingpoints, 
        pars_osu.hitobjects, 
        from_bpm = pars_osu.general["bpm"], 
        to_bpm   = pars_osu.general["norm_bpm"]
    )

    pars_osu.hitobjects = osu.replace_slider_length_with_time(pars_osu)

    maps[i] = pars_osu
    


# Remove the empty slots
maps = [i for i in maps if i]
audios = [i for i in audios if i]


# Extra check... just in case
if len(maps) != len(audios):
    raise Exception(f"The list length of maps and audios are not equal. maps: {len(maps)}, audios: {len(audios)}")


# Convert audio files path to spectrograms
print("\nPreparing audio and converting audio bpm")
for i, audiof_path in enumerate(audios):
    waveform, sr = librosa.load(audiof_path)
    audio_bpm = maps[i].general["bpm"]
    print(f"{audio_bpm} -> {normalized_bpm}")
    norm_waveform = audio.update_waveform_bpm(waveform, audio_bpm, normalized_bpm)
    specrogram = audio.waveform_to_spectrogram(norm_waveform, frame_length, frame_step)

    audios[i] = (specrogram, sr)
    
