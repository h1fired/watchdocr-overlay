

class Group:
    def __init__(self, states: tuple):
        self._states = states

    def include(self, state):
        return any((s == state for s in self._states))

    def all(self):
        return self._states


class Var:
    def __init__(self, name: str, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)


class StateEnumMeta(type):
    def __new__(cls, clsname, bases, dct):
        enum_items = {k: v for k, v in dct.items() if not k.startswith('__') and not callable(v)}
        for i, key in enumerate(enum_items.keys()):
            dct[key] = 1 << i
            enum_items[key] = 1 << i

        _cls = super().__new__(cls, clsname, bases, dct)
        _cls.__states__ = enum_items

        # Init
        def new_init(self, *args, **kwargs):
            # Create flags
            flags = {}
            for key in enum_items.keys():
                flags[key] = False
            self._flags = flags

            # Create groups
            groups = []
            if _cls.Meta.groups == '__all__':
                g = Group(list(enum_items.values()))
                groups.append(g)
            else:
                for group in _cls.Meta.groups:
                    g = Group([enum_items[item] for item in group])
                    groups.append(g)
            self._groups = groups

        _cls.__init__ = new_init

        return _cls

    def __iter__(cls):
        return iter([Var(k, v) for k, v in cls.__states__.items()])


class StateEnum(metaclass=StateEnumMeta):

    def set(self, state: str | int, value=True):
        nstate = state
        if isinstance(state, int):
            s = next(
                (key for key, value in self.__states__.items() if value == state),
                None
            )
            nstate = s

        for group in self._groups:
            if group.include(self.__states__[nstate]):
                for s in group.all():
                    key = next((k for k, v in self.__states__.items() if v == s), None)
                    if key:
                        self._flags[key] = False

        self._flags[nstate] = value

    def flags(self):
        state = 0
        for key, flag in self._flags.items():
            if flag is True:
                state |= self.__states__[key]
        return state

    def __str__(self):
        included_states = []
        value = self.flags()
        for key, state in self.__states__.items():
            if value & state:
                included_states.append(key)

        return f'{self.__class__.__name__}({"|".join(included_states)})'

    def __repr__(self):
        return self.__str__()

    def __and__(self, other):
        return self.flags() & other

    def __rand__(self, other):
        return other & self.flags()

    def __or__(self, other):
        return self.flags() | other

    def __ror__(self, other):
        return other | self.flags()

    class Meta:
        groups = tuple()


class default:
    def __new__(cls):
        return None
