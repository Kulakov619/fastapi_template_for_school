import json

from fastapi import HTTPException
from models.lib import Author as AuthorSql
from schemas.lib import Author, AuthorCreate, Authors
from services.mixins import BaseService
from sqlalchemy.future import select
from utils.encode import encode_base64


class LibService(BaseService):

    async def get_authors(self) -> Authors:
        result = await self.db.execute(select(AuthorSql))
        return Authors(
            authors=[
                Author(
                    id=el.id,
                    first_name=el.first_name,
                    last_name=el.last_name
                ) for el in result.scalars().all()
            ]
        )

    async def get_author(self, author_id: int) -> Author:
        cache_key = 'author_key_' + str(author_id)
        cached = await self.check_in_cache(cache_key)
        if cached:
            try:
                data = json.loads(cached.decode("utf-8"))
                return Author(**data)
            except Exception:
                pass

        query = select(AuthorSql).where(AuthorSql.id == author_id)
        result = await self.db.execute(query)
        author_row = result.scalars().first()
        if author_row is None:
            raise HTTPException(status_code=404, detail="Author not found")

        author = Author(
            id=author_row.id,
            first_name=author_row.first_name,
            last_name=author_row.last_name,
        )

        try:
            serialised = json.dumps(author.dict()).encode("utf-8")
            await self.put_in_cache(cache_key, serialised)
        except Exception:
            pass

        return author

    async def create_author(self, author: AuthorCreate) -> Author:
        new_db_author = AuthorSql(
            first_name=author.first_name,
            last_name=author.last_name,
        )
        self.db.add(new_db_author)
        await self.db.commit()
        await self.db.refresh(new_db_author)

        created_author = Author(
            id=new_db_author.id,
            first_name=new_db_author.first_name,
            last_name=new_db_author.last_name,
        )

        cache_key = 'author_key_' + str(new_db_author.id)
        await self.put_in_cache(cache_key, json.dumps(created_author.dict()).encode("utf‑8"))

        return created_author
