# python-xcall

A Python [x-callback-url](http://x-callback-url.com) client for 
communicating with x-callback-url enabled macOS applications. Uses the handy
[xcall](https://github.com/martinfinke/xcall) command line tool. 


## Software compatability
Requires:
- macOS
- python 2.7
- Uses macOS [xcall](https://github.com/martinfinke/xcall) (included).
- Needs pytest and mock for testing

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/python-xcall.git
Cloning into 'python-xcall'...
```

## Try it out
Call a `scheme` with an `action`:
```python

>>> import xcall
>>> xcall.xcall('ulysses', 'get-version')
u'{\n  "buildNumber" : "33542",\n  "apiVersion" : "2"\n}\n'
```
The reply will be utf-8 un-encoded and then url unquoted. It will _not_ be
turned decoded further into python objects.

A dictionary of key-value pairs can also be provided (each value is utf-8
encoded and then url quoted before sending):
```python
>>> xcall.xcall('ulysses', 'new-sheet', {'text':'My new sheet', 'index':'2'})
```


## Licensing & thanks

The code and the documentation are released under the MIT and Creative Commons
Attribution-NonCommercial licences respectively.

Thanks to
- [Martin Finke](https://github.com/martinfinke) for his handy [xcall](https://github.com/martinfinke/xcall) application.
- [Dean Jackson](https://github.com/deanishe) for suggestions


  

