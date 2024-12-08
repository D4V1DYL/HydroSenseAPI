from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import SessionLocal
from models.models import User, UserCompanyMapping, Company
from typing import Optional, List
import cloudinary
import cloudinary.uploader
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth import get_current_super_admin_user, get_db

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

# Pydantic Models
class AssignRole(BaseModel):
    user_id: int
    role: int

class AssignCompany(BaseModel):
    user_id: int
    company_id: int

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    email: EmailStr
    phone_number: str
    website: Optional[str] = None
    image: Optional[UploadFile] = None

class UserWithRole(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    role_id: Optional[int]
    role_name: Optional[str]

class UserCompanyMappingResponse(BaseModel):
    user_id: int
    user_name: str
    company_id: int
    company_name: str

class CompanyResponse(BaseModel):
    company_id: int
    name: str

# Assign Role to User Endpoint
@router.post("/assign-role", status_code=status.HTTP_200_OK)
@limiter.limit("50/minute")
def assign_role(request: Request, assign_role: AssignRole, db: Session = Depends(get_db), current_user: User = Depends(get_current_super_admin_user)):
    user = db.query(User).filter(User.UserID == assign_role.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.Role = assign_role.role
    db.commit()
    return {"message": "Role assigned successfully"}

# Assign Company to User Endpoint
@router.post("/assign-company", status_code=status.HTTP_200_OK)
@limiter.limit("50/minute")
def assign_company(request: Request, assign_company: AssignCompany, db: Session = Depends(get_db), current_user: User = Depends(get_current_super_admin_user)):
    user = db.query(User).filter(User.UserID == assign_company.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    company = db.query(Company).filter(Company.CompanyID == assign_company.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    user_company_mapping = db.query(UserCompanyMapping).filter(UserCompanyMapping.UserID == assign_company.user_id).first()
    if user_company_mapping:
        user_company_mapping.CompanyID = assign_company.company_id
    else:
        new_mapping = UserCompanyMapping(UserID=assign_company.user_id, CompanyID=assign_company.company_id)
        db.add(new_mapping)
    db.commit()
    return {"message": "Company assigned successfully"}

# Create Company Endpoint
@router.post("/create-company", status_code=status.HTTP_201_CREATED)
@limiter.limit("50/minute")
def create_company(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    address: str = Form(...),
    email: EmailStr = Form(...),
    phone_number: str = Form(...),
    website: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin_user)
):
    try:
        image_url = None
        if image:
            result = cloudinary.uploader.upload(image.file, public_id=f"company_images/{uuid.uuid4()}")
            image_url = result['secure_url']

        new_company = Company(
            Name=name,
            Description=description,
            Address=address,
            Email=email,
            PhoneNumber=phone_number,
            Website=website,
            Image=image_url
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        return {"message": "Company created successfully", "company": new_company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get All Users with Roles Assigned
@router.get("/users-with-roles", response_model=List[UserWithRole])
@limiter.limit("50/minute")
def get_users_with_roles(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_super_admin_user)):
    users = db.query(User).all()
    return [
        UserWithRole(
            user_id=user.UserID,
            first_name=user.FirstName,
            last_name=user.LastName,
            role_id=user.Role,
            role_name=user.role.Name if user.role else None
        )
        for user in users
    ]

# Get All User-Company Mappings
@router.get("/user-company-mappings", response_model=List[UserCompanyMappingResponse])
@limiter.limit("50/minute")
def get_user_company_mappings(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_super_admin_user)):
    mappings = db.query(UserCompanyMapping).all()
    return [
        UserCompanyMappingResponse(
            user_id=mapping.UserID,
            user_name=f"{mapping.user.FirstName} {mapping.user.LastName}",
            company_id=mapping.CompanyID,
            company_name=mapping.company.Name
        )
        for mapping in mappings
    ]

# List All Companies
@router.get("/companies", response_model=List[CompanyResponse])
@limiter.limit("50/minute")
def list_companies(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_super_admin_user)):
    companies = db.query(Company).all()
    return [
        CompanyResponse(
            company_id=company.CompanyID,
            name=company.Name
        )
        for company in companies
    ]