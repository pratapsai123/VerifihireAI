import asyncio
import websockets
import json
import uuid

async def test_ws_validation():
    # Use the expected URL pattern with a random UUID
    random_token = str(uuid.uuid4())
    url = f"ws://localhost:8000/ws/interview/{random_token}/candidate/"
    
    print(f"Testing WebSocket validation with invalid token: {random_token}")
    print(f"URL: {url}")
    
    try:
        async with websockets.connect(url) as websocket:
            # We expect the server to accept and then immediately send an error message + close
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received response: {data}")
            
            if data.get('type') == 'error' and 'Invalid session' in data.get('message', ''):
                print("✅ TEST PASSED: Server sent appropriate error message.")
            else:
                print("❌ TEST FAILED: Server sent unexpected message.")
                
            try:
                await websocket.recv()
                print("❌ TEST FAILED: Connection remained open after error.")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"✅ TEST PASSED: Connection closed with code {e.code}")
                if e.code == 4004:
                    print("✅ TEST PASSED: Connection closed with correct code 4004.")
                else:
                    print(f"⚠️ Note: Connection closed with code {e.code} instead of 4004.")
                    
    except ConnectionRefusedError:
        print("❌ ERROR: Could not connect to the server. Is it running?")
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws_validation())
