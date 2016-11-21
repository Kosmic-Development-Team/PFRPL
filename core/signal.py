from util.supplier import Supplier
from util.utility import *
import core.stream as instream


class Signal(instream.Stream, Supplier):

    def __init__(self, value):
        super(Signal, self).__init__()
        self._value = value

    def __runall(self, u, s):
        u(self.get())
        s.set(self.get())

    def __runifelif(self, u, s):
        if u(self.get()):
            s.set(self.get())
        else:
            s.destroy()

    def __runif(self, u, s):
        if u(self.get()):
            s.set(self.get())

    def set(self, *values):
        for value in list(values):
            self._value = value
            self.run()

    def get(self):
        return self._value

    def edit(self, unaryoperator):
        self.set(unaryoperator(self.get()))

    def mapsignal(self, unaryfunc):
        return self.map(lambda: unaryfunc(self.get()))

    def reducesignal(self, value, bifunc):
        return self.withstream(Signal(value), lambda s: s.edit(lambda v: bifunc(self.get(), v)))

    def foreach(self, unaryoperator):
        return self.withstream(Signal(self.get()), lambda s: self.__runall(unaryoperator, s))

    def untilsignal(self, signal):
        return self.until(lambda: signal.get())

    def untilsignalbool(self, unaryfunc):
        v = None
        if unaryfunc(self.get()):
            v = self.get()
        return self.withstream(Signal(v), lambda s: self.__runifelif(unaryfunc, s))

    def filtersignal(self, signal):
        return signal.addchild(self.filtersignalbool(lambda x: signal.get()))

    def filtersignalbool(self, unaryfunc):
        v = None
        if unaryfunc(self.get()):
            v = self.get()
        return self.withstream(Signal(v), lambda s: self.__runif(unaryfunc, s))

    def doforeach(self, unaryoperator):
        unaryoperator(self.get())
        return self.withstream(Signal(self.get()), lambda s: self.__runall(unaryoperator, s))

    def find(self, unaryfunc):
        return self.filtersignalbool(unaryfunc).first(1)
