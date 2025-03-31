from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
import time
from datetime import datetime
import random
import string
from src.database import get_async_session
from .models import links_table
from .schemas import LinkCreate
from fastapi_cache import FastAPICache

from fastapi_cache.decorator import cache


router = APIRouter(
    prefix="/links",
    tags=["Booking"]
)


@router.get("/{short_code}")
@cache(namespace="link:{short_code}", expire=60)
async def get_original_link(short_code: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(links_table.c.full_link).where(links_table.c.short_link == short_code)
        result = await session.execute(query)
        return {
            "status": "success",
            "data": result.scalars().all()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })

@router.delete("/{short_code}")
async def delete_link(short_code: str, session: AsyncSession = Depends(get_async_session)):
    try:
        statement = delete(links_table).where(links_table.c.short_link == short_code)
        await session.execute(statement)
        await session.commit()
        await FastAPICache.clear(namespace=f"link:{short_code}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })

@router.put("/{short_code}")
async def update_link(short_code: str, new_link:str,session: AsyncSession = Depends(get_async_session)):
    try:
        query = update(links_table).where(links_table.c.short_link == short_code).values(full_link=new_link)
        await session.execute(query)
        await session.commit()
        await FastAPICache.clear(namespace=f"link:{short_code}")
        return {"status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })
    

@router.get("/{short_code}/stats")
async def check_links(short_code: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(links_table.c.clicks).where(links_table.c.short_link == short_code)
        result = await session.execute(query)
        return {
            "status": "success",
            "data": result.scalars().all()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })
    
@router.post("/shorten")
async def short_alias(request: LinkCreate,session: AsyncSession = Depends(get_async_session)):
    try:        
        query = select(links_table.c.clicks).where(links_table.c.short_link == request.short_link)
        result = await session.execute(query)

        if len(result.scalars().all()) > 0:
            return {
                "status": "fail",
                "data": "This short link already exist!"
                }
        
        query = select(links_table.c.clicks).where(links_table.c.short_link == request.short_link)
        statement = insert(links_table).values(**request.dict())
        await session.execute(statement)
        await session.commit()
        return {"status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })



@router.get('/search/')
@cache(namespace="link:{short_code}", expire=60)
async def search_link(full_link: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(links_table.c.short_link).where(links_table.c.full_link == full_link)
        result = await session.execute(query)
        result = result.scalars().all()
        print(len(result))
        if len(result) !=0:
            return {
                "status": "success",
                "data": result
            }
        else:
            return {
                "status": "fail",
                "data": "There is no alias for this link. You can create one."
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })

@router.get('/long/')
@cache(expire=60)
async def get_long():
    time.sleep(5)
    return 'hello'