from collections import OrderedDict

from flow.destructible import Destructible
from flow.supplier import Supplier
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
        self.addchild(child)
        self._tocall[child] = func
        return child

    def removechild(self, child):
        super(Stream, self).removechild(child)
        if child in self._tocall.keys():
            del self._tocall[child]

    def run(self):
        for func in list(self._tocall.values()):
            func()

    def onrun(self, operator):
        return self.withstream(Stream(), lambda s: self.__runall(operator, s))

    def withstream(self, stream, unaryoperator):
        return self.addchildterm(stream, lambda: unaryoperator(stream))

    def tostream(self):
        return self.withstream(Stream(), lambda s: s.run())

    def combine(self, *streams):
        st = self.tostream()
        for stream in list(streams):
            stream.withstream(st, lambda s: s.run())
        return st

    def filter(self, supplier):
        if isinstance(supplier, Supplier):
            return self.withstream(Stream(), lambda s: self.__runif(supplier, s))
        else:
            return self.withstream(Stream(), lambda s: self.__runiflambda(supplier, s))

    def until(self, supplier):
        if isinstance(supplier, Supplier):
            return self.withstream(Stream(), lambda s: self.__runifelif(supplier, s))
        else:
            return self.withstream(Stream(), lambda s: self.__runifeliflambda(supplier, s))

    def count(self):
        return self.reduce(lambda i: i + 1)

    def first(self, n):
        return self.until(self.count().map(lambda i: i <= n))

    def tosignal(self, signal):
            return signal.addchildterm(self.withstream(signal.Signal(signal.get()), lambda s: s.set(signal.get())))

    def map(self, supplier):
        import flow.signal as insignal
        if isinstance(supplier, Supplier):
            return self.withstream(insignal.Signal(supplier.get()), lambda s: s.set(supplier.get()))
        else:
            return self.withstream(insignal.Signal(supplier.get()), lambda s: s.set(supplier()))

    def reduce(self, value, unaryoperator):
        import flow.signal as insignal
        return self.withstream(insignal.Signal(value), lambda s: s.edit(unaryoperator))
