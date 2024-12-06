from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from models.models import Product, Company
import cloudinary
import cloudinary.uploader
import uuid

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Cloudinary
cloudinary.config(
    cloud_name='dqnwgswnw',
    api_key='194188234624597',
    api_secret='ZsNvOsVwHO6W_gYcij37sYQnExs'
)

def upload_image_to_cloudinary(file: UploadFile):
    try:
        result = cloudinary.uploader.upload(file.file, public_id=f"images/{uuid.uuid4()}")
        return result['secure_url']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


@router.post("/save/")
def create_product(
    ProductID: str = Form(...),
    Name: str = Form(...),
    Description: str = Form(...),
    CompanyID: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if the company exists
        company = db.query(Company).filter(Company.CompanyID == CompanyID).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if the product already exists
        existing_product = db.query(Product).filter(Product.ProductID == ProductID).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product already exists")

        # Upload image to Cloudinary
        image_url = upload_image_to_cloudinary(image)

        # Create a new product
        new_product = Product(
            ProductID=ProductID,
            Name=Name,
            Description=Description,
            Image=image_url,
            CompanyID=CompanyID
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {"message": "Product created successfully", "product": new_product}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
