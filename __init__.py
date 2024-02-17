from .nodes.load_youtube_video import LoadYoutubeVideoNode
 
NODE_CLASS_MAPPINGS = { 
    "LoadYoutubeVideoNode" : LoadYoutubeVideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "LoadYoutubeVideoNode" : "⚡ Load Youtube Video",
}

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']