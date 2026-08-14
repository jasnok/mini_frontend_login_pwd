"""
PostgreSQL 클라이언트 (pgvector 연동)
Supabase REST API 대체 - 직접 PostgreSQL 연결
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from pathlib import Path

# .env 파일 경로
ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"


def get_required_env(key: str) -> str:
    """필수 환경 변수 가져오기"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"환경 변수 {key}가 설정되지 않았습니다")
    return value


class PostgresConnection:
    """PostgreSQL 연결 관리자"""
    
    def __init__(self):
        self.conn = None
    
    def connect(self):
        """PostgreSQL 연결 생성"""
        load_dotenv(ENV_PATH)
        
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5433")),
                user=os.getenv("DB_USER", "agent_user"),
                password=get_required_env("DB_PASSWORD"),
                database=os.getenv("DB_NAME", "agent_db")
            )
            return self.conn
        except psycopg2.Error as e:
            raise ValueError(f"PostgreSQL 연결 실패: {str(e)}")
    
    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()


def get_postgres_connection():
    """
    새 PostgreSQL 연결 반환 (팩토리 함수)
    
    사용 예:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("SELECT * FROM customers WHERE id = %s", (user_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    """
    pg = PostgresConnection()
    return pg.connect()
