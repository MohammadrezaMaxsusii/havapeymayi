from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI()
ALLOWED_IPS = {"192.168.1.1", "203.0.113.42", "127.0.0.1"}

@app.middleware('http')
def responseFormatterMiddleware(request: Request, call_next):
    try:
        response = call_next(request)
        json_compatible_item_data = jsonable_encoder(response)
        return JSONResponse(content=response)
    except Exception as e:
        json_compatible_item_data = jsonable_encoder(response)
        return JSONResponse(content=json_compatible_item_data)
        return response
    
    

class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host  
        if client_ip not in ALLOWED_IPS:
            return Response("Access denied", status_code=403)
        return await call_next(request)
app.add_middleware(IPFilterMiddleware)