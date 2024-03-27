import math

class OsuParsedData:
    def __init__(self):
        self.general = {}
        self.metadata = {}
        self.difficulty = {}
        self.timingpoints = []
        self.hitobjects = []


def try_to_nr(nr):
    if nr.isdigit():
            return int(nr)
    else:
        try:
            return float(nr)
        except Exception:
            return nr


def keyword_to_obj(str: str):
    key, value = str.split(":", 1)
    return key.strip(), try_to_nr(value.strip())


def parse_osu_file(osu_file_path: str) -> OsuParsedData:
    """
    Parse an osu! file into an object.

    This function reads an osu! file and parses its contents into an appropriate object
    representing the data in the file.

    Args:
        osu_file_path (str): The path to the osu! file to be parsed.

    Returns:
        OsuPrsedData: An object containing the parsed data from the osu! file.
    """

    parsed_data = OsuParsedData()
    current_header = ""

    with open(osu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("//"):
                continue

            if line.startswith('[') and line.endswith(']'):
                current_header = line.lower().strip('[]')
                continue

            if current_header in ["general", "metadata", "difficulty"]:
                key, value = keyword_to_obj(line)
                getattr(parsed_data, current_header)[key] = value
            elif current_header in ["timingpoints", "hitobjects"]:
                line_vals = []

                for val in line.strip().split(","):
                    val = try_to_nr(val)
                    line_vals.append(val)
                
                getattr(parsed_data, current_header).append(line_vals)

    return parsed_data


def timing_to_bpm(timing_value: float) -> float:
    """
    Convert timing value to BPM.

    Args:
        timing_value (float): The timing value in milliseconds.

    Returns:
        float: The corresponding BPM.
    """
    return round(60000 / timing_value, 2)


def get_latest_timing_point(timing_points: list, time: int, uninherited = 0):
    """
    Get the latest timing point before or equal to the given time.

    Args:
    timing_points (list): A list of timing points, each represented as a tuple (timestamp, value).
    time (float): The time to compare against.

    Returns:
    tuple or None: The latest timing point before or equal to the given time, or None if no such point exists.
    """
    # if uninherited = 0, beatLength represents slider velocity
    # if uninherited = 1, beatLength represents bpm update
    latest_timing_point = None
    for timing_point in [t for t in timing_points if t[6] == uninherited]:
        if timing_point[0] <= time:
            latest_timing_point = timing_point
        else:
            break
    return latest_timing_point


def replace_slider_length_with_time(parsed_osu: OsuParsedData) -> list:
    """
    Replace slider length with the time it takes to complete the slider.

    Args:
        parsed_osu (OsuParsedData): Parsed osu! data containing hit objects and timing points.

    Returns:
        list: Updated hit objects with slider length replaced by time to complete the slider.
    """

    updated_hit_objects = []
    slider_multiplier = parsed_osu.difficulty["SliderMultiplier"]
    
    for hit_object in parsed_osu.hitobjects:
        if len(hit_object) < 8: # Not a slider
            updated_hit_objects.append(hit_object)
            continue

        hit_time = int(hit_object[2])
        sv = get_latest_timing_point(parsed_osu.timingpoints, hit_time, uninherited=0)[1]
        sv = 1/abs(sv)*100
        beat_length = get_latest_timing_point(parsed_osu.timingpoints, hit_time, uninherited=1)[1]
        rollbacks = hit_object[6]
        length = hit_object[7]
        
        sliding_time = math.floor(length / (slider_multiplier * 100 * sv) * beat_length * rollbacks)

        hit_object[7] = sliding_time
        updated_hit_objects.append(hit_object)

    return updated_hit_objects

def normalise_bpm(timingpoints: list, hitobjects: list, from_bpm: float, to_bpm: float) -> tuple:
    """
    Normalize the BPM of the timing points and hit objects in an osu! beatmap.

    Args:
        timingpoints (list): List of timing points, each represented as a tuple (timestamp, beat_length, ...)
        hitobjects (list): List of hit objects in the beatmap.
        from_bpm (float): Current BPM of the beatmap.
        to_bpm (float): Target BPM to normalize to.

    Returns:
        tuple: A tuple containing the updated timing points and hit objects.
    """

    bpm_multiplier = from_bpm / to_bpm
    timingpoints_updated = []
    hitobjects_updated = []

    for tp in timingpoints:
        tp[0] = int(tp[0] * bpm_multiplier)
        if tp[6] == 1: # For uninhired points
            tp[1] = 1 / to_bpm * 1000 * 60 
        timingpoints_updated.append(tp)

    for ho in hitobjects:
        ho[2] = int(ho[2] * bpm_multiplier)
        hitobjects_updated.append(ho)

    return timingpoints_updated, hitobjects_updated




def are_hitobjects_in_divisor(parsed_osu: OsuParsedData) -> bool:


    return True