import time
from pathlib import Path

import aiosqlite
import json

from config import settings
from logger import db_logger as logger

DATABASE = settings.DB_PATH


async def init_db():

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                uid TEXT,
                wpm REAL,
                rawWpm REAL,
                charStats TEXT,
                acc REAL,
                mode TEXT,
                mode2 TEXT,
                timestamp INTEGER,
                testDuration REAL,
                afkDuration INTEGER,
                consistency REAL,
                keyConsistency REAL,
                chartData TEXT,
                language TEXT,
                isPb BOOLEAN,
                name TEXT,
                tags TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY,
                refresh_token TEXT,
                id_token TEXT,
                expires_at INTEGER
            )
        ''')

        await db.execute('''
                   CREATE TABLE IF NOT EXISTS auth_codes (
                       user_id INTEGER PRIMARY KEY,
                       auth_code TEXT NOT NULL,
                       expires_at INTEGER NOT NULL
                   )
               ''')
        await db.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                       user_id INTEGER PRIMARY KEY,
                       authorized BOOLEAN NOT NULL,
                       auth_date INTEGER NOT NULL
                   )
               ''')
        await db.commit()
        logger.info("Database initialized with tables 'results', 'tokens', 'auth_codes', and 'users'.")


async def result_exists(record_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT 1 FROM results WHERE id = ?', (record_id,)) as cursor:
            return await cursor.fetchone() is not None


async def insert_or_replace_result(item):
    async with aiosqlite.connect(DATABASE) as db:
        query = '''
            INSERT OR REPLACE INTO results (
                id, uid, wpm, rawWpm, charStats, acc, mode, mode2, timestamp,
                testDuration, afkDuration, consistency, keyConsistency, chartData,
                language, isPb, name, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        await db.execute(query, (
            item.get('_id', ''),
            item.get('uid', ''),
            item.get('wpm', 0.0),
            item.get('rawWpm', 0.0),
            json.dumps(item.get('charStats', [])),
            item.get('acc', 0.0),
            item.get('mode', ''),
            item.get('mode2', ''),
            item.get('timestamp', 0),
            item.get('testDuration', 0.0),
            item.get('afkDuration', 0),
            item.get('consistency', 0.0),
            item.get('keyConsistency', 0.0),
            json.dumps(item.get('chartData', '')),
            item.get('language', ''),
            item.get('isPb', False),
            item.get('name', ''),
            json.dumps(item.get('tags', []))
        ))
        await db.commit()


async def store_tokens(refresh_token, id_token, expires_in):
    try:
        expires_at = int(time.time()) + int(expires_in)
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute('''
                INSERT OR REPLACE INTO tokens (refresh_token, id_token, expires_at)
                VALUES (?, ?, ?)
            ''', (refresh_token, id_token, expires_at))
            await db.commit()
            logger.info("Tokens stored in the database.")
    except aiosqlite.Error as e:
        logger.error(f"Database error occurred while storing tokens: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while storing tokens: {e}")


async def load_tokens():
    try:
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute(
                    'SELECT refresh_token, id_token, expires_at FROM tokens ORDER BY id DESC LIMIT 1') as cursor:
                row = await cursor.fetchone()
                if row:
                    logger.info(f"Loaded tokens: {str(row)[:40]}...")
                    return row
                return None
    except aiosqlite.Error as e:
        logger.error(f"Database error occurred while loading tokens: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading tokens: {e}")
        return None


async def get_all_results():
    try:
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute('SELECT * FROM results') as cursor:
                rows = await cursor.fetchall()
                logger.info(f"Fetched {len(rows)} results from the database.")
                return rows
    except aiosqlite.Error as e:
        logger.error(f"Database error occurred: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return []


async def store_auth_code(user_id, auth_code):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT OR REPLACE INTO auth_codes (user_id, auth_code, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, auth_code, int(time.time()) + 300))  # Код действует 5 минут
        await db.commit()


async def check_auth_code(user_id, auth_code):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT auth_code, expires_at FROM auth_codes WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                stored_code, expires_at = row
                if stored_code == auth_code and int(time.time()) < expires_at:
                    return True
    return False


async def store_authorization(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, authorized, auth_date)
            VALUES (?, ?, ?)
        ''', (user_id, True, int(time.time())))
        await db.commit()


async def is_authorized(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT authorized FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return False


async def get_authorized_users():
    async with aiosqlite.connect(DATABASE) as db:
        query = 'SELECT user_id FROM users'
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()

    return [row[0] for row in rows]


async def get_predlast_result(record):
    async with aiosqlite.connect(DATABASE) as db:
        query = '''
            SELECT uid, wpm, acc, testDuration FROM results 
            WHERE uid = ? AND (tags LIKE ? OR tags IS NULL)
            ORDER BY timestamp DESC
            LIMIT 2
        '''
        tag_param = f'%{json.dumps([settings.TAG_RESULT])}%'
        async with db.execute(query, (record['uid'], tag_param)) as cursor:
            rows = await cursor.fetchall()

    columns = ['uid', 'wpm', 'acc', 'testDuration']
    results = []
    for row in rows:
        row_dict = dict(zip(columns, row))

        for col in ['wpm', 'acc', 'testDuration']:
            try:
                row_dict[col] = float(row_dict[col])
            except (TypeError, ValueError):
                row_dict[col] = 0.0
        results.append(row_dict)

    return results


async def get_overall_results():
    async with aiosqlite.connect(DATABASE) as db:
        query = '''
                    SELECT 
                        AVG(wpm) as avg_wpm,
                        AVG(acc) as avg_acc,
                        SUM(testDuration) as avg_duration,
                        COUNT(*) as test_count
                    FROM results
                    WHERE tags LIKE ? OR tags IS NULL
                '''
        tag_param = f'%{json.dumps([settings.TAG_RESULT])}%'
        async with db.execute(query, (tag_param,)) as cursor:
            row = await cursor.fetchone()

    return row
