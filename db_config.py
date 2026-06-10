import asyncpg
from config import PG_URL

async def create_db_pool():
    return await asyncpg.create_pool(PG_URL)

async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(100),
                bunker_id VARCHAR(50) UNIQUE,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')