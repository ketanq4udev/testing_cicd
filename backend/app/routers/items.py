from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

_items: List[dict] = [
    {"id": 1, "name": "Item One", "description": "First sample item"},
    {"id": 2, "name": "Item Two", "description": "Second sample item"},
]
_next_id = 3


class ItemCreate(BaseModel):
    name: str
    description: str = ""


class Item(ItemCreate):
    id: int


@router.get("/", response_model=List[Item])
def list_items():
    return _items


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in _items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    global _next_id
    item = {"id": _next_id, **payload.model_dump()}
    _next_id += 1
    _items.append(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int):
    for i, item in enumerate(_items):
        if item["id"] == item_id:
            _items.pop(i)
            return
    raise HTTPException(status_code=404, detail="Item not found")


@router.get("/stats/summary")
def get_stats():
    total = len(_items)
    with_desc = sum(1 for item in _items if item["description"])
    return {
        "total_items": total,
        "items_with_description": with_desc,
        "items_without_description": total - with_desc,
    }
