from typing import Dict

from fastapi import FastAPI, WebSocket

from middlewares import RequestContextLogMiddleware
from oceanthundersbe.dto import UserData

app = FastAPI(name="ocean-thunders")
app.add_middleware(RequestContextLogMiddleware)

connection_mapping: Dict[str, WebSocket] = {}
user_data: Dict[str, UserData] = {}

from oceanthundersbe.controller import message
