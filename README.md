# Ceryle
Ceryle is task-based command runner tool.
Define tasks as DSL in `CERYLE` file.  The DSL is based on python dictionay form and can be extended with python code.

# Getting Started
## Prerequisites
* Python 3.6 or later

## Installation
```sh
$ pip install ceryle
```

## Usage
First, write `CERYLE` file like following.

```python
context = '.'
default = 'foo'

{
    'foo': {
        'dependencies': ['bar'],
        'tasks': [{
            'run': command(['echo', 'first'])
        }, {
            'run': command(['echo', 'next'])
        }]
    },
    'bar': {
        'tasks': [{
            'run': command(['echo', 'preproces'])
        }]
    }
}
```

Next, run `ceryle` command at the same location with `CERYLE` file.

```sh
$ ceryle
# outputs
preprocess
first
next
```

If you want to run only tasks in `bar` group, run with group name.

```sh
$ ceryle bar
# outputs
preprocess
```

## Syntax Suger
Can write task definition simply.

```python
{
    'foo': {
        'dependencies': ['bar'],
         # needless to write with dictionary form if no spec for tasks
        'tasks': [
            # not array form
            command('echo first'),
            command('echo next')
        ]
    },
    # more simpler
    'bar': [
        command('echo preproces')
    ]
}
```
