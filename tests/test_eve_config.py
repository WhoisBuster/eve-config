from tests import TestCase

from eve_config import EveConfig
from eve_config.exceptions import InvalidSettingKeyException, MissingConfigurationValue

import os


class TestEveConfig(TestCase):
    def test_construct(self):
        config = EveConfig()

        self.assertIsNotNone(config)
        self.assertTrue(isinstance(config.configuration, dict))

    def test_construct_with_kwargs(self):
        config = EveConfig(secret_key='chocolate')

        self.assertIsNotNone(config)
        self.assertEqual('chocolate', config['SECRET_KEY'])

    def test_get(self):
        config = EveConfig()

        config.set('ITEM_A', 1)
        config['ITEM_B'] = 2

        def invalid_get():
            return config['ITEM_C']

        self.assertEqual(1, config['ITEM_A'])
        self.assertEqual(2, config['ITEM_B'])
        self.assertRaises(IndexError, invalid_get)

    def test_set(self):
        config = EveConfig()
        config.set('VALID_KEY', '123')
        config['ANOTHER_KEY'] = True

        self.assertEqual('123', config.get('VALID_KEY'))
        self.assertTrue(config['ANOTHER_KEY'])

    def test_set_invalid_key(self):
        config = EveConfig()

        self.assertRaises(InvalidSettingKeyException, config.set, 'invalid key', '123')

    def test_apply(self):
        config = EveConfig()
        config.apply({'KEY_1': 123, 'KEY_2': 345})

        self.assertEqual(123, config.get('KEY_1'))
        self.assertEqual(345, config.get('KEY_2'))

    def test_apply_invalid_type(self):
        config = EveConfig()

        self.assertRaises(AttributeError, config.apply, True)
        self.assertRaises(AttributeError, config.apply, '')
        self.assertRaises(AttributeError, config.apply, [])

    def test_detect_alias(self):
        config = EveConfig()
        os.environ['TEST_1_D'] = 'abc'

        result = config.d('TEST_1_D')

        self.assertEqual('abc', result)
        self.assertEqual('abc', config.get('TEST_1_D'))

    def test_detect(self):
        config = EveConfig()
        os.environ['TEST_1_DETECT'] = 'abc'

        result = config.detect('TEST_1_DETECT')

        self.assertEqual('abc', result)
        self.assertEqual('abc', config.get('TEST_1_DETECT'))

    def test_detect_already_exists(self):
        config = EveConfig()

        config.set('ALREADY_EXIST', True)
        os.environ['ALREADY_EXIST'] = 'no'

        self.assertTrue(config.detect('ALREADY_EXIST'))

    def test_detect_required(self):
        config = EveConfig()

        self.assertRaises(MissingConfigurationValue, config.detect, 'NOT_FOUND', required=True)

    def test_detect_default(self):
        config = EveConfig()

        self.assertEqual('abc', config.detect('STILL_MISSING', default='abc'))

    def test_settings(self):
        config = EveConfig()
        config.set('ABC', 'def')

        self.assertEqual('def', config.settings.get('ABC'))

    def test_resource_methods(self):
        config = EveConfig()
        config.resource_methods(['GET', 'POST', 'PATCH', 'DELETE'])

    def test_resource_methods_wrong_type(self):
        config = EveConfig()

        self.assertRaises(AttributeError, config.resource_methods, False)
        self.assertRaises(AttributeError, config.resource_methods, '')
        self.assertRaises(AttributeError, config.resource_methods, None)
        self.assertRaises(AttributeError, config.resource_methods, 1)

    def test_resource_methods_invalid_verb(self):
        config = EveConfig()

        self.assertRaises(AttributeError, config.resource_methods, ['JUMP'])

    def test_item_methods(self):
        config = EveConfig()
        config.item_methods(['GET', 'POST', 'DELETE', 'PUT'])

    def test_item_methods_wrong_type(self):
        config = EveConfig()

        self.assertRaises(AttributeError, config.item_methods, False)
        self.assertRaises(AttributeError, config.item_methods, '')
        self.assertRaises(AttributeError, config.item_methods, None)
        self.assertRaises(AttributeError, config.item_methods, 1)

    def test_item_methods_invalid_verb(self):
        config = EveConfig()

        self.assertRaises(AttributeError, config.item_methods, ['JUMP'])

    def test_set_cache(self):
        config = EveConfig()

        config.set_cache(60)
        self.assertEqual('max-age=60', config.get('CACHE_CONTROL'))
        self.assertEqual(60, config.get('CACHE_EXPIRES'))

        config.set_cache(45, 30)
        self.assertEqual('max-age=45', config.get('CACHE_CONTROL'))
        self.assertEqual(30, config.get('CACHE_EXPIRES'))

        config.set_cache(-1, -1)
        self.assertEqual('max-age=20', config.get('CACHE_CONTROL'))
        self.assertEqual(20, config.get('CACHE_EXPIRES'))

    def test_resource(self):
        config = EveConfig()
        config.resource('example1', {'a': 123})

        self.assertEqual({'example1': {'a': 123}}, config.settings.get('DOMAIN'))

    def test_resource_duplicate(self):
        config = EveConfig()
        config.resource('example1', {})

        self.assertRaises(KeyError, config.resource, 'example1', {'a': 'b'})
