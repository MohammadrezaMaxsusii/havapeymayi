import time
import paramiko


class ParamikoManager:
    def empty_channel(session: paramiko.Channel):
        output = ""
        while True:
            if session.recv_ready():
                output += session.recv(1024).decode()
            if output.endswith("$ ") or output.endswith("# "):
                break
        return session

    def exec(session: paramiko.Channel, command: str):
        session.send(command + "\n")
