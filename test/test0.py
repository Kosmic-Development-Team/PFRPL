from core.destructible import *
from core.stream import *

s = Stream()
s.onrun(lambda: print("Hello World!"))
s.run()