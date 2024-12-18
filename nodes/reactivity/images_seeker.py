import torch

class ImagesSeekerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image": ("IMAGE",),
                "fps": ("INT", {"default": 12,"min": 1, "max": 255, "step": 1}),
                "points_string": ("STRING", {"default": "0:(0.0),\n7:(1.0),\n15:(0.0)\n", "multiline": True}),
            }
        }

    RETURN_NAMES = ("IMAGE", "FPS")
    RETURN_TYPES = ("IMAGE", "FLOAT")
    FUNCTION = "main"
    CATEGORY = "Pronodes/Reactivity"

    def main(self, image, fps, points_string):
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
        
        constant_skip_value = 5
        seeked_idx = -1

        for frame, value in points:
            if value == 1.0:
                seeked_idx += constant_skip_value
            else:
                seeked_idx += 1

            if seeked_idx < len(images_list):
                seeked_images_list.append(images_list[seeked_idx])

        original_duration = len(images_list) / fps
        new_fps = len(seeked_images_list) / original_duration

        # print(original_duration, new_fps, len(seeked_images_list))

        images_t = torch.cat(seeked_images_list, dim=0)
        return (images_t, new_fps,)