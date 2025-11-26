from api.v1 import examples

import uvicorn
from fastapi import FastAPI


app = FastAPI(
    title="Simple API",
    description="Simple API",
    version="1.0",
)

app.include_router(
    examples.router,
    prefix="/api/v1/examples",
    tags=["examples"],
)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)