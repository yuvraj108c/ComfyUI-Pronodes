import random
import torch
import itertools

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


    def shuffle_no_consecutive(self,lst):
        """
        Shuffles a list ensuring no element appears consecutively with its original neighbors.
        
        Args:
            lst: Input list to be shuffled
            
        Returns:
            A new shuffled list where no element appears next to the same elements as in the original list
            Returns None if such a shuffle is impossible
        """
        if len(lst) <= 1:
            return lst.copy()
            
        # Make a copy to avoid modifying the original list
        result = []
        remaining = lst.copy()
        
        # Keep track of the last added element to avoid consecutive repeats
        last_added = None
        
        # Maximum attempts to find a valid shuffle
        max_attempts = 100
        
        while remaining:
            # Get valid candidates (not adjacent to last_added)
            candidates = [x for x in remaining if x != last_added]
            
            # If we're at the last element, also ensure it's not equal to the first element
            if len(remaining) == 1 and result and candidates and candidates[0] == result[0]:
                # If this happens, we need to backtrack or restart
                if max_attempts > 0:
                    # Reset and try again
                    result = []
                    remaining = lst.copy()
                    last_added = None
                    max_attempts -= 1
                    continue
                else:
                    return None
                    
            if not candidates:
                if max_attempts > 0:
                    # Reset and try again
                    result = []
                    remaining = lst.copy()
                    last_added = None
                    max_attempts -= 1
                    continue
                else:
                    return None
                    
            # Randomly select from valid candidates
            chosen = random.choice(candidates)
            result.append(chosen)
            remaining.remove(chosen)
            last_added = chosen
            
        return result

    def main(self, image, fps, points_string):
        # Parse the input string into a list of tuples
        points = []
        points_string = points_string.rstrip(',\n')
        for point_str in points_string.split(','):
            frame_str, value_str = point_str.split(':')
            frame = int(frame_str.strip())
            value = float(value_str.strip()[1:-1])  # Remove parentheses around value
            points.append((frame, value))
            
        images_indices_list = [index for index in range(image.shape[0])]

        # Resize list to match the size of points
        images_indices_list = list(itertools.islice(itertools.cycle(images_indices_list), len(points)))
        shuffled_images_indices_list = self.shuffle_no_consecutive(images_indices_list)

        # Sync frame change to beat        
        final_shuffled_images_indices_list = []
        frame_idx = 0
        for frame, value in points:
            if value == 1.0:
                frame_idx += 1
            final_shuffled_images_indices_list.append(shuffled_images_indices_list[frame_idx])

        final_tensors = [image[idx] for idx in final_shuffled_images_indices_list]
        
        return (torch.stack(final_tensors),)