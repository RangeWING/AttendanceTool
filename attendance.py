import os
from ipycanvas import Canvas, MultiCanvas, hold_canvas
from ipywidgets import Image, Output, widgets
from PIL import Image as PILImage
from typing import Dict, List, Tuple
from IPython.display import display
from collections import namedtuple
import numpy as np

Label = namedtuple('Label', ['text', 'x', 'y', 'conf'])

class AttendanceTool:
    out = Output()
    canvas: Canvas

    def __init__(self, path: str) -> None:
        self.root = path
        self.widgets: Dict[str, widgets.Widget] = dict(
            offset = widgets.IntSlider(
                value=1,
                min=1,
                max=100,
                step=1,
                description='Index',
                disabled=False
            ),
            prefix = widgets.Text(
                value='A',
                placeholder='prefix',
                description='Prefix',
                disabled=False
            ),
            format = widgets.Text(
                value='02d',
                placeholder='format',
                description='Format',
                disabled=False
            ),
            display_size = widgets.IntSlider(
                value=1600,
                min=320,
                max=3840,
                step=10,
                description='Max Width',
                disabled=False
            ),
            fontsize = widgets.IntSlider(
                value=32,
                min=1,
                max=100,
                step=1,
                description='Font Size',
                disabled=False
            ),
            fill_color = widgets.Text(
                value='red',
                placeholder='black or #000000',
                description='Text color',
                disabled=False
            ),
            stroke_color = widgets.Text(
                value='yellow',
                placeholder='black or #000000',
                description='Stroke color',
                disabled=False
            ),
            file = widgets.Select(
                options=os.listdir(self.root),
                rows=10,
                description='Image',
                disabled=False
            )
        )
        
        self.btns: Dict[str, widgets.Widget] = dict(
            start = widgets.Button(
                description='Load',
                button_style='info',
                tooltip='Load'
            ),
            clear = widgets.Button(
                description='Clear',
                button_style='warning',
                tooltip='Clear'
            ),
            save = widgets.Button(
                description='Save',
                button_style='success',
                tooltip='Save'
            ),
            undo = widgets.Button(
                description='Undo',
                tooltip='Save'
            )
        )

        self.canvas = MultiCanvas(2, width=100, height=100)
        self.btns['start'].on_click(self.on_btn_start)
        self.btns['clear'].on_click(self.on_btn_clear)
        self.btns['save'].on_click(self.on_btn_save)
        self.btns['undo'].on_click(self.on_btn_undo)

        self.labels: List[Label] = []

        display(*self.widgets.values())
        display(widgets.HBox(tuple(self.btns.values())))
        display(self.out)

    def conf(self, key: str) -> str|int:
        if key == 'ALL':
            return {k: v.value for k, v in self.widgets.items()}

        value = self.widgets[key].value
        return value

    def on_btn_start(self, _):
        self.on_btn_clear(None)
        
        with self.out:
            print(f'Loading image {self.conf("file")}', flush=True)
            self.load_image()
            canvas = self.draw_canvas()
        
        display(self.canvas)

        # with self.out_canvas:
        #     display(canvas)

    def on_btn_clear(self, _):
        # self.out.clear_output()
        # self.out_canvas.clear_output()
        # self.canvas.clear()
        self.clear_labels()

    def on_btn_undo(self, _):
        self.labels.pop()
        self.draw_labels()

    def on_btn_save(self, _):
        with self.out:
            path, base = os.path.split(self.image_path)
            output = os.path.join(path, f'labeled_{".".join(base.split(".")[:-1])}.png')
            self.canvas.to_file(output)
            print(f'Saved to {output}', flush=True)


    def load_image(self, verbose=True):
        self.image_path = os.path.join(self.root, self.conf('file'))
        self.image = PILImage.open(self.image_path)
        self.image_size = self.image.size
        if verbose:
            print(f'Image Loaded. Size: {self.image_size}')
    
    def clear_labels(self):
        self.canvas[1].clear()

    def draw_canvas(self, verbose=True):
        w, h = self.image_size
        max_w = self.conf('display_size') #max width
        if w > max_w:
            r = max_w / w
            canvas_size = (int(w * r), int(h * r))
        else:
            canvas_size = w, h
            
        if verbose:
            print(f'Canvas size: {canvas_size}')
        
        self.canvas = MultiCanvas(2, width=canvas_size[0], height=canvas_size[1], sync_image_data=True)
        # self.canvas[0].draw_image(self.image, width=canvas_size[0], height=canvas_size[1])
        self.canvas[0].put_image_data(np.array(self.image.resize(canvas_size)))
        self.canvas.on_mouse_down(self.on_click)
        self.canvas_size = canvas_size
        return self.canvas

    def index(self):
        return self.conf('offset')

    @out.capture()
    def on_click(self, x, y):
        idx = self.index()
        text_format: str = self.conf('prefix') + "{0:" + self.conf('format') + "}"
        text = text_format.format(idx)
        self.widgets['offset'].value = idx + 1

        self.labels.append(Label(text, x, y, self.conf("ALL")))
        self.draw_labels()


    def draw_labels(self):
        with hold_canvas():
            self.clear_labels()
            canvas = self.canvas[1]
            for label in self.labels:
                conf = label.conf
                text = label.text

                canvas.text_align = "center"
                canvas.text_baseline = "middle"

                font = f"{conf['fontsize']}px sans-serif"
                # canvas.font = f"bold {font}"
                # canvas.fill_style = conf['stroke_color']
                # canvas.fill_text(text, label.x, label.y)

                canvas.font = font
                canvas.stroke_style = conf['stroke_color']
                canvas.line_width = 3
                canvas.stroke_text(text, label.x, label.y)

                canvas.font = font
                canvas.fill_style = conf['fill_color']
                canvas.fill_text(text, label.x, label.y)



        


