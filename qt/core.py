from PySide6.QtCore import (
    Signal,
    Slot,
    Qt,
    QObject,
    QThreadPool,
    QTimer,
    QThread,
    QRect,
    QRectF,
    QPoint,
    QPointF,
    Property,
    QSize,
    QSizeF,
    QEvent,
    QMetaObject,
    Q_ARG,
    QGenericArgument,
    QMetaType,
    QStringListModel,
    QCoreApplication,
    QPropertyAnimation,
    QEasingCurve,
    QtMsgType,
    qInstallMessageHandler,
    QElapsedTimer,
    QUrl,
    QAbstractListModel,
    QModelIndex
)
from PySide6.QtGui import (
    QKeySequence,
    QFont,
    QCursor,
    QPainter,
    QPen,
    QBrush,
    QColor,
    QPainterPath,
    QTextCursor,
    QIntValidator,
    QIcon,
    QRegularExpressionValidator,
    QPixmap,
    QPixmapCache,
    QGuiApplication,
    QDoubleValidator,
    QAction
)
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QGraphicsOpacityEffect,
    QStyleOptionSlider,
    QFileDialog,
    QSystemTrayIcon,
    QMenu
)


class TaskEvent(QEvent):
    def __init__(self, callback):
        super().__init__(QEvent.Type(QEvent.User))
        self.callback = callback


class EventReceiver(QObject):
    def event(self, event):
        if isinstance(event, TaskEvent):
            event.callback()
            return True
        return super().event(event)


class QApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver = EventReceiver()

    def postTask(self, fn):
        self.postEvent(self.receiver, TaskEvent(fn))


class QCoreApplication(QCoreApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver = EventReceiver()

    def postTask(self, fn):
        self.postEvent(self.receiver, TaskEvent(fn))
