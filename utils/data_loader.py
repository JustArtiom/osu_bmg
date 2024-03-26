import os

def load_training_data_paths(train_path: str) -> list: 
    """
    Load paths to training data.

    This function takes the path to the directory containing the training data 
    and returns a list of lists (2D array), where each inner list contains two strings:
    the path to an audio file and the path to its corresponding osu file.

    Args:
        train_path (str): The path to the directory containing the training data.

    Returns:
        list: A list of lists containing paths to audio file and their corresponding osu file
    """

    tdata_paths = []

    for folder in os.listdir(train_path):
        work_dir = os.path.join(train_path, folder)
        if not os.path.isdir(work_dir):
            print(f"Warning: Skipping Path {work_dir} because is not a directory")
            continue

        # Get the audio files
        audio_files = [f for f in os.listdir(work_dir)
                        if f.lower().endswith(".mp3") 
                        or f.lower().endswith(".wav")]
        # Get the osu files
        osu_files = [f for f in os.listdir(work_dir)
                        if f.lower().endswith(".osu")]

        if len(audio_files) == 0 or len(osu_files) == 0:
            print(f"Warning: Skipping Path {work_dir} because it doesnt have enough files")
            continue

        if len(audio_files) > 1:
            print(f"Warning: Skipping Path {work_dir} because it has more than one audio file")
            continue
        else: audio_file = audio_files[0]

        for osu_file in osu_files:
            tdata_paths.append([
                os.path.join(work_dir, audio_file), 
                os.path.join(work_dir, osu_file)
            ])

    return tdata_paths
