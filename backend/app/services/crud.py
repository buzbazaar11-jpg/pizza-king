"""Generic admin CRUD router factory: list / get / create / update / delete for any model."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db


def to_dict(obj: Any) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def crud_router(model, prefix: str, read_dep, write_dep, readonly_fields=("id", "created_at"),
                public_filter=None) -> APIRouter:
    r = APIRouter(prefix=prefix, tags=[prefix.strip("/")])
    cols = {c.name for c in model.__table__.columns} - set(readonly_fields)

    @r.get("")
    async def list_items(db: AsyncSession = Depends(get_db), _=Depends(read_dep), limit: int = 500, offset: int = 0):
        q = select(model)
        if public_filter is not None:
            q = q.where(public_filter)
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return [to_dict(x) for x in rows]

    @r.get("/{item_id}")
    async def get_item(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(read_dep)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return to_dict(obj)

    @r.post("", status_code=201)
    async def create_item(payload: dict, db: AsyncSession = Depends(get_db), _=Depends(write_dep)):
        obj = model(**{k: v for k, v in payload.items() if k in cols})
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return to_dict(obj)

    @r.patch("/{item_id}")
    async def update_item(item_id: str, payload: dict, db: AsyncSession = Depends(get_db), _=Depends(write_dep)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        for k, v in payload.items():
            if k in cols:
                setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return to_dict(obj)

    @r.delete("/{item_id}", status_code=204)
    async def delete_item(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(write_dep)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        await db.delete(obj)
        await db.commit()

    return r
