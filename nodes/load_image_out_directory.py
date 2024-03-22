import folder_paths
from PIL import Image
import os
from .utils import pil2tensor

class LoadImageFromOutputDirectoryNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "image":("IMAGE",),
                "filename": ("STRING",{"default":"image.png"})
            }
        }

    RETURN_NAMES = ("image",)
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    CATEGORY = "Pronodes"

    def main(self, image, filename):
        pil_image = Image.open(os.path.join(folder_paths.get_output_directory(),filename))
        return (pil2tensor(pil_image),)