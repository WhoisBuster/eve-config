# eve-config

[![Build Status](https://travis-ci.org/WhoisBuster/eve-config.svg?branch=master)](https://travis-ci.org/WhoisBuster/eve-config)

`eve-config` is a Python package for the [Eve](https://github.com/nicolaiarocci/eve) framework that helps you abolish the `settings.py` as much as possible, and provides simpler loading of configuration variables from the environment.

## Installing

To install **eve-config**, you will most likely want to install from Pip (and include it in your project).

```sh
pip install eve-config
```

## Usage

`eve-config` is designed to be used in replacement (or integrated with) your `settings.py`. Here is an example of what you can do with `eve-config`:

```python
from eve import Eve
from eve_config import EveConfig

# Create a new configuration
config = EveConfig()

# Detect variables from the environment (or with the alias)
config.detect('DATABASE_URL', required=True)
config.d('IS_PRODUCTION', default=False)

# Register a resource (e.g., books)
config.resource('books', {})

# Create the Eve application
app = Eve(settings=config.settings)
```

And for a better example, here's the output of `config.settings`:

```python
{
     'APP_NAME': 'your-app',
     'DATABASE_URL': 'your://db@here',
     'IS_PRODUCTION': False,
     'DOMAIN': {
         'books': {},
     }
}
```


### Setting Values

`eve-config` has sensible defaults when attempting to detect configuration values from the environment, always preferring user-set values to `os.environ`.

But here's a quick example for the basics of how you can set variables in `eve-config`:

```python
from eve import Eve
from eve_config import EveConfig
import os

# Create new config
config = EveConfig()

# Explicitly setting values (these are the same)
config.set('TEST_1', True)
config['TEST_1'] = False

print(config['TEST_1'])
# False

# Or try and detect one from the environment.
# If it's set in the environment, use that value.
db_url_fb = config.detect('DATABASE_URL', default='/dev/null')
os.environ['DATABASE_URL'] = 'redis://'
db_url = config.detect('DATABASE_URL', default='/dev/null')

print([db_url_fb, db_url])
# ['/dev/null', 'redis://']

# .d() is an alias for .detect()
config.d('APP_NAME', default='default-app')

# You can even manipulate the configuration key
# Find WRONG_NAME in the environment, and set it to RIGHT_NAME
os.environ['WRONG_NAME'] = 'lol'
config.d('WRONG_NAME', default=False, config_key='RIGHT_NAME')

print(config.get('RIGHT_NAME'))
# 'lol'

# Neat!
```

#### `set(...)`

The set() method sets a simple configuration value based off of the key provided.

Example:

```python
from eve_config import EveConfig

config = EveConfig()

# Use the method
config.set('A', 'a')
print(config.get('A'))
# 'a'

# Or use the magic method
config['A'] = 'b'
print(config.get('A'))
# 'b' 
```


### Getting Values

Retrieving values from the `EveConfig` instance is easy.

Example:

```python
from eve_config import EveConfig

config = EveConfig(app_name='example-app')

print(config.get('APP_NAME'))
# 'example-app'
print(config['APP_NAME'])
# 'example-app'

# Warning: An IndexError is thrown with the bracket syntax
no_exist = config['NO_EXIST']
# raise IndexError: 'NO_EXIST' is not a valid configuration value

```



### Environment Setup

One of `eve-config`'s primary features is the ability to use `.env` files in your application root. These **should be excluded via `.gitignore`**, and are meant to not be committed to source control.

Here's an example of a working Eve app using `eve-config`:

**`app/.env`**
```
DATABASE_URL=postgres://user:secret@host/db_name
DEBUG=1
```

**`app/eve.py`**

```python
from eve import Eve
from eve_config import EveConfig

config = EveConfig()
config.d('DATABASE_URL', required=True)
config.d('DEBUG', default=False)

app = Eve(settings=config.settings)

if __name__ == '__main__':
	# For example use
	settings = config.settings
	print('DB: {}\nDebug: {}'.format(settings['DATABASE_URL'], settings['DEBUG'])

	# Run the Eve app
    app.run()
```

Now, if you run the app from your terminal:
```bash
$ python app/eve.py
DB: postgres://user:secret@host/db_name
Debug: 1
 * Starting...

# You can override them at the prompt too!
$ DATABASE_URL='redis://' python app/eve.py
DB: redis://
Debug: 1
 * Starting...
```



### Detecting Values

#### `detect(...)` or `d(...)`

`d()` is an alias for the `detect()` method, as it's somewhat shorter to write.

When calling `.detect()`, note that it will search the environment for the variable and set it appropriate, **at the time it is called**. This means that if it is not loaded into the environment, it will not be found. (see the *Environment Setup* section for more information).

Example:

```python
from eve_config import EveConfig
import os

config = EveConfig()

os.environ['DATABASE_URL'] = 'abc'
os.environ['IS_PRODUCTION'] = True

# detect()/d() search the environment at call time
config.d('DATABASE_URL', required=True)
config.d('IS_PRODUCTION', default=False)

print(config.settings)
# { 'DATABASE_URL': 'abc', 'IS_PRODUCTION': True }
```

## License

Licensed under the [CC 4.0 Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).

Copyright &copy; 2016 WhoisBuster