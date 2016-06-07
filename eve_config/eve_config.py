from eve_config.exceptions import MissingConfigurationValue, InvalidSettingKeyException

from dotenv import load_dotenv, find_dotenv

import os
import re


class EveConfig(object):
    """
    Creates a new EveConfig configuration object. This class provides
    methods for retrieving, setting, and detecting settings from the
    environment.
    """

    HTTP_VERBS = ['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'DELETE']
    """ list[str]: A list of valid HTTP verbs to use in the resource_methods() and item_methods() """

    SETTING_KEY_REGEX = re.compile(r'^[\w\d_\-]+$')
    """ object: A simple regex to match environment variables """

    def __init__(self, *args, **kwargs):
        """
        We take the kwargs and apply all of the configuration values
        that are provided. They will have precedence over environment
        variables.

        :param *args: The arguments (that we ignore)
        :param **kwargs: The settings collected from kwargs are directly applied
                         to the configuration.
        """

        # database_url: '...' => DATABASE_URL: '...'
        kwargs = {k.upper(): v for k, v in kwargs.items()}

        # Create our configuration starting with the
        self.configuration = kwargs.copy()
        self.apps = []

        env_file = self.detect('ENV_FILE', default='.env')

        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            self.set('ENV_FILE', find_dotenv(env_file))
            load_dotenv(self.get('ENV_FILE'))

    def __getitem__(self, item):
        """
        Override the magic method so that we can have key access
        similar to that of a real dict.

            Example: config['YOUR_KEY']

        :param item: The configuration key to return

        :return: The configuration value (if exists)

        :throws IndexError: The configuration key does not exist
        """

        if item not in self.configuration.keys():
            raise IndexError('\'{}\' was not found in the configuration'.format(item))

        return self.get(item)

    def __setitem__(self, key, value):
        """
        Override the magic method so that we can set values similar
        to that of a real dict.

        Example:
            | config = EveConfig()
            | config['IS_PRODUCTION'] = True

        :param key: The configuration key to set
        :param value: The configuration value to set
        """

        self.set(key, value)

    def get(self, key, default=None):
        """
        Returns a configuration value from the internal
        dictionary.

        :param key: The configuration key
        :param default: The default value if the value is not found

        :return: The value or default value for the configuration key
        """
        return self.configuration.get(key, default)

    def set(self, key, value):
        """
        Sets a configuration value on the internal dictionary

        :param key: The configuration key
        :param value: The new configuration value
        """

        if not re.match(self.SETTING_KEY_REGEX, key):
            raise InvalidSettingKeyException(
                '\'{}\' is not a valid configuration key (example: YOUR_CONFIG_VAR)'.format(key))

        self.configuration[key.upper()] = value

    def apply(self, config):
        """
        Sets multiple configuration values from a dictionary
        containing a key/value list of data.

        :param config: The configuration dictionary
        """

        # Check to make sure it's a dictionary
        if not isinstance(config, dict):
            raise AttributeError('apply() only takes parameter of type dict')

        # Iterate over and apply these settings
        for key, value in config.items():
            self.set(key, value)

    def d(self, env_key, default=None, required=False, config_key=None):
        """
        An alias for the detect() method

        See the detect() method documentation for more information.
        """
        return self.detect(env_key, default, required, config_key)

    def detect(self, env_key, default=None, required=False, config_key=None):
        """
        The detect method allows users to detect settings from the environment
        and set defaults.

        :param env_key:     The environment variable to search for
        :param default:         The default value if not found in the environment
        :param required:        If the value is required, will throw an exception if not found.
        :param config_key:      Defaults to :param:``setting_key``

        :return: The found value, or the default if not found
        """

        environ = os.environ.copy()

        # Let's make sure the environment variable is in all caps and cleaned up
        setting_key = env_key.upper()

        # If it's None, default to env_key
        config_key = config_key if config_key is not None else setting_key

        # If we've already got a configuration value set, then we
        # shouldn't load from the environment. (explicit vs. implied)
        if config_key in self.configuration.keys():
            return self.configuration.get(config_key)

        # Let's search the environment since it's not in the user-supplied list.
        found_in_env = (config_key in environ.keys())

        # If we found it, save it to the running config and return it
        # (it doesn't matter if it returns to the void)
        if found_in_env:
            self.set(config_key, environ.get(config_key))

            return self.configuration[config_key]

        # If we can't find it, and it's required, let's raise an exception
        if required and not found_in_env:
            raise MissingConfigurationValue('The \'{}\' configuration value is required'.format(setting_key))

        # If you're here, it's not required and we can safely return the default.
        return default

    def resource_methods(self, methods):
        """
        Update the list of RESOURCE_METHODS, or valid HTTP verbs
        that resources will allow.

        :param methods: A list of HTTP verbs
        """

        if not isinstance(methods, list):
            raise AttributeError('resource_methods() expects a parameter of type list')

        methods = [str(x).upper().strip() for x in methods]

        for method in methods:
            if method not in self.HTTP_VERBS:
                raise AttributeError('\'{}\' is not a recognized HTTP verb'.format(method))

        self.configuration['RESOURCE_METHODS'] = methods

    def item_methods(self, methods):
        """
        Update the list of ITEM_METHODS, or valid HTTP verbs
        that resources will allow.

        :param methods: A list of HTTP verbs
        """

        if not isinstance(methods, list):
            raise AttributeError('item_methods() expects a parameter of type list')

        methods = [str(x).upper().strip() for x in methods]

        for method in methods:
            if method not in self.HTTP_VERBS:
                raise AttributeError('\'{}\' is not a recognized HTTP verb'.format(method))

        self.configuration['ITEM_METHODS'] = methods

    def set_cache(self, max_age=20, expires=None):
        """
        Sets the cache expiration for the Eve application

        :param max_age: Number of seconds the response is valid for
        :param expires: Number of seconds until the cache expires
        """

        if max_age <= 0:
            max_age = 20

        if expires is None:
            expires = max_age
        elif expires <= 0:
            expires = 20

        self.set('CACHE_CONTROL', 'max-age={}'.format(max_age))
        self.set('CACHE_EXPIRES', expires)

    def resource(self, name, config):
        """
        Registers a new resource (adds it to the DOMAIN configuration
        value automatically)

        :param name: The name of the new resource (e.g., 'books')
        :param config: The dictionary configuration for the resource
        """
        name = name.lower()

        if name in [x.get('name') for x in self.apps]:
            raise KeyError('Refusing to re-define application \'{}\''.format(name))

        self.apps.append({'name': name, 'config': config})

    @property
    def domain(self):
        """
        Generates a configuration dict for the 'DOMAIN' value,
        which specifies the resources available to the API.

        :return: The DOMAIN configuration dict
        """

        return {x.get('name'): x.get('config') for x in self.apps}

    @property
    def settings(self):
        """
        Returns the complete dict of setting values to be passed
        directly to Eve.

        :return: The configuration values
        :rtype: dict
        """

        # Grab our configuration and merge the domains
        data = self.configuration.copy()

        # If the DOMAIN is already specified (overridden) in the
        # configuration, use that. Otherwise, fall back to our generated dict
        data['DOMAIN'] = data.get('DOMAIN', self.domain)

        return data
