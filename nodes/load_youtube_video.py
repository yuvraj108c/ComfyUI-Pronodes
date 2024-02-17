from yt_dlp import YoutubeDL
import os, subprocess
from .utils import clean_string, get_video_metadata

class LoadYoutubeVideoNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "url": ("STRING",{"default":""}),
            }
        }

    RETURN_TYPES = ("STRING","INT",)
    RETURN_NAMES = ("video_path","frame_rate",)
    FUNCTION = "main"
    CATEGORY = "Pronodes"
    OUTPUT_NODE=True

    def main(self,url):
        try:
            subfolder = "youtube"
            output_dir = f"output/{subfolder}"
            os.makedirs(output_dir,exist_ok=True)

            # get video title
            with YoutubeDL({"quiet":True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = clean_string(info_dict.get('title', None))

            # download video if not exists
            video_save_path = os.path.join(output_dir,video_title) + ".mp4"
            if not os.path.isfile(video_save_path):
                subprocess.run(f"yt-dlp -q -f 22 {url} -o '{video_save_path}'", shell=True)
                print(f"PRONODES] Downloaded video to {video_save_path}")
            else:
                print(f"[PRONODES] '{video_title}.mp4' exists.. skipping download")

            metadata = get_video_metadata(video_save_path)
            frame_rate = int(metadata["fps"])
            width,height = metadata["source_size"]
            
            previews = [
                {
                    "filename":f"{video_title}.mp4",
                    "subfolder":subfolder,
                    "format":"video/h264-mp4",
                    "type":"output",
                }
            ]
            data = [
                {
                    "frame_rate":frame_rate,
                    "resolution":f"{width} x {height}",
                    "video_title":video_title
                }
            ] 
            return {"ui": {"previews":previews,"data":data},"result": (video_save_path,frame_rate,)}


        except Exception as e:
            raise e

