import folder_paths
import os

class VHSFilenamesToPath:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "Filenames": ("VHS_FILENAMES",),
            }
        }

    RETURN_NAMES = ("path",)
    RETURN_TYPES = ("STRING",)
    FUNCTION = "main"
    CATEGORY = "Pronodes"

    def main(self,Filenames):
        save_output, output_files = Filenames
        return (output_files[-1],)