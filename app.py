import sys
import os

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
import pandas as pd

from Network_Security.utils.main_utils.utils import load_object
from Network_Security.utils.ml_utils.model.estimator import NetworkModel

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

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Security System</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #0f172a; color: white; }
        .container { max-width: 800px; margin: auto; background: #1e293b; padding: 40px; border-radius: 16px; }
        input, button { width: 100%; padding: 10px; margin: 10px 0; border-radius: 8px; }
        button { background: #3b82f6; color: white; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #334155; padding: 8px; text-align: left; }
        th { background: #3b82f6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Intrusion Detection System</h1>
        <p>Upload CSV file for prediction</p>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" id="fileInput" name="file" accept=".csv" required>
            <button type="submit">Predict</button>
        </form>
        <div id="result"></div>
    </div>
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const file = document.getElementById('fileInput').files[0];
            const formData = new FormData();
            formData.append('file', file);
            document.getElementById('result').innerHTML = '<p>Processing...</p>';
            const response = await fetch('/predict', { method: 'POST', body: formData });
            const html = await response.text();
            document.getElementById('result').innerHTML = html;
        });
    </script>
</body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(content=HTML_PAGE)

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
        return HTMLResponse(content=table_html)
    except Exception as e:
        raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)