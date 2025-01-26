import paramiko
from typing import List, Tuple, Literal
import paramiko


class SessionManager:
    clients: List[Tuple[str, paramiko.Channel]] = []

    def getKey(
        self,
        clientId: str,
        deviceId: int,
        deviceType: Literal["switch", "router"],
    ) -> str:
        return str(f"{deviceType.upper()}_{deviceId}:{clientId}")

    def setClient(self, key: str, client: paramiko.Channel):
        self.clients.append((key, client))

    def getClient(self, key: str) -> paramiko.Channel:
        for k, client in self.clients:
            if k == key:
                return client

    def hasClient(self, key: str):
        for k, client in self.clients:
            if k == key:
                return True

        return False
