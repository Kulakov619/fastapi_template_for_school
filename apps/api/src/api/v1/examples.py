from fastapi import APIRouter, status, Depends
from typing import Optional
from schemas.examples import ExampleResponse
from services.examples import ExamplesService
from utils.cache import get_service
from utils.cache import get_service


router = APIRouter()


@router.get(
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


@router.get(
    "/service/{data}",
    response_model=ExampleResponse,
    status_code=status.HTTP_200_OK
)
async def example(
    data: str,
    ex_service: ExamplesService = Depends(get_service(ExamplesService)),
) -> ExampleResponse:
    return await ex_service.get_example(data)
