from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models.models import Product, Company, WaterQualityPrediction, WaterQuality, WaterData, WaterDataDetail, WaterProperty,User
import cloudinary
import cloudinary.uploader
import uuid
import pandas as pd
from joblib import load
from pydantic import BaseModel
from typing import List
import json
from sqlalchemy import delete
from auth import get_current_admin_user



router = APIRouter()

# Initialize Cloudinary
cloudinary.config(
    cloud_name='dqnwgswnw',
    api_key='194188234624597',
    api_secret='ZsNvOsVwHO6W_gYcij37sYQnExs'
)

# Load the water quality prediction model
model = load("models/svm_model.pkl")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for water data input
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

class WaterDataInputEdit(BaseModel):
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
    ProductID: int

# Function to upload image to Cloudinary
def upload_image_to_cloudinary(file: UploadFile):
    try:
        result = cloudinary.uploader.upload(file.file, public_id=f"images/{uuid.uuid4()}")
        return result['secure_url']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

# Endpoint to create product and predict water quality in one request
@router.post("/save/")
def create_product_and_predict(
    Name: str = Form(...),
    Description: str = Form(...),
    CompanyID: str = Form(...),
    image: UploadFile = File(...),
    water_data: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    try:
        # Parse water_data JSON string to dictionary
        water_data_dict = json.loads(water_data)
        water_data_input = WaterDataInput(**water_data_dict)

        # Step 1: Create Product
        # Check if the company exists
        company = db.query(Company).filter(Company.CompanyID == CompanyID).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Generate a unique ProductID

        # Upload image to Cloudinary
        image_url = upload_image_to_cloudinary(image)

        # Create a new product
        new_product = Product(
            Name=Name,
            Description=Description,
            Image=image_url,
            CompanyID=CompanyID
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        # Step 2: Predict Water Quality
        # Convert input data to DataFrame
        input_data = pd.DataFrame([{
            "pH": water_data_input.pH,
            "Iron": water_data_input.Iron,
            "Nitrate": water_data_input.Nitrate,
            "Chloride": water_data_input.Chloride,
            "Lead": water_data_input.Lead,
            "Turbidity": water_data_input.Turbidity,
            "Fluoride": water_data_input.Fluoride,
            "Copper": water_data_input.Copper,
            "Odor": water_data_input.Odor,
            "Sulfate": water_data_input.Sulfate,
            "Chlorine": water_data_input.Chlorine,
            "Manganese": water_data_input.Manganese,
            "Total Dissolved Solids": water_data_input.Total_Dissolved_Solids
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
        water_data_entry = WaterData(
            ProductID=new_product.ProductID,
            Date=pd.Timestamp.now(tz="UTC"),
            Description="Water Quality Prediction"
        )
        db.add(water_data_entry)
        db.commit()
        db.refresh(water_data_entry)

        # Save prediction
        new_prediction = WaterQualityPrediction(
            WaterDataID=water_data_entry.WaterDataID,
            WaterQualityID=water_quality.WaterQualityID
        )
        db.add(new_prediction)

        # Bulk-fetch water property IDs
        water_properties = db.query(WaterProperty).all()
        property_dict = {prop.Name: prop.WaterPropertyID for prop in water_properties}

        # Save water data details
        for prop, value in water_data_input.dict().items():
            if prop in property_dict:
                water_data_detail = WaterDataDetail(
                    WaterDataID=water_data_entry.WaterDataID,
                    WaterPropertyID=property_dict[prop],
                    Value=value
                )
                db.add(water_data_detail)

        db.commit()

        return {"message": "Product created and water quality predicted successfully", "product": new_product, "prediction": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to predict water quality
@router.post("/predict/")
def predict_water_quality(data: WaterDataInputEdit, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
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
    

@router.delete("/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    try:
        # Step 1: Delete records from dependent tables
        # Delete WaterQualityPrediction records
        db.execute(delete(WaterQualityPrediction).where(WaterQualityPrediction.WaterDataID.in_(
            db.query(WaterData.WaterDataID).filter(WaterData.ProductID == product_id)
        )))

        # Delete WaterDataDetail records
        db.execute(delete(WaterDataDetail).where(WaterDataDetail.WaterDataID.in_(
            db.query(WaterData.WaterDataID).filter(WaterData.ProductID == product_id)
        )))

        # Delete WaterData records
        db.execute(delete(WaterData).where(WaterData.ProductID == product_id))

        # Step 2: Delete the product record
        db.execute(delete(Product).where(Product.ProductID == product_id))

        # Commit the transaction
        db.commit()

        return {"message": "Product and related records deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))