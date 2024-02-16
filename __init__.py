from .nodes.download_youtube_video import DownloadYoutubeVideo
 
NODE_CLASS_MAPPINGS = { 
    "DownloadYoutubeVideo" : DownloadYoutubeVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "DownloadYoutubeVideo" : "⭐ Download Youtube Video",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']