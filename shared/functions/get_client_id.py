from fastapi import Request


def getClientId(req: Request) -> str | None:
    try:
        return req.headers["clientId"]
    except Exception as e:
        return None
