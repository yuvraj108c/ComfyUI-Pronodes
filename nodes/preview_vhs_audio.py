import folder_paths
import os

class PreviewVHSAudioNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "audio": ("VHS_AUDIO",),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "main"
    CATEGORY = "Pronodes"
    OUTPUT_NODE=True

    def main(self,audio):
        # save audio
        audio_save_name = "vhs_audio_preview.wav"
        os.makedirs(folder_paths.get_temp_directory(), exist_ok=True)
        audio_save_path = os.path.join(folder_paths.get_temp_directory(),audio_save_name)
        with open(audio_save_path, 'wb') as file:
            file.write(audio())

        previews = [
            {
                "filename": audio_save_name,
                "type":"temp"
            }
        ]

        return {"ui": {"previews":previews},}