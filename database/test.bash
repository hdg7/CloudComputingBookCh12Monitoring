#!/bin/bash

pip install pytest sqlalchemy pytest-asyncio aioredis
pytest -v testDb.py testDbRedis.py
