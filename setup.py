from setuptools import setup, find_packages

setup(name='AttendanceTool', 
      version='0.4.1', 
      packages=find_packages(),
      author="RangeWING",
      author_email="rangewing@kaist.ac.kr",
      install_requires=['numpy', 'ipycanvas', 'easydict', 'Pillow', 'ipykernel'])