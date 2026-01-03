from typing import Optional

from fastapi import APIRouter, Depends, status
from schemas.lib import Author, AuthorCreate, Authors
from services.lib import LibService
from utils.cache import get_service

router = APIRouter()


@router.get(
    "/authors",
    response_model=Authors,
    status_code=status.HTTP_200_OK
)
async def authors(
    lib_service: LibService = Depends(get_service(LibService)),
) -> Authors:
    return await lib_service.get_authors()


@router.get(
    "/author/{iid}",
    response_model=Author,
    status_code=status.HTTP_200_OK
)
async def author(
    iid: int,
    lib_service: LibService = Depends(get_service(LibService)),
) -> Author:
    return await lib_service.get_author(iid)


@router.post(
    "/author",
    response_model=Author,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    author: AuthorCreate,
    lib_service: LibService = Depends(get_service(LibService)),
) -> Author:
    return await lib_service.create_author(author)
