import os
import io
from collections import namedtuple

import numpy as np
from ipycanvas import Canvas, MultiCanvas, hold_canvas
from ipywidgets import Image, Output, widgets
from PIL import Image as PILImage
from typing import Dict, List, Tuple
from IPython.display import display

Label = namedtuple('Label', ['text', 'x', 'y', 'conf'])

class AttendanceTool:
    out = Output()
    canvas: Canvas

    def __init__(self, path: str) -> None:
        self.root = path
        file_lists = sorted(os.listdir(self.root))
        self.thumbnail_size = (300, 200)

        self.widgets: Dict[str, widgets.Widget] = dict(
            prefix = widgets.Text(
                value='A',
                placeholder='prefix',
                description='Prefix',
                layout={'width': '15%'},
                disabled=False
            ),
            format = widgets.Text(
                value='02d',
                placeholder='format',
                description='Format',
                layout={'width': '15%'},
                disabled=False
            ),
            fill_color = widgets.Text(
                value='red',
                placeholder='black or #000000',
                description='Text color',
                layout={'width': '15%'},
                disabled=False
            ),
            stroke_color = widgets.Text(
                value='yellow',
                placeholder='black or #000000',
                description='Stroke color',
                layout={'width': '15%'},
                disabled=False
            ),
            display_size = widgets.IntSlider(
                value=1200,
                min=320,
                max=3840,
                step=10,
                description='Max Width',
                layout={'width': '50%'},
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
            file = widgets.Select(
                options=file_lists,
                value=file_lists[0],
                rows=10,
                description='Image',
                disabled=False
            ),
            thumbnail = widgets.Image(
                width=self.thumbnail_size[0],
                height=self.thumbnail_size[1],
            ),
            offset = widgets.BoundedIntText(
                value=0,
                min=0,
                step=1,
                description='Index',
                layout={'width': '15%'},
                disabled=False
            ),
            label_mode = widgets.Label(
                value=" Mode "
            ),
            mode = widgets.ToggleButtons(
                options = ['Label', 'Remove'],
                value='Label',
                tooltips=['Label', 'Remove'],
                layout={'width': 'fit-content'},
            )
        )
        
        self.btns: Dict[str, widgets.Widget] = dict(
            load = widgets.Button(
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
            rotate = widgets.Button(
                description='Rotate',
                tooltip='Rotate'
            ),
            undo = widgets.Button(
                description='Undo',
                tooltip='Undo'
            )
        )

        self.canvas = MultiCanvas(2, width=100, height=100)
        self.btns['load'].on_click(self.on_btn_load)
        self.btns['clear'].on_click(self.on_btn_clear)
        self.btns['save'].on_click(self.on_btn_save)
        self.btns['undo'].on_click(self.on_btn_undo)
        self.btns['rotate'].on_click(self.on_btn_rotate)

        self.canvas.on_mouse_down(self.on_click)
        self.canvas.on_key_down(self.on_keydown)

        self.widgets['file'].observe(self.on_select_image, 'value')
        self.on_select_image(None)

        self.labels: List[Label] = []

        display(
            widgets.HBox((
                self.widgets['prefix'], self.widgets['format'], self.widgets['fill_color'], self.widgets['stroke_color']
            )),
            widgets.HBox((
                self.widgets['display_size'],
            )),
            widgets.HBox((
                self.widgets['file'], self.widgets['thumbnail']
            )),
            widgets.HBox((
                self.widgets['label_mode'], self.widgets['mode']
            )),
            widgets.HBox((
                self.widgets['offset'], self.widgets['fontsize']
            )),
            widgets.HBox(tuple(self.btns.values())),
            self.out
        )

    def conf(self, key: str) -> str|int:
        if key == 'ALL':
            return {k: v.value for k, v in self.widgets.items()}

        value = self.widgets[key].value
        return value

    def on_btn_load(self, _):
        self.labels.clear()
        self.canvas[1].clear()
        self.out.clear_output()
        
        with self.out:
            self.load_image()
            self.draw_canvas()
    
    def display(self):
        return self.canvas

    def on_btn_clear(self, _):
        self.labels.clear()
        self.canvas[1].clear()

    def on_btn_undo(self, _):
        self.labels.pop()
        self.draw_labels()
    
    def on_btn_rotate(self, _):     
        with self.out:
            self.image = self.image.rotate(90, expand=True)
            self.draw_canvas()
            self.draw_labels()

    def on_btn_rotate_CW(self, _):     
        with self.out:
            self.image = self.image.rotate(-90, expand=True)
            self.draw_canvas()
            self.draw_labels()


    def on_btn_save(self, _):
        with self.out:
            path, base = os.path.split(self.image_path)
            start = self.labels[0].text
            end = self.labels[-1].text
            filename = f"labeled_{start}-{end}"
            output = os.path.join(path, f'{filename}.png')
            canvas = Canvas(width=self.canvas.width, height=self.canvas.height, sync_image_data=True)

            def _save(_):
                with self.out:
                    canvas.to_file(output)
                    print('Done')

            print(f'Saving to {output}..', end='')
            canvas.observe(_save, "image_data")
            with hold_canvas():
                canvas.draw_image(self.canvas[0])
                canvas.draw_image(self.canvas[1])
            # canvas.to_file(output)


    def load_image(self, verbose=True):
        if verbose:
            print(f'Loading image {self.conf("file")}..', end='')

        self.image_path = os.path.join(self.root, self.conf('file'))
        self.image = PILImage.open(self.image_path)

        if verbose:
            print(f'Done. Size: {self.image.size}')

    def draw_canvas(self, verbose=True):
        w, h = self.image.size
        max_w = self.conf('display_size') #max width
        if w > max_w:
            r = max_w / w
            canvas_size = (int(w * r), int(h * r))
            if verbose:
                print(f'Image resized: {self.image.size} -> {canvas_size}')
        else:
            canvas_size = w, h
            

        self.canvas.width = canvas_size[0]
        self.canvas.height = canvas_size[1]
        
        # self.canvas[0].draw_image(self.image, width=canvas_size[0], height=canvas_size[1])
        self.canvas[0].put_image_data(np.array(self.image.resize(canvas_size)))
        self.canvas_size = canvas_size
        return self.canvas

    def index(self):
        return self.conf('offset')

    @out.capture()
    def on_click(self, x, y):
        mode = self.conf('mode')
        if mode == 'Label':
            idx = self.index()
            text_format: str = self.conf('prefix') + "{0:" + self.conf('format') + "}"
            text = text_format.format(idx)
            self.widgets['offset'].value = idx + 1

            self.labels.append(Label(text, x, y, self.conf("ALL")))
        elif mode == 'Remove':
            self.remove_nearest_label(x, y)

        self.draw_labels()
    
    @out.capture()
    def on_keydown(self, key, shift_key, ctrl_key, meta_key):
        if key == 'z':
            self.on_btn_undo(None)
        elif ord('1') <= ord(key) <= ord('9'):
            i = ord(key) - ord('1')
            self.widgets['fontsize'].value = 8 + (8 * i)
        elif key == 's':
            self.on_btn_save(None)
        elif key == 'r':
            self.on_btn_rotate(None)
        elif key == 't':
            self.on_btn_rotate_CW(None)
        elif key == 'o':
            self.widgets['mode'].value = 'Label'
        elif key == 'p':
            self.widgets['mode'].value = 'Remove'
        elif key == 'c':
            self.on_btn_clear(None)


    def remove_nearest_label(self, x, y):
        if len(self.labels) < 1:
            return
        
        def distance(label: Label):
            return (label.x - x) ** 2 + (label.y - y) ** 2

        idx = 0
        dist = distance(self.labels[0])

        for i, label in enumerate(self.labels):
            d = distance(label)
            if d < dist:
                dist = d
                idx = i
        
        self.labels.pop(idx)


    def draw_labels(self, canvas=None):
        if canvas is None:
            canvas = self.canvas[1]

        with hold_canvas():
            canvas.clear()
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

    def on_select_image(self, _):
        with self.out:
            image_path = os.path.join(self.root, self.conf('file'))
            image = PILImage.open(image_path)
            image.thumbnail(self.thumbnail_size)
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            self.widgets['thumbnail'].value = img_byte_arr.getvalue()
