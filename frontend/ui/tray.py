from qt.core import QObject, QIcon, QAction, QSystemTrayIcon, QMenu, Signal


class SystemTray(QObject):
    showTriggered = Signal()

    def __init__(self, window, app):
        super().__init__(window)

        self.tray = QSystemTrayIcon(QIcon(':/qml/resource/resources/icons/tray.svg'), app)

        self.menu = QMenu()
        self.show_action = QAction('Show')
        self.quit_action = QAction('Quit')

        self.show_action.triggered.connect(self.showTriggered)
        self.quit_action.triggered.connect(app.quit)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def show(self):
        self.tray.show()
