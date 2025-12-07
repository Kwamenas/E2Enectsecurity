import os 
import sys
from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.pipeline import train_pipeline
from src.utils.main_utils.calls_utils import load_object
from fastapi import FastAPI,File,UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

app=FastAPI()

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home_route():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipe=train_pipeline()
        train_pipe.run_pipeline()
        return Response("Training Successful")
    except Exception as e:
        raise CustomException(e)