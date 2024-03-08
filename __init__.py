from .nodes.load_youtube_video import LoadYoutubeVideoNode
from .nodes.preview_vhs_audio import PreviewVHSAudioNode
 
NODE_CLASS_MAPPINGS = { 
    "LoadYoutubeVideoNode" : LoadYoutubeVideoNode,
    "PreviewVHSAudioNode" : PreviewVHSAudioNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "LoadYoutubeVideoNode" : "⚡ Load Youtube Video",
     "PreviewVHSAudioNode" : "⚡ Preview VHS audio",
}

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']