import imageio

def get_video_metadata(video_path):
    reader = imageio.get_reader(video_path)
    return reader.get_meta_data()

def clean_string(input_string):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    cleaned_string = ''.join(c if c not in invalid_chars else '_' for c in input_string)
    cleaned_string = cleaned_string.strip(" .")
    return cleaned_string