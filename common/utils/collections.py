

class UniqueError(Exception):
    pass


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise UniqueError('Key already exists')
        return super().__setitem__(key, value)
