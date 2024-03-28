import tensorflow as tf
import librosa.display
import numpy as np
import librosa
import math


def waveform_to_spectrogram(waveform: np.ndarray, frame_length: int, frame_step: int) -> np.ndarray:
    """
    Convert a waveform into its spectrogram representation.

    Params:
        waveform (np.ndarray): The input waveform.
        frame_length (int): The length of each frame in samples.
        frame_step (int): The number of samples to step between frames.

    Returns:
        np.ndarray: The spectrogram representation of the input waveform.
    """
    spectrogram = tf.signal.stft(waveform, frame_length, frame_step)

    spectrogram = tf.abs(spectrogram)
    spectrogram = spectrogram[..., tf.newaxis]
    spectrogram = spectrogram.numpy()

    return spectrogram

def update_waveform_bpm(waveform: np.ndarray, from_bpm: int, to_bpm: int) -> np.ndarray:
    """
    Update a waveform's BPM by stretching it to match the target BPM.

    Params:
        waveform (np.ndarray): The waveform to be updated.
        from_bpm (int): The original BPM (beats per minute) of the waveform.
        to_bpm (int): The target BPM (beats per minute) to which the waveform will be stretched.

    Returns:
        np.ndarray: The updated waveform with the tempo adjusted to match the target BPM.
    """
    return librosa.effects.time_stretch(waveform, rate=to_bpm / from_bpm)


def get_beats(bpm: int, offset: int, divisor: float, max_len_ms: int) -> list:
    """
    Calculate beats within a specified time frame.

    Parameters:
    - bpm (int): Beats per minute.
    - offset (int): Offset in milliseconds.
    - divisor (float): Time divisor as a fraction (e.g., 1/4).
    - max_len_ms (int): Maximum length in milliseconds.

    Returns:
    - list: List of beat timestamps in milliseconds.
    """
    mini_beats = [offset]
    in_between = 60 / bpm * 1000 * divisor
    while mini_beats[-1] < max_len_ms:
        mini_beats.append(round(mini_beats[-1] + in_between, 10))
    return [math.floor(b) for b in mini_beats], in_between
