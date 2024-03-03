import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// Copied from videohelpersuite
// https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/blob/ca8494b38006c76f5b0f02eade284998dbab011e/web/js/VHS.core.js

function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]])
    node?.graph?.setDirtyCanvas(true);
}

function chainCallback(object, property, callback) {
    if (object == undefined) {
        //This should not happen.
        console.error("Tried to add callback to non-existant object")
        return;
    }
    if (property in object) {
        const callback_orig = object[property]
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            callback.apply(this, arguments);
            return r
        };
    } else {
        object[property] = callback;
    }
}

function addVideoPreview(nodeType) {
    chainCallback(nodeType.prototype, "onNodeCreated", function () {
        var element = document.createElement("div");
        const previewNode = this;
        var previewWidget = this.addDOMWidget("videopreview", "preview", element, {
            serialize: false,
            hideOnZoom: false,
            getValue() {
                return element.value;
            },
            setValue(v) {
                element.value = v;
            },
        });
        previewWidget.computeSize = function (width) {
            const textPreviewHeight = 70
            if (this.aspectRatio && !this.parentEl.hidden) {
                let height = (previewNode.size[0] - 20) / this.aspectRatio + 10 + textPreviewHeight;
                if (!(height > 0)) {
                    height = 0;
                }
                this.computedHeight = height + 10 + textPreviewHeight;
                return [width, height];
            }
            return [width, -4];//no loaded src, widget should not display
        }
        // element.style['pointer-events'] = "none"
        previewWidget.value = { hidden: false, paused: false, params: {} }
        previewWidget.parentEl = document.createElement("div");
        previewWidget.parentEl.className = "pronodes_preview";
        previewWidget.parentEl.style['width'] = "100%"
        element.appendChild(previewWidget.parentEl);
        previewWidget.videoEl = document.createElement("video");
        previewWidget.videoEl.controls = true;
        previewWidget.videoEl.loop = true;
        previewWidget.videoEl.muted = true;
        previewWidget.videoEl.style['width'] = "100%"
        previewWidget.videoEl.addEventListener("loadedmetadata", () => {

            previewWidget.aspectRatio = previewWidget.videoEl.videoWidth / previewWidget.videoEl.videoHeight;
            fitHeight(this);
        });
        previewWidget.videoEl.addEventListener("error", () => {
            //TODO: consider a way to properly notify the user why a preview isn't shown.
            previewWidget.parentEl.hidden = true;
            fitHeight(this);
        });

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

        this.updateParameters = (params, force_update) => {
            if (!previewWidget.value.params) {
                if (typeof (previewWidget.value != 'object')) {
                    previewWidget.value = { hidden: false, paused: false }
                }
                previewWidget.value.params = {}
            }
            Object.assign(previewWidget.value.params, params)

            if (force_update) {
                previewWidget.updateSource();
            }
        };
        previewWidget.updateSource = function () {
            if (this.value.params == undefined) {
                return;
            }
            let params = {}
            Object.assign(params, this.value.params);//shallow copy
            this.parentEl.hidden = this.value.hidden;

            if (params.previews && params.data) {

                previewWidget.videoEl.src = api.apiURL('/view?' + new URLSearchParams(params.previews[0]));

                const { frame_rate, video_title, resolution } = params.data[0]
                previewWidget.textEl.value = `RESOLUTION: ${resolution}, FPS: ${frame_rate}\nTITLE: ${video_title}`

                this.videoEl.autoplay = true;
                this.videoEl.hidden = false;
                this.textEl.hidden = false;
            } else {
                this.textEl.hidden = true;
                this.videoEl.hidden = true;
            }
        }
        previewWidget.parentEl.appendChild(previewWidget.textEl)
        previewWidget.parentEl.appendChild(previewWidget.videoEl)
    });
}

app.registerExtension({
    name: "pronodes.youtube_video_display",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        if (nodeData?.name == "LoadYoutubeVideoNode") {
            chainCallback(nodeType.prototype, "onExecuted", function (message) {
                if (message?.previews) {
                    this.updateParameters(message, true);
                }
            });
            addVideoPreview(nodeType);

            //Hide the information passing 'preview' output
            //TODO: check how this is implemented for save image
            chainCallback(nodeType.prototype, "onNodeCreated", function () {
                this._outputs = this.outputs
                Object.defineProperty(this, "outputs", {
                    set: function (value) {
                        this._outputs = value;
                        requestAnimationFrame(() => {
                            if (app.nodeOutputs[this.id + ""]) {
                                this.updateParameters(app.nodeOutputs[this.id + ""], true);
                            }
                        })
                    },
                    get: function () {
                        return this._outputs;
                    }
                });
                //Display previews after reload/ loading workflow
                requestAnimationFrame(() => { this.updateParameters({}, true); });
            });
        }
    },
});