import imageio

def get_video_fps(video_path):
    reader = imageio.get_reader(video_path)
    fps = reader.get_meta_data()['fps']
    return fps

def clean_string(input_string):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    cleaned_string = ''.join(c if c not in invalid_chars else '_' for c in input_string)
    cleaned_string = cleaned_string.strip(" .")
    return cleaned_string