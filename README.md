# AttendanceTool
* click to put auto-numbered texts

## Installation
```pip install git+https://github.com/RangeWING/AttendanceTool.git```

## How to use
Run the code below on Jupyter notebook. 

Of course you can run it on Google Colab.

```python
from attendance import *
image_path = './images/' # path to images to label
tool = AttendanceTool(image_path)
tool.display()
```

### Colab Usage
1. Click the link below:
  https://colab.research.google.com/github/RangeWING/AttendanceTool/blob/main/attendance.ipynb

2. Upload your images.
3. Run and enjoy!


### Shortcuts
When it does not work, click the canvas once again.

**Functions**
* `z`: undo
* `c`: clear
* `s`: save
* `r`: rotate CCW
* `t`: rotate CW
* `o`: label mode
* `p`: remove mode

**Labels**
* `1`~`9`: font size shortcuts
* `0`: set index to 0
* `+` or `=`: increase index by 1
* `-`: decrease index by 1