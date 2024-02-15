from yt_dlp import YoutubeDL
import os, subprocess
import torch
import numpy as np
import cv2

# Source: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite

def ffmpeg_suitability(path):
    try:
        version = subprocess.run([path, "-version"], check=True,
                                 capture_output=True).stdout.decode("utf-8")
    except:
        return 0
    score = 0
    #rough layout of the importance of various features
    simple_criterion = [("libvpx", 20),("264",10), ("265",3),
                        ("svtav1",5),("libopus", 1)]
    for criterion in simple_criterion:
        if version.find(criterion[0]) >= 0:
            score += criterion[1]
    #obtain rough compile year from copyright information
    copyright_index = version.find('2000-2')
    if copyright_index >= 0:
        copyright_year = version[copyright_index+6:copyright_index+9]
        if copyright_year.isnumeric():
            score += int(copyright_year)
    return score

def get_ffmpeg_path():
    if "VHS_FORCE_FFMPEG_PATH" in os.environ:
        ffmpeg_path = os.environ.get("VHS_FORCE_FFMPEG_PATH")
    else:
        ffmpeg_paths = []
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            imageio_ffmpeg_path = get_ffmpeg_exe()
            ffmpeg_paths.append(imageio_ffmpeg_path)
        except:
            if "VHS_USE_IMAGEIO_FFMPEG" in os.environ:
                raise
            # logger.warn("Failed to import imageio_ffmpeg")
        if "VHS_USE_IMAGEIO_FFMPEG" in os.environ:
            ffmpeg_path = imageio_ffmpeg_path
        else:
            system_ffmpeg = shutil.which("ffmpeg")
            if system_ffmpeg is not None:
                ffmpeg_paths.append(system_ffmpeg)
            if len(ffmpeg_paths) == 0:
                raise Exception("No valid ffmpeg found.")
                ffmpeg_path = None
            elif len(ffmpeg_paths) == 1:
                #Evaluation of suitability isn't required, can take sole option
                #to reduce startup time
                ffmpeg_path = ffmpeg_paths[0]
            else:
                ffmpeg_path = max(ffmpeg_paths, key=ffmpeg_suitability)
    return ffmpeg_path

def lazy_eval(func):
    class Cache:
        def __init__(self, func):
            self.res = None
            self.func = func
        def get(self):
            if self.res is None:
                self.res = self.func()
            return self.res
    cache = Cache(func)
    return lambda : cache.get()

def cv_frame_generator(video, frame_load_cap, skip_first_frames, select_every_nth):
    try:
        video_cap = cv2.VideoCapture(video)
        if not video_cap.isOpened():
            raise ValueError(f"{video} could not be loaded with cv.")
        # set video_cap to look at start_index frame
        total_frame_count = 0
        total_frames_evaluated = -1
        frames_added = 0
        frame_rate = video_cap.get(cv2.CAP_PROP_FPS)
        base_frame_time = 1/frame_rate
        width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        prev_frame = None
        target_frame_time = base_frame_time

        yield (width, height, target_frame_time, frame_rate)
        time_offset=target_frame_time - base_frame_time
        while video_cap.isOpened():
            if time_offset < target_frame_time:
                is_returned = video_cap.grab()
                # if didn't return frame, video has ended
                if not is_returned:
                    break
                time_offset += base_frame_time
            if time_offset < target_frame_time:
                continue
            time_offset -= target_frame_time
            # if not at start_index, skip doing anything with frame
            total_frame_count += 1
            if total_frame_count <= skip_first_frames:
                continue
            else:
                total_frames_evaluated += 1

            # if should not be selected, skip doing anything with frame
            if total_frames_evaluated%select_every_nth != 0:
                continue

            # opencv loads images in BGR format (yuck), so need to convert to RGB for ComfyUI use
            # To my testing: No. opencv has no support for alpha
            unused, frame = video_cap.retrieve()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # convert frame to comfyui's expected format
            # TODO: frame contains no exif information. Check if opencv2 has already applied
            frame = np.array(frame, dtype=np.float32) / 255.0
            if prev_frame is not None:
                inp  = yield prev_frame
                if inp is not None:
                    #ensure the finally block is called
                    return
            prev_frame = frame
            frames_added += 1
            # if cap exists and we've reached it, stop processing frames
            if frame_load_cap > 0 and frames_added >= frame_load_cap:
                break
        if prev_frame is not None:
            yield prev_frame
    finally:
        video_cap.release()

def get_audio(file, start_time=0, duration=0):
    args = [get_ffmpeg_path(), "-v", "error", "-i", file]
    if start_time > 0:
        args += ["-ss", str(start_time)]
    if duration > 0:
        args += ["-t", str(duration)]
    try:
        res =  subprocess.run(args + ["-f", "wav", "-"],
                              stdout=subprocess.PIPE, check=True).stdout
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to extract audio from: {file}")
        return False
    return res

def clean_string(input_string):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    cleaned_string = ''.join(c if c not in invalid_chars else '_' for c in input_string)
    cleaned_string = cleaned_string.strip(" .")
    return cleaned_string

class LoadYoutubeVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "url": ("STRING",{"default":""}),
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
    import numpy as np

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
                print(f"[⭐PRONODES] Downloaded video to {video_save_path}")
            else:
                print(f"[⭐PRONODES] '{video_title}.mp4' exists.. skipping download")

            # load video frames
            gen = cv_frame_generator(video_save_path, frame_load_cap, skip_first_frames, select_every_nth)
            (width, height, target_frame_time, frame_rate) = next(gen)
            width = int(width)
            height = int(height)
            calculated_frame_rate = int(frame_rate/select_every_nth)
            
            # Some minor wizardry to eliminate a copy and reduce max memory by a factor of ~2
            images = torch.from_numpy(np.fromiter(gen, np.dtype((np.float32, (height, width, 3)))))
            if len(images) == 0:
                raise Exception("[⭐PRONODES] No frames generated")


            #Setup lambda for lazy audio capture
            audio = lambda : get_audio(video_save_path, skip_first_frames * target_frame_time,
                                    frame_load_cap*target_frame_time*select_every_nth)
            return (images, lazy_eval(audio),calculated_frame_rate)

        except Exception as e:
            raise e

