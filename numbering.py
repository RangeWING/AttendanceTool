import cv2
import numpy as np
from easydict import EasyDict
import argparse
import os

FONT_SIZE = [0.5+i for i in range(10)]

def on_mouse(clicked_list: list, args: dict, callback=None):
    def _on(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            arg = EasyDict(args)
            clicked_list.append(((x, y), arg))
            if callback is not None:
                callback(cv2.EVENT_LBUTTONUP)
        elif event == cv2.EVENT_MBUTTONUP:
            if len(clicked_list) > 0:
                pos = np.array([x, y])
                nearest = min(clicked_list, key=lambda e: np.sum((np.array(e[0]) - pos)**2))
                clicked_list.remove(nearest)
            if callback is not None:
                callback(cv2.EVENT_MBUTTONUP)
    return _on

def update_image(image_original: np.ndarray, clicked_list: list, args: dict):
    result = image_original.copy()
    for i, ((x, y), arg) in enumerate(clicked_list): 
        text = f'{args.prefix}{(arg.index):02d}'
        fontsize = FONT_SIZE[arg.fontsize]
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, fontsize, int(fontsize*3 if arg.bold else fontsize*2))
        text_args = dict(img=result, text=text, org=(x-tw//2, y+th//2),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=fontsize, lineType=cv2.LINE_AA,
                    color=(0, 220, 235), thickness=int(fontsize*3 if arg.bold else fontsize*2))
        cv2.putText(**text_args)

        text_args.update(dict(color=(0, 0, 255), thickness=int(fontsize if arg.bold else fontsize//2)))
        cv2.putText(**text_args)

        # cv2.putText(result, f'{args.prefix}{(f"%0{args.digits}d" % (i+args.offset))}', org=(x-30, y+8), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=FONT_SIZE[arg.fontsize], color=(0, 0, 255), thickness=(2 if arg.bold else 1))
    return result

def render_info(text_args):
    info = f'Size={text_args.fontsize} / #{text_args.index} / Bold={text_args.bold}'
    cv2.setWindowTitle('frame', info)
    print(info)
    # H, W = image.shape[:2]
    # image = image.copy()
    # cv2.putText(image, str(args), org=(0, 0), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0, 255, 0), thickness=1)
    # return image


def main(args):
    # path: str, prefix: str = '', offset: int = 0):
    
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', 1600, 1280)
    
    text_args = EasyDict({
        'fontsize': 4,
        'bold': True,
        'index': args.offset
    })
    
    
    image_o = cv2.imread(args.file)
    H, W = image_o.shape[:2]

    if W > 6000 or H > 4000:
        ratio = min(6000/W, 4000/H)
        image_o = cv2.resize(image_o, fx=ratio, fy=ratio, dsize=None)

    image_rendered = image_o.copy()

    clicked = []

    def mouse_callback(event):
        if event == cv2.EVENT_LBUTTONUP:
            text_args.index += 1
        elif event == cv2.EVENT_MBUTTONUP:
            text_args.index -= 1
        render_info(text_args)

    cv2.setMouseCallback('frame', on_mouse(clicked, text_args, callback=mouse_callback))

    while True:
        image_rendered = update_image(image_o, clicked, args)
        # print(image_rendered)
        # image_show = render_info(image_rendered, args)
        # print(image_show)
        cv2.imshow('frame', image_rendered)
        
        ch = cv2.waitKey(1)
        if ch == 27:
            break
        elif ch in [ord(c) for c in '1234567890']:
            text_args.fontsize = int(chr(ch))-1
            render_info(text_args)
        elif ch == ord('b'):
            text_args.bold = not text_args.bold
            render_info(text_args)
        elif ch == ord('-'):
            text_args.index -= 1
            render_info(text_args)
        elif ch == ord('='):
            text_args.index += 1
            render_info(text_args)
        elif ch == ord('s'):
            dir, base = os.path.split(args.file)
            cv2.imwrite(os.path.join(dir, f"{'.'.join(base.split('.')[:-1])}_labeled.png"), image_rendered)
        elif ch == ord('z'):
            if len(clicked) > 0:
                clicked.pop()
                text_args.index -= 1
                render_info(text_args)



if __name__ == '__main__':
    parser = argparse.ArgumentParser("AttendenceTool")
    parser.add_argument(
        "file", help="image file path"
    )
    parser.add_argument(
        "-o",
        "--offset",
        default=0,
        type=int,
        help="offset number",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        default='D',
        type=str,
        help="prefix",
    )
    parser.add_argument(
        "-d",
        "--digits",
        default=2,
        type=int,
        help="digits",
    )

    args = parser.parse_args()

    main(args)
    # main('/home/rangewing/test.avi', os.path.join(os.path.dirname(__file__), 'lane.txt'))
