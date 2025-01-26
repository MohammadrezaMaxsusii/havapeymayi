from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()


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
