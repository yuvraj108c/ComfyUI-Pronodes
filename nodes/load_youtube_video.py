from yt_dlp import YoutubeDL
import os, subprocess
import torch
import numpy as np
from .utils import clean_string, cv_frame_generator, get_audio, lazy_eval

class LoadYoutubeVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "url": ("STRING",{"default":"https://www.youtube.com/shorts/esdmCU88tdc"}),
                "frame_load_cap": ("INT",{
                    "default": 0,
                    "step":1,
                    "display": "number"
                }),
                "skip_first_frames": ("INT",{
                    "default": 0,
                    "step":1,
                    "display": "number"
                }),
                "select_every_nth": ("INT",{
                    "default": 1,
                    "step":1,
                    "display": "number"
                }),
                "output_dir": ("STRING",{"default":"output/youtube"}),
            }
        }

    RETURN_TYPES = ("IMAGE","VHS_AUDIO","INT",)
    RETURN_NAMES = ("IMAGE","audio","calculated_frame_rate",)
    FUNCTION = "main"
    CATEGORY = "pronodes"

    def main(self,url,output_dir, frame_load_cap,skip_first_frames,select_every_nth):
        try:
            os.makedirs(output_dir,exist_ok=True)

            # get video title
            with YoutubeDL({"quiet":True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = clean_string(info_dict.get('title', None))

            # download video
            video_save_path = os.path.join(output_dir,video_title) + ".mp4"
            if not os.path.isfile(video_save_path):
                subprocess.run(f"yt-dlp -q -f 22 {url} -o '{video_save_path}'", shell=True)
                print(f"[PRONODES] Downloaded video to {video_save_path}")
            else:
                print(f"[PRONODES] '{video_title}.mp4' exists.. skipping download")

            # load video frames
            gen = cv_frame_generator(video_save_path, frame_load_cap, skip_first_frames, select_every_nth)
            (width, height, target_frame_time, frame_rate) = next(gen)
            width = int(width)
            height = int(height)
            calculated_frame_rate = int(frame_rate/select_every_nth)
            
            # Some minor wizardry to eliminate a copy and reduce max memory by a factor of ~2
            images = torch.from_numpy(np.fromiter(gen, np.dtype((np.float32, (height, width, 3)))))
            if len(images) == 0:
                raise Exception("[PRONODES] No frames generated")


            #Setup lambda for lazy audio capture
            audio = lambda : get_audio(video_save_path, skip_first_frames * target_frame_time,
                                    frame_load_cap*target_frame_time*select_every_nth)
            return (images, lazy_eval(audio),calculated_frame_rate)

        except Exception as e:
            raise e

