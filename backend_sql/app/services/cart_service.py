from datetime import datetime

import psycopg2
from fastapi import HTTPException
from psycopg2.extras import RealDictCursor

from app.core.postgres_client import get_postgres_connection
from app.schemas.cart_schema import CartCreate, CartPublic, CartUpdate


def _make_cart_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def cart_create(cart: CartCreate) -> CartPublic:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cart_id = _make_cart_id()
        cursor.execute(
            """
            INSERT INTO carts (id, user_id, item_id, count, created_date)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING *
            """,
            (cart_id, cart.user_id, cart.item_id, cart.count),
        )
        result = cursor.fetchone()
        conn.commit()

        if not result:
            raise HTTPException(status_code=500, detail="장바구니 생성에 실패했습니다.")

        return CartPublic.model_validate(dict(result))

    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=409, detail="중복된 장바구니 항목입니다.")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def cart_get_all() -> list[CartPublic]:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM carts ORDER BY created_date DESC")
        rows = cursor.fetchall()
        return [CartPublic.model_validate(dict(row)) for row in rows]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def cart_get(cart_id: str) -> CartPublic | None:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM carts WHERE id = %s", (cart_id,))
        result = cursor.fetchone()
        if not result:
            return None
        return CartPublic.model_validate(dict(result))
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def cart_get_by_user(user_id: str) -> list[CartPublic]:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            "SELECT * FROM carts WHERE user_id = %s ORDER BY created_date DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        return [CartPublic.model_validate(dict(row)) for row in rows]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def cart_update(cart_id: str, cart: CartUpdate) -> CartPublic:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE carts
            SET count = %s
            WHERE id = %s
            RETURNING *
            """,
            (cart.count, cart_id),
        )
        result = cursor.fetchone()
        conn.commit()

        if not result:
            raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")

        return CartPublic.model_validate(dict(result))

    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def cart_delete(cart_id: str) -> CartPublic:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM carts WHERE id = %s", (cart_id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")

        cursor.execute("DELETE FROM carts WHERE id = %s", (cart_id,))
        conn.commit()
        return CartPublic.model_validate(dict(existing))

    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB 오류: {str(e)}")
    finally:
        cursor.close()
        conn.close()
