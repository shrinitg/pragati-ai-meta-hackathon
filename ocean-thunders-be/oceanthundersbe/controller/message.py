
from oceanthundersbe import app, connection_mapping
from fastapi import WebSocket

from oceanthundersbe.service.message import Message

message_service = Message()


@app.websocket("/message")
async def handle_message(websocket: WebSocket):
    try:
        print("WebSocket connection request received")
        await websocket.accept()
        await message_service.handle_message(websocket)
    except Exception as e:
        print(f"Some exception occurred with websocket request: {e}")
