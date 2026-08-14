# product_service.py
from app.schemas.product_schema import (
    ProductCreate, 
    ProductPublic, 
    ProductUpdate,
)
from app.core.postgres_client import get_postgres_connection
from psycopg2.extras import RealDictCursor
import psycopg2
from zoneinfo import ZoneInfo
from datetime import datetime


# 1. 상품 생성
def product_create(product: ProductCreate) -> ProductPublic | None:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        
        cursor.execute(
            "INSERT INTO products (id, name, price, created_at) VALUES (%s, %s, %s, %s) RETURNING *",
            (
                now.strftime("%Y%m%d%H%M%S%f"),
                product.name,
                product.price,
                now.isoformat()
            )
        )
        result = cursor.fetchone()
        conn.commit()
        
        if not result:
            return None
        return ProductPublic.model_validate(dict(result))
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"DB Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# 2. 전체 상품 조회
def product_get_all() -> list[ProductPublic]:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        results = cursor.fetchall()
        return [ProductPublic.model_validate(dict(row)) for row in results]
    except psycopg2.Error as e:
        print(f"DB Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# 3. 한 개 상품 조회
def product_get(product_id: str) -> ProductPublic | None:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        if not result:
            return None
        return ProductPublic.model_validate(dict(result))
    except psycopg2.Error as e:
        print(f"DB Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# 4. 상품 삭제
def product_delete(product_id: str) -> ProductPublic | None:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 삭제 전에 상품 정보 조회
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            return ProductPublic.model_validate(dict(result))
        return None
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"DB Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# 5. 상품 수정
def product_update(
    product_id: str,
    product: ProductUpdate,
) -> ProductPublic | None:
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "UPDATE products SET name = %s, price = %s WHERE id = %s RETURNING *",
            (product.name, product.price, product_id)
        )
        result = cursor.fetchone()
        conn.commit()
        
        if not result:
            return None
        return ProductPublic.model_validate(dict(result))
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"DB Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
