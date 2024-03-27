from utils import audio, osu, data_loader
import librosa

def test_loading_training_paths(): 
    train_pack = data_loader.load_training_data_paths("trainmaps")
    print(train_pack)

# test_loading_training_paths()

def test_spectrogram_generation():
    example_path = "trainmaps/template/audio.mp3"
    from_bpm = 184
    to_bpm = 180

    y, sr = librosa.load(example_path)
    waveform = audio.update_waveform_bpm(y, from_bpm, to_bpm)
    spectrogram = audio.waveform_to_spectrogram(waveform, 256, 128)

    print(spectrogram.shape)

# test_spectrogram_generation()

def tets_osu_file_parser():
    example_path = "trainmaps/template/template.osu"

    parsed = osu.parse_osu_file(example_path)
    print(parsed.hitobjects)

# tets_osu_file_parser()
