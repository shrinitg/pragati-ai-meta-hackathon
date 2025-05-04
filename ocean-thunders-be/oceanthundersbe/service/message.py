import base64
import json
import os
import uuid

import requests
from fastapi import WebSocket

from oceanthundersbe import connection_mapping, user_data, constants
from oceanthundersbe.dto import InputMessage, UserData, InputMessageType
from oceanthundersbe.service.llm_service import LLMService

from e2enetworks.cloud import tir

from oceanthundersbe.service.utils import remove_emojis

tir.init(api_key=constants.E2E_API_KEY, access_token=constants.E2E_ACCESS_TOKEN, team=constants.E2E_TEAM,
         project=constants.E2E_PROJECT)
client = tir.ModelAPIClient()

llm_service = LLMService()


class Message:

    def __init__(self):
        print("Message class has been initialized")

    async def handle_message(self, websocket: WebSocket):
        connection_id = str(uuid.uuid4())
        if connection_id not in connection_mapping:
            connection_mapping[connection_id] = websocket
            user_data[connection_id] = UserData()

        try:
            while True:
                data = await websocket.receive_text()
                print(f"Received from {connection_id}: {data}")
                data = InputMessage(**json.loads(data))
                if data.type == InputMessageType.AUDIO:
                    data.content = await self.get_text_from_speech(data.content, connection_id)
                    transcript_response = {
                        "type": "transcription",
                        "content": data.content
                    }
                    await websocket.send_json(transcript_response)
                response = await llm_service.handle_and_generate_response(data, connection_id)

                if data.type == InputMessageType.AUDIO:
                    async for audio_packet in self.convert_text_to_speech(response, websocket):

                        response = {
                            "type": "audio",
                            "content": audio_packet,
                            "format": "wav"
                        }
                        await websocket.send_json(response)
                else:
                    response = {
                        "type": "assistant",
                        "content": response
                    }
                    await websocket.send_json(response)

        except Exception as e:
            print(f"Connection {connection_id} closed due to exception: {e}")
            await websocket.close()
            del connection_mapping[connection_id]
        finally:
            await websocket.close()

    async def get_text_from_speech(self, content, connection_id):
        file_path = f"{connection_id}.mp3"
        audio_bytes = base64.b64decode(content)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        data = {"input": f"./{file_path}",
                "language": "English",
                "task": "transcribe",
                "max_new_tokens": 400,
                "return_timestamps": "none"
                }
        output = client.infer(model_name="whisper-large-v3", data=data)
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Audio text received is: {output[1].outputs[0].data[0]}")
        return output[1].outputs[0].data[0]

    async def convert_text_to_speech(self, content, websocket):

        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": constants.SARVAM_API_KEY
        }

        without_emoji_content = remove_emojis(content)
        chunk_size = 500
        chunks = [without_emoji_content[i:i + chunk_size] for i in range(0, len(without_emoji_content), chunk_size)]

        print(f"number of chunks: {len(chunks)}")

        text_response_sent = False

        for i, chunk in enumerate(chunks):
            payload = {
                "inputs": [chunk],
                "target_language_code": "hi-IN",
                "speaker": "neel",
                "model": "bulbul:v1",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.0,
                "enable_preprocessing": True,
            }

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:

                if not text_response_sent:
                    text_response = {
                        "type": "assistant",
                        "content": content
                    }
                    await websocket.send_json(text_response)
                    text_response_sent = True

                audio_data = base64.b64decode(response.json()["audios"][0])
                b64_audio = base64.b64encode(audio_data).decode("utf-8")

                with open("output.wav", "wb") as f:
                    f.write(
                        base64.b64decode(b64_audio))
                yield b64_audio
            else:
                print(f"Error for chunk {i}: {response.status_code}")
                print(response.json())
