import folder_paths
import os
from .utils import tensor2pil

class SaveAndOverwriteImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image": ("IMAGE",),
                "filename": ("STRING",{"default":"image.png"})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "main"
    CATEGORY = "Pronodes"
    OUTPUT_NODE=True

    def main(self,image, filename):
        pil_images = tensor2pil(image) 
        pil_images[0].save(os.path.join(folder_paths.get_output_directory(), filename))
        return {}