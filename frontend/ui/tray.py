from qt.core import QObject, QIcon, QAction, QSystemTrayIcon, QMenu, Signal


class SystemTray(QObject):
    showTriggered = Signal()

    def __init__(self, app, parent=None):
        super().__init__(parent)

        self.tray = QSystemTrayIcon(QIcon(':/qml/resources/icons/app/app.ico'), app)
        self.tray.activated.connect(self._onActivated)

        self.menu = QMenu()
        self.show_action = QAction('Show')
        self.show_action.setVisible(False)
        self.quit_action = QAction('Quit')

        self.show_action.triggered.connect(self.showTriggered)
        self.quit_action.triggered.connect(app.quit)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def show(self):
        self.tray.show()

    def setShowActiveVisible(self, value: bool):
        self.show_action.setVisible(value)

    def _onActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showTriggered.emit()
