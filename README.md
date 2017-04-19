# python-xcall

A Python [x-callback-url](http://x-callback-url.com) client for 
communicating with x-callback-url macOS applications. Depends on the
[xcall](https://github.com/martinfinke/xcall) command line tool. 


## Software compatability
Requires:
- macOS
- python 2.7
- [Ulysses](https://ulyssesapp.com) 2.8
- Uses macOS [xcall](https://github.com/martinfinke/xcall) (included) for x-callback-url support (Thanks Martin Finke!)
- Needs pytest and mock for testing

## Installation
Check it out:
```bash
$ git clone https://github.com/robwalton/python-xcall.git
Cloning into 'python-xcall'...
```

## Try it out
Call a scheme with an action. The reply will be utf-8 un-encoded and then
url unquoted. It will _not_ be turned decoded further into python objects.
```python

>>> import xcall

>>> xcall.xcall('ulysses', 'get-version')
u'{\n  "buildNumber" : "33542",\n  "apiVersion" : "2"\n}\n'
```
A dictionary of key-value pairs can also be provided. Each value will be utf-8
encoded and then url quoted before sendning.

```python
>>> xcall.xcall('ulysses', 'new-sheet', {'text':'My new sheet', 'index':'2'})
```

Notice that although it will
>>> token = ulysses.authorize()
>>> ulysses.set_access_token(token)

>>> library = ulysses.get_root_items(recursive=True)
>>> print library[0]
Group(title='iCloud', n_sheets=0, n_containers=4, identifier='4A14NiU-iGaw06m2Y2DNwA')

>>> print '\n'.join(ulysses.treeview(library[0]))
4A14NiU-iGaw06m2Y2DNwA - iCloud:
hZ7IX2jqKbVmPGlYUXkZjQ -    Inbox:
aFV99jXk9_AHHqZJ6znb8w -       test
d5TuSlVXQwZnIWMN0DusKQ -    ulysses-python-client-playground:
dULx6YXeWVqCZzrpsH7-3A -       test sheet
YHlYv7PlYgtm626haxAF4A -    Project:
...
```
## API calls implemented

- [x]  new-sheet
- [x]  new-group
- [x]  insert
- [x]  attach-note
- [x]  update-note
- [x]  remove-note
- [ ]  attach-image
- [x]  attach-keywords
- [x]  remove-keywords
- [x]  set-group-title
- [x]  set-sheet-title
- [x]  move
- [x]  copy
- [x]  trash
- [x]  get-item
- [x]  get-root-items
- [x]  read-sheet
- [x]  get-quick-look-url
- [x]  open
- [x]  open-all, open-recent, open-favorites
- [x]  authorize


## Licensing & thanks

The code and the documentation are released under the MIT and Creative Commons Attribution-NonCommercial licences respectively. See LICENCE.txt for details.

## TODO

- Do something useful with this
- Add links up to parent groups
- Logging should go somwhere sensible and include level
- Add to PiPy
  - complete setup.py
  - document testing
- implement attach-image call

  
