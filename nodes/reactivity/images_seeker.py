import torch
import os
# import einops
from comfy.model_management import soft_empty_cache, get_torch_device
import numpy as np
from comfy.utils import ProgressBar
import pathlib
import traceback
import folder_paths
from urllib.parse import urlparse
from torch.hub import download_url_to_file, get_dir
import einops


MODEL_TYPE = pathlib.Path(__file__).parent.name
CKPT_NAME_VER_DICT = {
    "rife47.pth": "4.7",
    "rife48.pth": "4.7",
    "rife49.pth": "4.7",
}
BASE_MODEL_DOWNLOAD_URLS = [
    "https://github.com/styler00dollar/VSGAN-tensorrt-docker/releases/download/models/",
    "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation/releases/download/models/",
    "https://github.com/dajes/frame-interpolation-pytorch/releases/download/v1.0.0/"
]

def preprocess_frames(frames):
    return einops.rearrange(frames[..., :3], "n h w c -> n c h w")

def postprocess_frames(frames):
    return einops.rearrange(frames, "n c h w -> n h w c")[..., :3].cpu()

class ImagesSeekerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image": ("IMAGE",),
                "fps": ("INT", {"default": 12,"min": 1, "max": 255, "step": 1}),
                "skip_count": ("INT", {"default": 5,"min": 1, "max": 255, "step": 1}),
                "skip_range": ("INT", {"default": 10,"min": 1, "max": 255, "step": 1}),
                "points_string": ("STRING", {"default": "0:(0.0),\n7:(1.0),\n15:(0.0)\n", "multiline": True}),
            }
        }

    RETURN_NAMES = ("IMAGE",)
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    CATEGORY = "Pronodes/Reactivity"

    def main(self, image, fps, skip_count, skip_range, points_string):
        # Parse the input string into a list of tuples
        points = []
        points_string = points_string.rstrip(',\n')
        for point_str in points_string.split(','):
            frame_str, value_str = point_str.split(':')
            frame = int(frame_str.strip())
            value = float(value_str.strip()[1:-1])  # Remove parentheses around value
            points.append((frame, value))
            
        images_list = list(torch.split(image, split_size_or_sections=1))
        seeked_images_list = []
        # print("image count", len(images_list))
        seeked_idx = -1
        
        seeked_idx_list = []
        for frame, value in points:
            if value == 1.0:

                for i in range(skip_range):

                    seeked_idx += skip_count
                    if seeked_idx < len(images_list):
                        seeked_images_list.append(images_list[seeked_idx])
                        seeked_idx_list.append(seeked_idx)

            else:
                seeked_idx += 1

                if seeked_idx < len(images_list):
                    seeked_images_list.append(images_list[seeked_idx])
                    seeked_idx_list.append(seeked_idx)
        
        original_duration = len(images_list) / fps
        new_fps = len(seeked_images_list) / original_duration

        # print(original_duration, new_fps, len(seeked_images_list))

        images_t = torch.cat(seeked_images_list, dim=0)
        return (images_t, new_fps,)

    @classmethod
    def vfi(
        self,
        ckpt_name,
        frames,
        clear_cache_after_n_frames = 10,
        multiplier = 2,
        fast_mode = False,
        ensemble = False,
        scale_factor = 1.0,
    ):
        from .rife_arch import IFNet
        model_path = self.load_file_from_github_release(MODEL_TYPE, ckpt_name)
        arch_ver = CKPT_NAME_VER_DICT[ckpt_name]
        interpolation_model = IFNet(arch_ver=arch_ver)
        interpolation_model.load_state_dict(torch.load(model_path))
        interpolation_model.eval().to(get_torch_device())
        frames = preprocess_frames(frames).to(get_torch_device())


        def return_middle_frame(frame_0, frame_1, timestep, model, scale_list, in_fast_mode, in_ensemble):
            return model(frame_0, frame_1, timestep, scale_list, in_fast_mode, in_ensemble)
        
        scale_list = [8 / scale_factor, 4 / scale_factor, 2 / scale_factor, 1 / scale_factor] 
        
        args = [interpolation_model, scale_list, fast_mode, ensemble]
        out = postprocess_frames(
            self.generate_frames_rife(frames, clear_cache_after_n_frames, multiplier, return_middle_frame, *args)
        )
        return out

    @classmethod
    def generate_frames_rife(
        self,
        frames,
        clear_cache_after_n_frames,
        multiplier,
        return_middle_frame_function,
        *return_middle_frame_function_args
    ):
        output_frames = torch.zeros(multiplier*frames.shape[0], *frames.shape[1:], device="cpu")
        out_len = 0

        number_of_frames_processed_since_last_cleared_cuda_cache = 0
        pbar = ProgressBar(len(frames))

        for frame_itr in range(len(frames) - 1): # Skip the final frame since there are no frames after it

            frame_0 = frames[frame_itr:frame_itr+1]
            frame_1 = frames[frame_itr+1:frame_itr+2]
            output_frames[out_len] = frame_0 # Start with first frame
            out_len += 1

            for middle_i in range(1, multiplier):
                timestep = middle_i/multiplier
                middle_frame = return_middle_frame_function(frame_0, frame_1, timestep, *return_middle_frame_function_args).detach().cpu()

                # Copy middle frames to output
                output_frames[out_len] = middle_frame
                out_len +=1

                # Try to avoid a memory overflow by clearing cuda cache regularly
                number_of_frames_processed_since_last_cleared_cuda_cache += 1
                if number_of_frames_processed_since_last_cleared_cuda_cache >= clear_cache_after_n_frames:
                    soft_empty_cache()
                    number_of_frames_processed_since_last_cleared_cuda_cache = 0
                    print("Clearing cache...")

                pbar.update(1)
            

        # Append final frame
        output_frames[out_len] = frames[-1:]
        print(f"done! - {(len(frames) -1) * (multiplier-1)} new frames generated at resolution: {output_frames[0].shape}")
        out_len += 1

        # clear cache for courtesy
        soft_empty_cache()
        print("Final clearing cache done ...")

        res = output_frames[:out_len]
        return res

    @staticmethod
    def get_ckpt_container_path(model_type):
        # Use the original save location
        return os.path.join(folder_paths.models_dir, model_type)

    @staticmethod
    def load_file_from_url(url, model_dir=None, progress=True, file_name=None):
        if model_dir is None:
            hub_dir = get_dir()
            model_dir = os.path.join(hub_dir, 'checkpoints')

        os.makedirs(model_dir, exist_ok=True)

        parts = urlparse(url)
        file_name = os.path.basename(parts.path) if file_name is None else file_name
        cached_file = os.path.abspath(os.path.join(model_dir, file_name))
        if not os.path.exists(cached_file):
            print(f'Downloading: "{url}" to {cached_file}\n')
            download_url_to_file(url, cached_file, hash_prefix=None, progress=progress)
        return cached_file

    @classmethod
    def load_file_from_github_release(cls, model_type, ckpt_name):
        error_strs = []
        for i, base_model_download_url in enumerate(BASE_MODEL_DOWNLOAD_URLS):
            try:
                return cls.load_file_from_url(base_model_download_url + ckpt_name, cls.get_ckpt_container_path(model_type))
            except Exception:
                traceback_str = traceback.format_exc()
                if i < len(BASE_MODEL_DOWNLOAD_URLS) - 1:
                    print("Failed! Trying another endpoint.")
                error_strs.append(f"Error when downloading from: {base_model_download_url + ckpt_name}\n\n{traceback_str}")

        error_str = '\n\n'.join(error_strs)
        raise Exception(f"Tried all GitHub base urls to download {ckpt_name} but no success. Below is the error log:\n\n{error_str}")
