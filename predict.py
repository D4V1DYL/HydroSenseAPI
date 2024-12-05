from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
from joblib import load

model = load("models/svm_model.pkl")
router = APIRouter()

class WaterData(BaseModel):
    pH: float
    Iron: float
    Nitrate: float
    Chloride: float
    Lead: float
    Turbidity: float
    Fluoride: float
    Copper: float
    Odor: float
    Sulfate: float
    Chlorine: float
    Manganese: float
    Total_Dissolved_Solids: float

@router.post("/water/")
def predict_water_quality(data: WaterData):
    try:
        # Convert input data to numpy array
        input_data = pd.DataFrame([{
            "pH": data.pH,
            "Iron": data.Iron,
            "Nitrate": data.Nitrate,
            "Chloride": data.Chloride,
            "Lead": data.Lead,
            "Turbidity": data.Turbidity,
            "Fluoride": data.Fluoride,
            "Copper": data.Copper,
            "Odor": data.Odor,
            "Sulfate": data.Sulfate,
            "Chlorine": data.Chlorine,
            "Manganese": data.Manganese,
            "Total_Dissolved_Solids": data.Total_Dissolved_Solids
        }])

        # Make prediction
        prediction = model.predict(input_data)
        print(prediction)
        # Interpret the prediction
        result = "clean" if prediction[0] == 1 else "dirty"
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))