from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt


class NavigationNode(object):  

    
    def __init__(self, data):  
        self._data      = data
        self.obj_data   = None
    
        if type(data) == tuple:  
            self._data = list(data)  
        
        self._data          = [data]  
        self._columncount   = len(self._data)  
        self._children      = []  
        self._parent        = None  
        self._row           = 0  


    def data(self, column):  
        if column >= 0 and column < len(self._data):  
            return self._data[column]


    def columnCount(self):  
        return self._columncount


    def childCount(self):  
        return len(self._children)


    def child(self, row):  
        if row >= 0 and row < self.childCount():  
            return self._children[row]  


    def parent(self):  
        return self._parent


    def row(self):  
        return self._row 


    def addChild(self, child):  
        child._parent       = self  
        child._row          = len(self._children)  
        self._columncount   = max(child.columnCount(), self._columncount)  
        self._children.append(child)  


class NavigationModel(QAbstractItemModel):


    def __init__(self, nodes):
        QAbstractItemModel.__init__(self)
        self._root = NavigationNode(None)
        for node in nodes:
            self._root.addChild(node)
  

    def rowCount(self, index):
        return index.internalPointer().childCount()  if index.isValid() else self._root.childCount()


    def index(self, row, column, i_parent = None):
        parent = self._root if not i_parent or not i_parent.isValid() else i_parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, i_parent):
            return QModelIndex()

        child = parent.child(row)
        return QAbstractItemModel.createIndex(self, row, column, child) if child else QModelIndex()


    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QModelIndex()
      

    def columnCount(self, index):  
        return index.internalPointer().columnCount() if index.isValid() else self._root.columnCount()


    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()  
        return node.data(index.column()) if role == Qt.DisplayRole else None
