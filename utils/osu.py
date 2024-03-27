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