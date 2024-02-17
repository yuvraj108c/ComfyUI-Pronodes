import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// https://github.com/yolain/ComfyUI-Easy-Use/blob/be8df4e6faec6892d3007b63adb0c0b3ef510e59/web/js/image.js
// https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/blob/ca8494b38006c76f5b0f02eade284998dbab011e/web/js/VHS.core.js#L347
// https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved/blob/main/web/js/gif_preview.js

const youtube_video_preview = {
    name: 'Pronodes.youtube_video_preview',
    nodeCreated(node) {
        if (node.getTitle() == "⚡ Load Youtube Video") {
            const element = document.createElement("div");
            const previewWidget = node.addDOMWidget("datapreview", "preview", element, {
                getValue() {
                    return element.value;
                },
                setValue(v) {
                    element.src = v;
                },
                serialize: false,
            });
            element.style['pointer-events'] = "none"

            // text
            previewWidget.textEl = document.createElement("textarea");
            previewWidget.textEl.className = "comfy-multiline-input";
            previewWidget.textEl.style["width"] = "100%"
            previewWidget.textEl.readOnly = true
            previewWidget.textEl.rows = 3
            previewWidget.textEl.style.color = "#00FF41"
            previewWidget.textEl.style.overflow = "hidden"
            previewWidget.textEl.style["font-size"] = "smaller"
            previewWidget.textEl.style["padding"] = "4%"
            previewWidget.textEl.style["background-color"] = "black"
            previewWidget.textEl.hidden = true
            element.appendChild(previewWidget.textEl)

            // video
            previewWidget.videoEl = document.createElement("video");
            previewWidget.videoEl.autoplay = true
            previewWidget.videoEl.loop = true
            previewWidget.videoEl.muted = true
            previewWidget.videoEl.controls = true
            previewWidget.videoEl.hidden = true
            previewWidget.videoEl.style["width"] = "100%"
            previewWidget.videoEl.style["pointer-events"] = "initial"
            element.appendChild(previewWidget.videoEl)

            previewWidget.videoEl.addEventListener("loadedmetadata", () => {
                node.setSize([node.size[0], previewWidget.videoEl.offsetHeight + 160])
                node?.graph?.setDirtyCanvas(true);
            });
        }
    },
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        switch (nodeData.name) {
            case 'LoadYoutubeVideoNode': {
                const onExecuted = nodeType.prototype.onExecuted
                nodeType.prototype.onExecuted = function (message) {
                    const r = onExecuted ? onExecuted.apply(this, message) : undefined
                    if (this.widgets) {
                        const pos = this.widgets.findIndex((w) => w.name === "datapreview");
                        if (pos !== -1 && this.widgets[pos]) {
                            const w = this.widgets[pos]

                            if (message?.previews) {
                                const previewUrl = api.apiURL(
                                    '/view?' + new URLSearchParams(message.previews[0]).toString()
                                )
                                w.videoEl.hidden = false
                                w.videoEl.src = previewUrl
                            }
                            if (message?.data) {
                                const { frame_rate, video_title, resolution } = message.data[0]
                                w.textEl.hidden = false
                                w.textEl.value = `FPS: ${frame_rate}, RESOLUTION: ${resolution}\nTITLE: ${video_title}`
                            }
                        }
                    }
                    return r
                }
                break
            }
        }
    }
}

app.registerExtension(youtube_video_preview)