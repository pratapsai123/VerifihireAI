import websocket
import json
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("ASSEMBLYAI_API_KEY")

if not API_KEY:
    print("No API Key found")
    exit(1)

CONNECTION_PARAMS = {
    "sample_rate": 16000,
    "speech_model": "u3-rt-pro"
}
API_ENDPOINT_BASE_URL = "wss://streaming.assemblyai.com/v3/ws"
API_ENDPOINT = f"{API_ENDPOINT_BASE_URL}?{urlencode(CONNECTION_PARAMS)}"

def on_open(ws):
    print("\n[WebSocket] Connection opened successfully!")

def on_message(ws, message):
    data = json.loads(message)
    print(f"[WebSocket] Message received: {data.get('message_type')}")
    if data.get('message_type') == "SessionBegins":
        print(f"✅ It works! Session ID: {data.get('session_id')}")
        ws.close()

def on_error(ws, error):
    print(f"\n[WebSocket] Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"\n[WebSocket] Disconnected: Status={close_status_code}, Msg={close_msg}")

def run():
    print(f"Testing direct WebSocket connection to {API_ENDPOINT} ...")
    ws_app = websocket.WebSocketApp(
        API_ENDPOINT,
        header=[f"Authorization: {API_KEY}"], # header takes a list in websocket-client
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws_app.run_forever()

if __name__ == "__main__":
    run()
