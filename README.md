# AttendanceTool
* click to put auto-numbered texts

### Installation
```pip install git+https://github.com/RangeWING/AttendanceTool.git```

### How to use
Run the code below on Jupyter notebook. 

Of course you can run it on Google Colab.

```python
from attendance import *
image_path = './images/' # path to images to label
tool = AttendanceTool(image_path)
tool.display()
```


### Colab Usage
1. Click 'Open notebook' in the File tab
2. Select 'GitHub'
3. Write https://github.com/RangeWING/AttendanceTool
4. Select `attendance.ipynb` to clone the code.
5. Click 'Copy to Drive' button.
6. Upload your images.
7. Run and enjoy!