from qt.core import QObject, QIcon, QAction, QSystemTrayIcon, QMenu


class SystemTray(QObject):
    def __init__(self, window, app):
        super().__init__(window)

        self.tray = QSystemTrayIcon(QIcon("resources/icons/tray.svg"), app)

        self.menu = QMenu()
        self.show_action = QAction("Show")
        self.quit_action = QAction("Quit")

        self.show_action.triggered.connect(window.show)
        self.quit_action.triggered.connect(app.quit)

        self.menu.addAction(self.show_action)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)

    def show(self):
        self.tray.show()
