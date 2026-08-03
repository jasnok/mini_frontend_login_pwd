from app.core.supabase_client import get_supabase
from fastapi import HTTPException
from app.schemas.auth_scheme import (
    AuthCreate, AuthLogin, AuthPublic
)
from app.core.password import hash_password, verify_password


def sign_up_process(auth: AuthCreate):
    """ 회원 가입 """
    supabase = get_supabase()
    db_customer = _customer_get(auth.id)
    if db_customer is not None:
        raise HTTPException(
            status_code=409,
            detail="이미 사용 중인 아이디입니다."
        )
    result = (
        supabase.table("customers")
         .insert(
            {
                "id": auth.id,
                "pwd": hash_password(auth.pwd),
                "name": auth.name,
            }
        )
        .execute()
    )
    if not result.data:
        raise HTTPException(
                status_code = 500,
                detail = "DB 장애"
            )
    return AuthPublic.model_validate(result.data[0])


def sign_in_process(auth: AuthLogin):
    """ 회원 로그인 """
    db_customer = _customer_get(auth.id)
    if db_customer is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다."
        )
    if():
        payload = {"id": db_customer["id"], "name":db_customer["name"]}
        return AuthPublic.model_validate(payload)
    else:
        raise HTTPException(
            status_code = 401,
            detail = "아이디 또는 패스워드가 올바르지 않습니다."
        )

def sign_out_process(input_id:str):
    """ 회원 로그 아웃 """

    return AuthPublic(
        id = input_id,
    )

def my_page_process(input_id:str):
    """ 회원 마이페이지 """

    db_customer = _customer_get(input_id)
    if db_customer is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다."
        )
    return AuthPublic.model_validate(db_customer)

def _customer_get(customer_id: str) -> dict | None:
    supabase = get_supabase()

    result = (
        supabase.table("customers")
        .select("*")
        .eq("id", customer_id)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]