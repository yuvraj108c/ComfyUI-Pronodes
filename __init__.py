from .nodes.load_youtube_video import LoadYoutubeVideo
 
NODE_CLASS_MAPPINGS = { 
    "LoadYoutubeVideo" : LoadYoutubeVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "LoadYoutubeVideo" : "⭐Load Youtube Video",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']