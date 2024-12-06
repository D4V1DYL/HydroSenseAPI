from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import pandas as pd
from joblib import load
from sqlalchemy.orm import Session
from database import SessionLocal
from models.models import WaterQualityPrediction, WaterQuality, WaterData, WaterDataDetail, WaterProperty

model = load("models/svm_model.pkl")

router = APIRouter()

class WaterDataInput(BaseModel):
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
    ProductID: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/water/")
def predict_water_quality(data: WaterDataInput, db: Session = Depends(get_db)):
    try:
        # Convert input data to DataFrame
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
            "Total Dissolved Solids": data.Total_Dissolved_Solids
        }])

        # Ensure feature names match the model
        input_data.columns = input_data.columns.str.replace('_', ' ')
        input_data = input_data[model.feature_names_in_]

        # Make prediction
        prediction = model.predict(input_data)
        prediction_result = int(prediction[0])

        # Interpret the prediction
        result = "clean" if prediction_result == 1 else "dirty"

        # Get water quality ID
        water_quality = db.query(WaterQuality).filter(WaterQuality.Name == result.capitalize()).first()
        if not water_quality:
            raise HTTPException(status_code=404, detail="Water quality not found")

        # Save the prediction to the database
        water_data = WaterData(
            ProductID=data.ProductID,
            Date=pd.Timestamp.now(tz="UTC"),
            Description="Ini Test Water B"
        )
        db.add(water_data)
        db.commit()
        db.refresh(water_data)

        # Save prediction
        new_prediction = WaterQualityPrediction(
            WaterDataID=water_data.WaterDataID,
            WaterQualityID=water_quality.WaterQualityID
        )
        db.add(new_prediction)

        # Bulk-fetch water property IDs
        water_properties = db.query(WaterProperty).all()
        property_dict = {prop.Name: prop.WaterPropertyID for prop in water_properties}

        # Save water data details
        for prop, value in data.dict().items():
            if prop in property_dict:
                water_data_detail = WaterDataDetail(
                    WaterDataID=water_data.WaterDataID,
                    WaterPropertyID=property_dict[prop],
                    Value=value
                )
                db.add(water_data_detail)

        db.commit()

        return {"Message":"Sucessfully Predict", "prediction": result}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required feature: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))