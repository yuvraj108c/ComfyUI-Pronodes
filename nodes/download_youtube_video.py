from yt_dlp import YoutubeDL
import os, subprocess
from .utils import clean_string, get_video_fps

class DownloadYoutubeVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "url": ("STRING",{"default":""}),
                "output_dir": ("STRING",{"default":"output/youtube"}),
            }
        }

    RETURN_TYPES = ("STRING","INT",)
    RETURN_NAMES = ("video_path","frame_rate",)
    FUNCTION = "main"
    CATEGORY = "Pronodes"

    def main(self,url,output_dir):
        try:
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

            frame_rate = int(get_video_fps(video_save_path))
            return (video_save_path,frame_rate,)

        except Exception as e:
            raise e

