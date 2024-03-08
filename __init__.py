from .nodes.load_youtube_video import LoadYoutubeVideoNode
from .nodes.preview_vhs_audio import PreviewVHSAudioNode
from .nodes.vhs_filenames_to_path import VHSFilenamesToPath
 
NODE_CLASS_MAPPINGS = { 
    "LoadYoutubeVideoNode" : LoadYoutubeVideoNode,
    "PreviewVHSAudioNode" : PreviewVHSAudioNode,
    "VHSFilenamesToPath" : VHSFilenamesToPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "LoadYoutubeVideoNode" : "⚡ Load Youtube Video",
     "PreviewVHSAudioNode" : "⚡ Preview VHS audio",
     "VHSFilenamesToPath" : "⚡ VHS Filenames To Path",
}

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']