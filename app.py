import sys
import os
import requests

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL")
print(mongo_db_url)

import pymongo
from Network_Security.exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging
from Network_Security.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response, HTMLResponse
# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

from Network_Security.utils.main_utils.utils import load_object
from Network_Security.utils.ml_utils.model.estimator import NetworkModel


def download_file(url, filename):
    os.makedirs("final_model", exist_ok=True)
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ {filename} downloaded successfully!")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    else:
        print(f"✅ {filename} already exists")


PREPROCESSOR_URL = "https://drive.google.com/uc?export=download&id=1hk46WG0BTicQvpe1oYfgDjoVvTFP7LQk"
MODEL_URL = "https://drive.google.com/uc?export=download&id=17qBw0wk7tNx0sx4SpAyRrpd0hv44pEAD"

download_file(PREPROCESSOR_URL, "final_model/preprocessor.pkl")
download_file(MODEL_URL, "final_model/model.pkl")


os.makedirs("prediction_output", exist_ok=True)

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from Network_Security.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from Network_Security.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

templates = Jinja2Templates(directory="templates")
templates.env = Environment(
    loader=FileSystemLoader("templates"),
    auto_reload=True,
    cache_size=0
)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e, sys)

@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred
        df['predicted_column'] = df['predicted_column'].replace(-1, 0)
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)