from collections import OrderedDict

from core.destructible import Destructible
from util.supplier import Supplier
from util.utility import *


class Stream(Destructible):

    def __init__(self):
        super(Stream, self).__init__()
        self._tocall = OrderedDict()

    @staticmethod
    def __runall(operator, s):
        operator()
        s.run()

    @staticmethod
    def __runif(supplier, s):
        if supplier.get():
            s.run()

    @staticmethod
    def __runiflambda(supplier, s):
        if supplier():
            s.run()

    @staticmethod
    def __runifelif(supplier, s):
        if supplier.get():
            s.run()
        else:
            s.destroy()

    @staticmethod
    def __runifeliflambda(supplier, s):
        if supplier():
            s.run()
        else:
            s.destroy()

    def addchildterm(self, child, func):
        if isinstance(child, Destructible) and islambda(func, 0):
            self.addchild(child)
            self._tocall[child] = func
            return child
        invalidtypes(child, func)

    def removechild(self, child):
        super(Stream, self).removechild(child)
        if child in self._tocall.keys():
            del self._tocall[child]

    def run(self):
        for func in list(self._tocall.values()):
            func()

    def onrun(self, operator):
        if islambda(operator, 0):
            return self.withstream(Stream(), lambda s: self.__runall(operator, s))

    def withstream(self, stream, unaryoperator):
        if isinstance(stream, Stream) and islambda(unaryoperator, 1):
            return self.addchildterm(stream, lambda: unaryoperator(stream))
        invalidtypes(stream, unaryoperator)

    def tostream(self):
        return self.withstream(Stream(), lambda s: s.run())

    def combine(self, *streams):
        st = self.tostream()
        for stream in list(streams):
            if isinstance(stream, Stream):
                stream.withstream(st, lambda s: s.run())
            else:
                invalidtypes(stream)
        return st

    def filter(self, supplier):
        if isinstance(supplier, Supplier):
            return self.withstream(Stream(), lambda s: self.__runif(supplier, s))
        elif islambda(supplier, 0):
            return self.withstream(Stream(), lambda s: self.__runiflambda(supplier, s))
        invalidtypes(supplier)

    def until(self, supplier):
        if isinstance(supplier, Supplier):
            return self.withstream(Stream(), lambda s: self.__runifelif(supplier, s))
        elif islambda(supplier, 0):
            return self.withstream(Stream(), lambda s: self.__runifeliflambda(supplier, s))
        invalidtypes(supplier)

    def count(self):
        return self.reduce(lambda i: i + 1)

    def first(self, n):
        if isinstance(n, int):
            return self.until(self.count().map(lambda i: i <= n))
        invalidtypes(n)

    def tosignal(self, signal):
        import core.signal as insignal
        if isinstance(signal, insignal.Signal):
            return signal.addchildterm(self.withstream(signal.Signal(signal.get()), lambda s: s.set(signal.get())))
        invalidtypes(signal)

    def map(self, supplier):
        import core.signal as insignal
        if isinstance(supplier, Supplier):
            return self.withstream(insignal.Signal(supplier.get()), lambda s: s.set(supplier.get()))
        elif islambda(supplier, 0):
            return self.withstream(insignal.Signal(supplier.get()), lambda s: s.set(supplier()))
        invalidtypes(supplier)

    def reduce(self, value, unaryoperator):
        import core.signal as insignal
        if islambda(unaryoperator, 1):
            return self.withstream(insignal.Signal(value), lambda s: s.edit(unaryoperator))
        invalidtypes(unaryoperator)
