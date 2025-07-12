from dataclasses import fields


class DataclassTypeError(Exception):
    pass


class DataclassTypeValidation:
    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            value_type = type(value)
            if not isinstance(value, field.type):
                raise TypeError(
                    'Invalid value type '
                    f'({value_type.__name__} != {field.type.__name__})'
                )

            validation_func_name = f'validate_{field.name}'
            if hasattr(self, validation_func_name):
                var = getattr(self, validation_func_name)
                if callable(var):
                    var(value)

    def raise_error(self, message: str):
        raise DataclassTypeError(message)
