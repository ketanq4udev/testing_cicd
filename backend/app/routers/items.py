from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Item
from app import cache

router = APIRouter(prefix="/items", tags=["items"])

CACHE_LIST_KEY = "items:list"
CACHE_ITEM_KEY = "items:{id}"


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    cached = cache.cache_get(CACHE_LIST_KEY, "list_items")
    if cached is not None:
        return cached
    items = db.query(Item).all()
    result = [ItemResponse.model_validate(i).model_dump() for i in items]
    cache.cache_set(CACHE_LIST_KEY, result)
    return result


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    key = CACHE_ITEM_KEY.format(id=item_id)
    cached = cache.cache_get(key, "get_item")
    if cached is not None:
        return cached
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    result = ItemResponse.model_validate(item).model_dump()
    cache.cache_set(key, result)
    return result


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(name=payload.name, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    cache.cache_delete(CACHE_LIST_KEY)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    cache.cache_delete(CACHE_LIST_KEY)
    cache.cache_delete(CACHE_ITEM_KEY.format(id=item_id))


@router.get("/stats/summary")
def stats(db: Session = Depends(get_db)):
    total = db.query(Item).count()
    with_desc = db.query(Item).filter(Item.description != "").count()
    return {
        "total_items": total,
        "items_with_description": with_desc,
        "items_without_description": total - with_desc,
    }
