from core.supplier import Supplier
from util.utility import *
import core.stream as instream


class Signal(instream.Stream, Supplier):

    def __init__(self, value):
        super(Signal, self).__init__()
        self._value = value

    def __lambda0(self, u, s):
        u(self.get())
        s.set(self.get())

    def __lambda1(self, u, s):
        if u(self.get()):
            s.set(self.get())
        else:
            s.destroy()

    def __lambda2(self, u, s):
        if u(self.get()):
            s.set(self.get())

    def set(self, *values):
        for value in list(values):
            self._value = value
            self.run()

    def get(self):
        return self._value

    def edit(self, unaryoperator):
        if islambda(unaryoperator, 1):
            self.set(unaryoperator(self.get()))
        else:
            invalidtypes(unaryoperator)

    def mapsignal(self, unaryfunc):
        if islambda(unaryfunc, 1):
            return self.map(lambda: unaryfunc(self.get()))
        invalidtypes(unaryfunc)

    def reducesignal(self, value, bifunc):
        if islambda(bifunc, 2):
            return self.withstream(Signal(value), lambda s: s.edit(lambda v: bifunc(self.get(), v)))
        invalidtypes(bifunc)

    def foreach(self, unaryoperator):
        if islambda(unaryoperator, 1):
            return self.withstream(Signal(self.get()), lambda s: self.__lambda0(unaryoperator, s))
        invalidtypes(unaryoperator)

    def untilsignal(self, signal):
        if isinstance(signal, Signal):
            return self.until(lambda: signal.get())

    def untilsignalbool(self, unaryfunc):
        if islambda(unaryfunc, 1):
            v = None
            if unaryfunc(self.get()):
                v = self.get()
            return self.withstream(Signal(v), lambda s: self.__lambda1(unaryfunc, s))
        invalidtypes(unaryfunc)

    def filtersignal(self, signal):
        if isinstance(signal, Signal):
            return signal.addchild(self.filtersignalbool(lambda x: signal.get()))
        invalidtypes(signal)

    def filtersignalbool(self, unaryfunc):
        if islambda(unaryfunc, 1):
            v = None
            if unaryfunc(self.get()):
                v = self.get()
            return self.withstream(Signal(v), lambda s: self.__lambda2(unaryfunc, s))
        invalidtypes(unaryfunc)

    def doforeach(self, unaryoperator):
        if islambda(unaryoperator, 1):
            unaryoperator(self.get())
            return self.withstream(Signal(self.get()), lambda s: self.__lambda0(unaryoperator, s))
        invalidtypes(unaryoperator)

    def find(self, unaryfunc):
        if islambda(unaryfunc):
            return self.filtersignalbool(unaryfunc).first(1)
        invalidtypes(unaryfunc)
