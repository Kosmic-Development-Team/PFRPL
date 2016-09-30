from core.destructible import Destructible
from collections import OrderedDict
from util.utility import *


class Stream(Destructible):

    def __init__(self):
        super(Stream, self).__init__()
        self.__tocall = OrderedDict()

    def addchildterm(self, child, func):
        if isinstance(child, Destructible) and islambda(func, 0):
            super(Stream, self).addchild(child)
            self.__tocall[child] = func
            return child
        invalidtypes(child, func)

    def removechild(self, child):
        super(Stream, self).removechild(child)
        if child in self.__tocall.keys():
            del self.__tocall[child]

    def run(self):
        all(func() for func in self.__tocall.values())

    def onrun(self, func):
        if islambda(func, 0):
            return self.withstream(Stream(), lambda s: lambda0(func, s))

    def withstream(self, stream, action):
        if isinstance(stream, Stream) and islambda(action, 1):
            return self.addchildterm(stream, lambda: action(stream))
        invalidtypes(stream, action)

    def tostream(self):
        return self.withstream(Stream(), lambda s: s.run())

    def combine(self, *streams):
        if isinstance(streams, list):
            if all(isinstance(stream) for stream in streams):
                s = self.tostream()
                all(stream.withstream(s, lambda s: s.run()) for stream in streams)
                return s
        invalidtypes(streams)

def lambda0(func, s):
        func()
        s.run()
