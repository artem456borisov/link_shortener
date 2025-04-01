from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
import time
from datetime import datetime
import random
import string
from src.database import get_async_session
from .models import links_table
from .schemas import LinkCreate, BulkLinkCreate, ClickTrackResponse
from fastapi_cache import FastAPICache
from typing import List
from .schemas import BulkLinkCreate

from src.auth.users import User
from src.auth.users import current_active_user

from fastapi_cache.decorator import cache


router = APIRouter(
    prefix="/links",
    tags=["Linker"]
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
async def delete_link(short_code: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
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
async def update_link(short_code: str, new_link:str,session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
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

@router.post("/{short_code}/click")
async def track_link_click(
    short_code: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Track a click on a short link and increment the click counter.
    Returns the full URL for redirection.
    """
    try:
        # First get the current click count
        query = select(links_table.c.full_link, links_table.c.clicks).where(
            links_table.c.short_link == short_code
        )
        result = await session.execute(query)
        link_data = result.fetchone()
        
        if not link_data:
            raise HTTPException(status_code=404, detail={
                "status": "error",
                "data": "Short link not found",
            })
        
        # Increment click count
        stmt = (
            update(links_table)
            .where(links_table.c.short_link == short_code)
            .values(clicks=links_table.c.clicks + 1)
        )
        await session.execute(stmt)
        await session.commit()
        
        return {
            "status": "success",
            "data": {
                "url": link_data.full_link,
                "new_click_count": link_data.clicks + 1
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })

@router.post("/bulk-shorten")
async def bulk_create_short_links(
    requests: List[BulkLinkCreate],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    results = {
        "success": [],
        "failed": []
    }
    
    try:
        for request in requests:
            try:
                exists = await session.execute(
                    select(links_table)
                    .where(links_table.c.short_link == request.short_link)
                )
                
                if exists.scalar():
                    results["failed"].append({
                        "short_link": request.short_link,
                        "reason": "Already exists"
                    })
                    continue
                
                await session.execute(
                    insert(links_table).values(**request.dict())
                )
                results["success"].append(request.short_link)
                
            except Exception as e:
                results["failed"].append({
                    "short_link": request.short_link,
                    "reason": str(e)
                })
        
        await session.commit()
        return {
            "status": "partial_success",
            "data": results
        }
    
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
        })


@router.get('/long/')
@cache(expire=60)
async def get_long():
    time.sleep(5)
    return 'hello'