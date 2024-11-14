import asyncio

import pytest

from asyncmy.connection import Connection


@pytest.mark.asyncio
async def test_pool(pool):
    assert pool.minsize == 1
    assert pool.maxsize == 10
    assert pool.size == 1
    assert pool.freesize == 1


@pytest.mark.asyncio
async def test_pool_cursor(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            ret = await cursor.fetchone()
            assert ret == (1,)


@pytest.mark.asyncio
async def test_acquire(pool):
    conn = await pool.acquire()
    assert isinstance(conn, Connection)
    assert pool.freesize == 0
    assert pool.size == 1
    assert conn.connected
    await pool.release(conn)
    assert pool.freesize == 1
    assert pool.size == 1


@pytest.mark.asyncio
async def test_cancel_execute(pool, event_loop):
    async def run(index):
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f"SELECT {index}")
                ret = await cursor.fetchone()
                assert ret == (index,)

    task = event_loop.create_task(run(1))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await run(2)
