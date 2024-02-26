# AttendanceTool
* click to put auto-numbered texts
* G

### Dependency
```pip install opencv-python numpy easydict Pillow```

### Arguments
* -o: offset number (default: 0)
* -p: prefix (default: '')
* -d: minimum digits (default: 2)

#### Example
* Starts from 0, number format A0 \
  ``` python numbering.py -o 0 -p A  ```
* Starts from 22, number format D000 \
  ``` python numbering.py -o 22 -p D -d 3 ```



### Basic 


### Commands
* left click: add label
* middle click: remove nearest one
* 1~9: font size
* b: bold on/off
* z: undo
* s: save image (to 'result.png')
* ESC: quit
