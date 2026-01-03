import os 
import sys
import io
import pandas as pd
from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.pipeline.train_pipeline import train_pipe
from src.pipeline.predict_pipeline import PredictionConfig,PredictionPipeline
from fastapi import FastAPI,File,UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import numpy

app=FastAPI()

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#from fastapi.templating import Jinja2Templates
#templates=Jinja2Templates(directory="templates")

@app.get("/")
async def home_route():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        trainer=train_pipe()
        trainer.run_pipeline()
        return Response("Training Successful")
    except Exception as e:
        raise CustomException(e)

@app.post("/predict")
async def predict_route(request:Request,file:UploadFile= File(...)):
    try:
        content=await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        predictor=PredictionPipeline()
        df=predictor.predict(df)


        output_dir="Predict_Output"
        os.makedirs(output_dir,exist_ok=True)
        output_file=f"{output_dir}/pred.csv"
        df.to_csv(output_file,index=False)
        logging.info(f"Predictions saved to {output_file}")

        #table_html=df.to_html(classes="table table-striped")
        #return templates.TemplateResponse("table.html",{"request":request,"table":table_html})
    #table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return output_file
    #templates.TemplateResponse("table.html", {"request": request, "table": table_html})


    except Exception as e:
        raise CustomException(e)



if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8080)