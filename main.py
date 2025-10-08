import uvicorn
from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def read_root():
    return {'Hello': 'FastAPI'}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)