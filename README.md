# Fork

This is a fork from
[flask-autoindex](https://github.com/general03/flask-autoindex) 
with minimal changes to make it work with 
[Quart](https://quart.palletsprojects.com).

## Requirements

* ~Flask~ Quart
* Python >= 3.6

## Issues

* Latest `master` branch is not working right now with my local
Python, it probably won't work on yours.

* There is no PyPI package available, and references in this project
are still called `flask_autoindex`. Someday I may get to rename and
publish this properly.

* Tests have not been updated either.

* Icons don't show up. To fix this I would need to port the
`flask-silk` package, which is not mantained. A simpler solution
without dependencies would be better.

## Install

This branch is usable:

```
pip install 'git+https://github.com/ternstor/quart-autoindex.git@use_future_on_entry'
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