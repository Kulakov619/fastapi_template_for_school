from typing import Optional

import uvicorn
from fastapi import FastAPI


app = FastAPI(
    title="Simple API",
    description="Simple API",
    version="1.0",
)

@app.get(
    '/{name}',
    tags=['special methods'],
    summary='Приветствие автора',
    description='Описание',
    response_description='Описание вывода'
    )
def read_root(
        name: str,
        age: Optional[int] = None) -> dict:
    result = f"{name} {age}"
    return {'Hello': result}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)