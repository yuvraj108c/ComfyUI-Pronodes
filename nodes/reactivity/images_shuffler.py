import random
import torch

class ImagesShufflerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image": ("IMAGE",),
                "fps": ("INT", {"default": 12,"min": 1, "max": 255, "step": 1}),
                "points_string": ("STRING", {"default": "0:(0.0),\n7:(1.0),\n15:(0.0)\n", "multiline": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
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
        
        random_image_idx = random.randint(0, len(images_list) - 1)
        shuffled_images_list = []
        
        for frame, value in points:
            if value == 1.0:
                random_image_idx = random.randint(0, len(images_list) - 1)
            shuffled_images_list.append(images_list[random_image_idx])                
            
        images_t = torch.cat(shuffled_images_list, dim=0)
        return (images_t,)