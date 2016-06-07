class EveConfigException(BaseException):
    pass


class InvalidSettingKeyException(EveConfigException):
    pass


class MissingConfigurationValue(EveConfigException):
    pass
