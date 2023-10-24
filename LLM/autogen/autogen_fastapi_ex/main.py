# to test this code
# add your openai key to the config_list on autogen_chat.py
# run the following code in the same directory
# uvicorn main:app
# access http://localhost:8000
# send the following message:
# send ->  What is the status of my order?
# send ->  order 111
# send ->  customer 222
# the response should be Delivered
# send -> exit to end
# CTRL+C terminate the process


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import uuid
import threading
import asyncio

# custom import
from autogen_chat import AutogenChat


app = FastAPI()
app.autogen_chat = {}


@app.get("/")
async def get(request: Request):
    chat_id = str(uuid.uuid1())
    html = f"""<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            function showMessage(msg) {{
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(msg)
                message.appendChild(content)
                messages.appendChild(message)
            }};
            var chat_id = "{chat_id}"
            document.querySelector("#ws-id").textContent = chat_id;
            var ws = new WebSocket("ws://localhost:8000/ws/{chat_id}");
            ws.onmessage = function(event) {{
                showMessage(event.data)
            }};
            function sendMessage(event) {{
                var input = document.getElementById("messageText")
                ws.send(input.value)
                showMessage(input.value)
                input.value = ''
                event.preventDefault()
            }}
        </script>
    </body>
</html>
"""
    return HTMLResponse(html)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[AutogenChat] = []

    async def connect(self, autogen_chat: AutogenChat):
        await autogen_chat.websocket.accept()
        self.active_connections.append(autogen_chat)

    def disconnect(self, autogen_chat: AutogenChat):
        self.active_connections.remove(autogen_chat)

    async def send_local_message(self, message: str, autogen_chat: AutogenChat):
        await autogen_chat.websocket.send_text(message)


manager = ConnectionManager()


def do_work(autogen_chat):
    autogen_chat.start()

@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    try:
        autogen_chat = AutogenChat(chat_id=chat_id, websocket=websocket)
        await manager.connect(autogen_chat)
        t = threading.Thread(target=do_work, args=(autogen_chat,)) 
        autogen_chat.set_thread(t)
        t.start()
        while True:
            # wait for client message
            data = await autogen_chat.websocket.receive_text()
            # send data to thread 
            autogen_chat.client_sent_queue.put(data)
            # wait for response
            reply = autogen_chat.client_receive_queue.get(block=True)
            if reply != "exit":
                # send to the client on websocket
                await autogen_chat.websocket.send_text(reply)
            else:
                autogen_chat.thread.join()
                print("####FINISHED")
                raise WebSocketDisconnect

    except WebSocketDisconnect:
        manager.disconnect(autogen_chat)
    except Exception as e:
        #TODO end Thread in a nice way
        print("ERROR", str(e))
