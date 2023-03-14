import sys

from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsRectItem, QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem


class GraphicsRectItem(QGraphicsRectItem):
    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8
    handleCorners = [1, 3, 6, 8]

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, *args, handleSize=10, rows=3, columns=2):
        """
        Initialize the shape.
        """
        super().__init__(*args)
        self.handleSize = handleSize
        self.rows = int(rows)
        self.columns = int(columns)
        self.handles = {}
        self.lines = {}
        self.handleSelected = None
        self.handleHovered = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.updateHandlesPos()

    def getSections(self):
        sections = []
        rect = self.rect().translated(self.pos())
        scene_width = self.scene().width()
        scene_height = self.scene().height()
        section_width = rect.width()/self.columns
        section_height = rect.height()/self.rows
        for j in range(self.rows):
            column = []
            for i in range(self.columns):
                p1 = QPointF((rect.left() + section_width*i)/scene_width,
                             (rect.top() + section_height*j)/scene_height)
                p2 = QPointF((rect.left() + section_width*(i+1))/scene_width,
                             (rect.top() + section_height*(j+1))/scene_height)
                column.append(QRectF(p1, p2))
            sections.append(column)
        return sections

    def setRows(self, rows):
        self.rows = int(rows)
        self.lines = {}
        self.updateHandlesPos()
        self.update()

    def setColumns(self, columns):
        self.columns = int(columns)
        self.lines = {}
        self.updateHandlesPos()
        self.update()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        handle = self.handleAt(moveEvent.pos())
        self.handleHovered = handle
        cursor = Qt.SizeAllCursor if handle is None else self.handleCursors[handle]
        self.setCursor(cursor)
        self.update()
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.handleHovered = None
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.rect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def itemChange(self, change, value):
        if change == self.ItemPositionChange and self.scene():
            scene = self.scene().sceneRect()
            rect = self.rect()
            if rect.translated(value).left() < scene.left():
                value.setX(scene.left() - rect.left())
            elif rect.translated(value).right() > scene.right():
                value.setX(scene.right() - rect.right())
            if rect.translated(value).top() < scene.top():
                value.setY(scene.top() - rect.top())
            elif rect.translated(value).bottom() > scene.bottom():
                value.setY(scene.bottom() - rect.bottom())
            return value

        return QGraphicsItem.itemChange(self, change, value)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.rect()
        self.handles[self.handleTopLeft] = QRectF(QPointF(b.left(), b.top()),
                                                  QPointF(b.left() + s, b.top() + s))
        self.handles[self.handleTopMiddle] = QRectF(QPointF(b.left() + s, b.top()),
                                                    QPointF(b.right() - s, b.top() + s))
        self.handles[self.handleTopRight] = QRectF(QPointF(b.right() - s, b.top()),
                                                   QPointF(b.right(), b.top() + s))
        self.handles[self.handleMiddleLeft] = QRectF(QPointF(b.left(), b.top() + s),
                                                     QPointF(b.left() + s, b.bottom() - s))
        self.handles[self.handleMiddleRight] = QRectF(QPointF(b.right() - s, b.top() + s),
                                                      QPointF(b.right(), b.bottom() - s))
        self.handles[self.handleBottomLeft] = QRectF(QPointF(b.left(), b.bottom() - s),
                                                     QPointF(b.left() + s, b.bottom()))
        self.handles[self.handleBottomMiddle] = QRectF(QPointF(b.left() + s, b.bottom() - s),
                                                       QPointF(b.right() - s, b.bottom()))
        self.handles[self.handleBottomRight] = QRectF(QPointF(b.right() - s, b.bottom() - s),
                                                      QPointF(b.right(), b.bottom()))

        for i in range(1, self.rows):
            y = b.top() + i * b.height() / self.rows
            self.lines[i - 1] = QLineF(QPointF(b.left(), y), QPointF(b.right(), y))
        for i in range(1, self.columns):
            x = b.left() + i * b.width() / self.columns
            self.lines[self.rows + i - 2] = QLineF(QPointF(x, b.top()), QPointF(x, b.bottom()))

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        rect = self.rect()
        diff = mousePos - self.mousePressPos
        scene = self.scene().sceneRect()

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:
            rect.setTopLeft(self.mousePressRect.topLeft() + diff)

        elif self.handleSelected == self.handleTopMiddle:
            rect.setTop(self.mousePressRect.top() + diff.y())

        elif self.handleSelected == self.handleTopRight:
            rect.setTopRight(self.mousePressRect.topRight() + diff)

        elif self.handleSelected == self.handleMiddleLeft:
            rect.setLeft(self.mousePressRect.left() + diff.x())

        elif self.handleSelected == self.handleMiddleRight:
            rect.setRight(self.mousePressRect.right() + diff.x())

        elif self.handleSelected == self.handleBottomLeft:
            rect.setBottomLeft(self.mousePressRect.bottomLeft() + diff)

        elif self.handleSelected == self.handleBottomMiddle:
            rect.setBottom(self.mousePressRect.bottom() + diff.y())

        elif self.handleSelected == self.handleBottomRight:
            rect.setBottomRight(self.mousePressRect.bottomRight() + diff)

        if rect.translated(self.pos()).left() < scene.left():
            rect.setLeft(scene.left() - self.pos().x())
        elif rect.translated(self.pos()).right() > scene.right():
            rect.setRight(scene.right() - self.pos().x())
        if rect.translated(self.pos()).top() < scene.top():
            rect.setTop(scene.top() - self.pos().y())
        elif rect.translated(self.pos()).bottom() > scene.bottom():
            rect.setBottom(scene.bottom() - self.pos().y())

        rect = rect.normalized()
        self.setRect(rect)

        self.updateHandlesPos()

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.drawRect(self.rect())
        for line in self.lines.values():
            painter.drawLine(line)

        if self.handleHovered:
            painter.drawRect(self.handles[self.handleHovered])
        else:
            for handle in self.handleCorners:
                painter.drawRect(self.handles[handle])


def main():
    app = QApplication(sys.argv)

    grview = QGraphicsView()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)

    scene.addPixmap(QPixmap('01.png'))
    grview.setScene(scene)

    item = GraphicsRectItem(0, 0, 200, 200, handleSize=50)
    item.setPos(100, 100)
    scene.addItem(item)

    grview.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    grview.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
