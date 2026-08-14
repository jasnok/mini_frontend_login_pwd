from fastapi import APIRouter, HTTPException

from app.schemas.cart_schema import CartCreate, CartPublic, CartUpdate
from app.services.cart_service import (
    cart_create,
    cart_delete,
    cart_get,
    cart_get_all,
    cart_get_by_user,
    cart_update,
)

cart_router = APIRouter(tags=["Cart"])


@cart_router.post("/carts", response_model=CartPublic)
def create_cart(cart: CartCreate):
    return cart_create(cart)


@cart_router.get("/carts", response_model=list[CartPublic])
def get_all_carts():
    return cart_get_all()


@cart_router.get("/carts/{cart_id}", response_model=CartPublic)
def get_cart(cart_id: str):
    result = cart_get(cart_id)
    if result is None:
        raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")
    return result


@cart_router.get("/carts/user/{user_id}", response_model=list[CartPublic])
def get_carts_by_user(user_id: str):
    return cart_get_by_user(user_id)


@cart_router.put("/carts/{cart_id}", response_model=CartPublic)
def update_cart(cart_id: str, cart: CartUpdate):
    return cart_update(cart_id, cart)


@cart_router.delete("/carts/{cart_id}", response_model=CartPublic)
def delete_cart(cart_id: str):
    return cart_delete(cart_id)
