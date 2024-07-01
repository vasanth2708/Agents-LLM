import json
import sys
import os

from pydantic import BaseModel



# Add the commons directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../models')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../apps')))


import time
from typing import Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .utils.websocket_manager import WebSocketManager
from common.researcher.master.agent import GPTResearcher
from .experts.service import ExpertService
from fastapi.middleware.cors import CORSMiddleware

previous_queries = ["Task - "]
class ResearchRequest(BaseModel):
    task: str
    
    
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

manager = WebSocketManager()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/expert")
async def get_agent(query: str):
    previous_queries[0]+=query
    results = await ExpertService(query).find_expert()
    return results

@app.post("/chat")
async def get_chat(request: ResearchRequest):
    previous_queries[0]+=request
    results =  await GPTResearcher(request).conduct_research()
    print(results)
    return results