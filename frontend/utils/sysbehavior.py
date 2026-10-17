from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class SingleInstance(QObject):
    activate_requested = Signal()

    def __init__(self, app_id: str):
        super().__init__()
        self.app_id = app_id
        self.server = None

    def try_run(self) -> bool:
        # Try connecting to an existing server first
        socket = QLocalSocket()
        socket.connectToServer(self.app_id)
        if socket.waitForConnected(200):
            # Another instance exists — tell it to raise itself, then quit
            socket.write(b"activate")
            socket.waitForBytesWritten(200)
            socket.disconnectFromServer()
            return False

        # No instance running — clean up any stale server (e.g. after crash) and become the server
        QLocalServer.removeServer(self.app_id)
        self.server = QLocalServer()
        self.server.newConnection.connect(self._on_new_connection)
        self.server.listen(self.app_id)
        return True

    def _on_new_connection(self):
        conn = self.server.nextPendingConnection()
        if conn:
            conn.readyRead.connect(lambda: self._handle_read(conn))

    def _handle_read(self, conn):
        data = conn.readAll().data()
        if data == b"activate":
            self.activate_requested.emit()
