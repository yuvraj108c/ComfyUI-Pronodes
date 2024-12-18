from .nodes.load_youtube_video import LoadYoutubeVideoNode
from .nodes.preview_vhs_audio import PreviewVHSAudioNode
from .nodes.vhs_filenames_to_path import VHSFilenamesToPathNode
from .nodes.save_overwrite_image import SaveAndOverwriteImageNode
from .nodes.load_image_out_directory import LoadImageFromOutputDirectoryNode
from .nodes.reactivity.images_shuffler import ImagesShufflerNode
from .nodes.reactivity.images_seeker import ImagesSeekerNode
 
NODE_CLASS_MAPPINGS = { 
    "LoadYoutubeVideoNode" : LoadYoutubeVideoNode,
    "PreviewVHSAudioNode" : PreviewVHSAudioNode,
    "VHSFilenamesToPathNode" : VHSFilenamesToPathNode,
    "SaveAndOverwriteImageNode" : SaveAndOverwriteImageNode,
    "LoadImageFromOutputDirectoryNode" : LoadImageFromOutputDirectoryNode,
    "ImagesShufflerNode" : ImagesShufflerNode,
    "ImagesSeekerNode" : ImagesSeekerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
     "LoadYoutubeVideoNode" : "⚡ Load Youtube Video",
     "PreviewVHSAudioNode" : "⚡ Preview VHS audio",
     "VHSFilenamesToPathNode" : "⚡ VHS Filenames To Path",
     "SaveAndOverwriteImageNode" : "⚡ Save & Overwrite Image",
     "ImagesShufflerNode" : "⚡ Images Shuffler",
     "ImagesSeekerNode" : "⚡ Images Seeker",
}

WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS','WEB_DIRECTORY']