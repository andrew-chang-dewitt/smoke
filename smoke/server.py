import asyncio
from typing import NoReturn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

WS_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def index() -> HTMLResponse:
    return HTMLResponse(WS_HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

TEST_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Test data stream</title>
    </head>
    <body>
        <h1>Test data stream</h1>
        <ul id='data'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/data-stream");
            ws.onmessage = function(event) {
                var data = document.getElementById('data')
                var point = document.createElement('li')
                var content = document.createTextNode(event.data)
                point.appendChild(content)
                data.appendChild(point)
            };
        </script>
    </body>
</html>
"""


@app.get("/test")
async def test() -> HTMLResponse:
    return HTMLResponse(TEST_HTML)


@app.websocket("/data-stream")
async def socket_test(websocket: WebSocket) -> NoReturn:
    await websocket.accept()

    while True:
        await websocket.send_json({
            'message': 'this is a test',
            'number': 1,
            'bool': True
        })
        await asyncio.sleep(1)
