class Destructible:

    def __init__(self):
        self._parents = []
        self._children = []
        self.destroyed = False

    def addchild(self, child):
        if child not in self._children:
            self._children.append(child)
            child.__addparent(self)
        return child

    def __addparent(self, parent):
        if parent not in self._parents:
            self._parents.append(parent)
            parent.addchild(self)

    def removechild(self, child):
        if child in self._children:
            self._children.remove(child)
        if not self._children:
            self.destroy()

    def __removeparent(self, parent):
            if parent in self._parents:
                self._parents.remove(parent)

    def destroy(self):
        if not self.destroyed:
            self.destroyed = True
            all(parent.removechild(self) for parent in self._parents)
            all(child.__removeparent(self) for child in self._children)
        self._parents.clear()
        self._children.clear()
