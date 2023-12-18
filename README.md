# Fork

This is a fork from
[flask-autoindex](https://github.com/general03/flask-autoindex) 
with minimal changes to make it work with 
[Quart](https://quart.palletsprojects.com).

## Requirements

* ~Flask~ Quart
* Python >= 3.6

## Install

There is no PyPI package available, and references in this project
are still called `flask_autoindex`. I may get to rename and publish
this someday. Meanwhile:

```
pip install 'git+https://github.com/ternstor/quart-autoindex.git'
```

## Usage

```
import os.path
from quart import Quart
from flask_autoindex import AutoIndex

app = Quart(__name__)
AutoIndex(app, browse_root=os.path.curdir)

if __name__ == '__main__':
    app.run()
```

`quart run`

## Test

`python setup.py test`