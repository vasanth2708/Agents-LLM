import asyncio
import json

from fastapi import WebSocket

class WebSocketManager:
    """Manage websockets"""

    def __init__(self):
        """Initialize the WebSocketManager class."""
        self.active_connections = []
        self.sender_tasks = {}
        self.message_queues = {}

    async def start_sender(self, websocket: WebSocket):
        """Start the sender task."""
        queue = self.message_queues.get(websocket)
        if not queue:
            return

        while True:
            message = await queue.get()
            if websocket in self.active_connections:
                try:
                    await websocket.send_text(message)
                except:
                    break
            else:
                break

    async def connect(self, websocket: WebSocket):
        """Connect a websocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.message_queues[websocket] = asyncio.Queue()
        self.sender_tasks[websocket] = asyncio.create_task(self.start_sender(websocket))

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.sender_tasks[websocket].cancel()
            await self.message_queues[websocket].put(None)
            del self.sender_tasks[websocket]
            del self.message_queues[websocket]

    # async def start_streaming(self, task, report_type, report_source, websocket):
    #     """Start streaming the output."""
    #     report = await run_agent(task, report_type, report_source, websocket)
    #     return report


# async def run_agent(task, report_type, report_source, websocket):
#     """Run the agent."""
#     #start_time = datetime.datetime.now()
#     config_path = ""

#     if report_type == ReportType.DetailedReport.value:
#         pass
#         # researcher = DetailedReport(query=task, report_type=report_type, report_source=report_source, source_urls=None, config_path=config_path, websocket=websocket)
#     else:
#         researcher = BasicReport(query=task, report_type=report_type, report_source=report_source, source_urls=None, config_path=config_path, websocket=websocket)

#     report = await researcher.run()
#     #end_time = datetime.datetime.now()
#     #await websocket.send_json({"type": "logs", "output": f"\nTotal run time: {end_time - start_time}\n"})
#     return report
