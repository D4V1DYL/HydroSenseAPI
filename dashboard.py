from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import SessionLocal
from models.models import Company, Product, WaterQuality, WaterQualityPrediction, WaterData
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class CompanyLeaderboard(BaseModel):
    company_id: str
    company_name: str
    clean_count: int

class ProductList(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    result: str

class ProductHistory(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    product_image: str
    result: str
    date: str
    time: str

# Leaderboard Endpoint
@router.get("/leaderboard", response_model=List[CompanyLeaderboard])
def get_leaderboard(db: Session = Depends(get_db)):
    clean_quality_id = db.query(WaterQuality.WaterQualityID).filter(WaterQuality.Name == "Clean").scalar_subquery()
    
    leaderboard = (
        db.query(
            Company.CompanyID.label("company_id"),
            Company.Name.label("company_name"),
            func.count(WaterQualityPrediction.WaterQualityPredictionID).label("clean_count")
        )
        .join(Product, Product.CompanyID == Company.CompanyID)
        .join(WaterData, WaterData.ProductID == Product.ProductID)
        .join(WaterQualityPrediction, WaterQualityPrediction.WaterDataID == WaterData.WaterDataID)
        .filter(WaterQualityPrediction.WaterQualityID == clean_quality_id)
        .group_by(Company.CompanyID, Company.Name)
        .order_by(func.count(WaterQualityPrediction.WaterQualityPredictionID).desc())
        .all()
    )
    
    return leaderboard


# Products by Company Endpoint with Latest Result
@router.get("/company/{company_id}/products", response_model=List[ProductList])
def get_company_products(company_id: str, db: Session = Depends(get_db)):
    subquery = (
        db.query(
            WaterData.ProductID,
            func.max(WaterData.Date).label("latest_date")
        )
        .join(Product, Product.ProductID == WaterData.ProductID)
        .filter(Product.CompanyID == company_id)
        .group_by(WaterData.ProductID)
        .subquery()
    )
    
    products = (
        db.query(
            Product.ProductID.label("product_id"),
            Product.Name.label("product_name"),
            Product.Description.label("product_description"),
            WaterQuality.Name.label("result")
        )
        .join(WaterData, WaterData.ProductID == Product.ProductID)
        .join(WaterQualityPrediction, WaterQualityPrediction.WaterDataID == WaterData.WaterDataID)
        .join(WaterQuality, WaterQuality.WaterQualityID == WaterQualityPrediction.WaterQualityID)
        .join(subquery, (subquery.c.ProductID == WaterData.ProductID) & (subquery.c.latest_date == WaterData.Date))
        .filter(Product.CompanyID == company_id)
        .distinct(Product.ProductID, WaterData.Date)
        .order_by(Product.ProductID, desc(WaterData.Date))
        .all()
    )
    
    # Filter out duplicates and keep only the latest result for each product
    unique_products = {}
    for product in products:
        if product.product_id not in unique_products:
            unique_products[product.product_id] = product
    
    if not unique_products:
        raise HTTPException(status_code=404, detail="Company not found or no products available")
    
    return list(unique_products.values())


# Product History by Company Endpoint
@router.get("/company/{company_id}/history", response_model=List[ProductHistory])
def get_product_history(company_id: str, db: Session = Depends(get_db)):
    history = (
        db.query(
            Product.ProductID.label("product_id"),
            Product.Name.label("product_name"),
            Product.Description.label("product_description"),
            Product.Image.label("product_image"),
            WaterQuality.Name.label("result"),
            WaterData.Date.label("date")
        )
        .select_from(Company)
        .join(Product, Product.CompanyID == Company.CompanyID)
        .join(WaterData, WaterData.ProductID == Product.ProductID)
        .join(WaterQualityPrediction, WaterQualityPrediction.WaterDataID == WaterData.WaterDataID)
        .join(WaterQuality, WaterQuality.WaterQualityID == WaterQualityPrediction.WaterQualityID)
        .filter(Company.CompanyID == company_id)
        .order_by(WaterData.Date.desc())
        .all()
    )
    
    if not history:
        raise HTTPException(status_code=404, detail="Company not found or no history available")
    
    formatted_history = []
    for record in history:
        date_time = record.date
        date_str = date_time.strftime("%Y-%m-%d")
        time_str = date_time.strftime("%I:%M %p")
        formatted_history.append(ProductHistory(
            product_id = record.product_id,
            product_name=record.product_name,
            product_description=record.product_description,
            product_image=record.product_image,
            result=record.result,
            date=date_str,
            time=time_str
        ))
    
    return formatted_history