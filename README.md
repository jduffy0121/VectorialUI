# VectorialUI

## Program Information
*A UI Interface created by Auburn University's AMO Physics Research Group.*  
  
This program looks at cometary data regarding particles that radiate from the coma of the comet before and after coliding with a photon.  
A vectorial model is used to calculate this data (all found in pyvectorial).   
This UI allows users to manually input data, use a pickle, or use a yaml file to run the calculations contained in pyvectorial.  
This package is avaible for anyone to download.  

*Note, do all of the following installations before attempting to run the program*  
  
## Astropy Installation
*Used in FileRunner.py*  
  
Link: [Astropy website](https://docs.astropy.org/en/stable/install.html)  

1. ```conda install astropy ```

2. ``` x conda install -c conda-forge -c defaults scipy matplotlib \ h5py beautifulsoup4 html5lib bleach pandas sortedcontainers \ pytz setuptools mpmath bottleneck jplephem asdf pyarrow ```

## Sbpy Installation
*Used in FileRunner.py*  
  
Link: [Sbpy git](https://github.com/sjoset/sbpy)

1. ```git clone git@github.com:sjoset/sbpy.git```

2. ```cd sbpy/```

3. ``` python setup.py develop --user ```

## Pyvectorial Installation
*Used in FileRunner.py*  
  
Link: [Pyvectorial git](https://github.com/sjoset/pyvectorial)

1. ```git clone git@github.com:sjoset/pyvectorial.git```

2. ```cd pyvectorial/```

3. ```pip install .``` or ```pip install -e .``` for development mode

## PyQt5 Installation
*Used in UICreator.py*  
  
Link: [PyQt website](https://pypi.org/project/PyQt5/)

1. ```pip install pyqt5```

## VectorialUI Installation

1. ```git clone git@github.com:jduffy0121/VectorialUI.git```

2. ```cd vectorial_ui/```

3. ```pip install .``` or ```pip install -e .``` for development mode

## To run the UI
 ```./UICreator.py```