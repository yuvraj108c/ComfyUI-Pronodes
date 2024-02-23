import imageio
import re

def get_video_metadata(video_path):
    reader = imageio.get_reader(video_path)
    return reader.get_meta_data()

def clean_string(input_string):
    return re.sub("[^A-Za-z]", "", input_string)