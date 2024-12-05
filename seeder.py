from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import Base
from models.models import Role, User, Company, Product, WaterProperty, WaterData, WaterDataDetail, WaterQuality, WaterQualityPrediction, UserCompanyMapping

# Database URL
DATABASE_URL = "mysql+mysqlconnector://david:admin123@localhost:3306/hydrosense"  # Use PostgreSQL if needed

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a new session
session = Session(bind=engine)

# Create all tables
Base.metadata.create_all(engine)

# Seed data
def seed_data():
    # Seed roles
    roles = [
        Role(Name="Admin", Description="Administrator role"),
        Role(Name="User", Description="Regular user role")
    ]
    for role in roles:
        existing_role = session.query(Role).filter_by(Name=role.Name).first()
        if not existing_role:
            session.add(role)
    session.commit()

    # Seed companies
    companies = [
        Company(CompanyID="1", Name="Company A", Description="Description A", Address="Address A", Email="emailA@example.com", PhoneNumber="1234567890", Website="www.companya.com"),
        Company(CompanyID="2", Name="Company B", Description="Description B", Address="Address B", Email="emailB@example.com", PhoneNumber="0987654321", Website="www.companyb.com")
    ]
    for company in companies:
        existing_company = session.query(Company).filter_by(Email=company.Email).first()
        if not existing_company:
            session.add(company)
    session.commit()

    # Seed users
    users = [
        User(UserID="1", FirstName="John", LastName="Doe", Email="john.doe@example.com", Password="password", Role=1),
        User(UserID="2", FirstName="Jane", LastName="Doe", Email="jane.doe@example.com", Password="password", Role=2)
    ]
    for user in users:
        existing_user = session.query(User).filter_by(Email=user.Email).first()
        if not existing_user:
            session.add(user)
    session.commit()

    # Seed user-company mappings
    user_company_mappings = [
        UserCompanyMapping(UserCompanyID=1, UserID="1", CompanyID="1"),
        UserCompanyMapping(UserCompanyID=2, UserID="2", CompanyID="2")
    ]
    for mapping in user_company_mappings:
        existing_mapping = session.query(UserCompanyMapping).filter_by(UserID=mapping.UserID, CompanyID=mapping.CompanyID).first()
        if not existing_mapping:
            session.add(mapping)
    session.commit()

    # Seed products
    products = [
        Product(ProductID="1", Name="Product A", Description="Description A", CompanyID="1"),
        Product(ProductID="2", Name="Product B", Description="Description B", CompanyID="2")
    ]
    for product in products:
        existing_product = session.query(Product).filter_by(Name=product.Name, CompanyID=product.CompanyID).first()
        if not existing_product:
            session.add(product)
    session.commit()

    # Seed water properties
    water_properties = [
        WaterProperty(Name="pH", Description="pH level"),
        WaterProperty(Name="Iron", Description="Iron content"),
        WaterProperty(Name="Nitrate", Description="Nitrate content"),
        WaterProperty(Name="Chloride", Description="Chloride content"),
        WaterProperty(Name="Lead", Description="Lead content"),
        WaterProperty(Name="Turbidity", Description="Turbidity level"),
        WaterProperty(Name="Fluoride", Description="Fluoride content"),
        WaterProperty(Name="Copper", Description="Copper content"),
        WaterProperty(Name="Odor", Description="Odor level"),
        WaterProperty(Name="Sulfate", Description="Sulfate content"),
        WaterProperty(Name="Chlorine", Description="Chlorine content"),
        WaterProperty(Name="Manganese", Description="Manganese content"),
        WaterProperty(Name="Total Dissolved Solids", Description="Total dissolved solids content")
    ]
    for property in water_properties:
        existing_property = session.query(WaterProperty).filter_by(Name=property.Name).first()
        if not existing_property:
            session.add(property)
    session.commit()

    # Seed water data
    water_data = [
        WaterData(WaterDataID=1, ProductID="1", Date="2023-01-01 00:00:00", Description="Water data A"),
        WaterData(WaterDataID=2, ProductID="2", Date="2023-01-02 00:00:00", Description="Water data B")
    ]
    for data in water_data:
        existing_data = session.query(WaterData).filter_by(WaterDataID=data.WaterDataID).first()
        if not existing_data:
            session.add(data)
    session.commit()

    # Seed water data details
    water_data_details = [
        WaterDataDetail(WaterDataDetailID=1, WaterDataID=1, WaterPropertyID=1, Value=7.0),
        WaterDataDetail(WaterDataDetailID=2, WaterDataID=1, WaterPropertyID=2, Value=0.02),
        WaterDataDetail(WaterDataDetailID=3, WaterDataID=2, WaterPropertyID=1, Value=6.5),
        WaterDataDetail(WaterDataDetailID=4, WaterDataID=2, WaterPropertyID=2, Value=0.03)
    ]
    for detail in water_data_details:
        existing_detail = session.query(WaterDataDetail).filter_by(WaterDataDetailID=detail.WaterDataDetailID).first()
        if not existing_detail:
            session.add(detail)
    session.commit()

    # Seed water quality
    water_qualities = [
        WaterQuality(Name="Clean", Description="Clean water"),
        WaterQuality(Name="Dirty", Description="Dirty water")
    ]
    for quality in water_qualities:
        existing_quality = session.query(WaterQuality).filter_by(Name=quality.Name).first()
        if not existing_quality:
            session.add(quality)
    session.commit()

    # Seed water quality predictions
    water_quality_predictions = [
        WaterQualityPrediction(WaterQualityPredictionID=1, WaterDataID=1, WaterQualityID=1),
        WaterQualityPrediction(WaterQualityPredictionID=2, WaterDataID=2, WaterQualityID=2)
    ]
    for prediction in water_quality_predictions:
        existing_prediction = session.query(WaterQualityPrediction).filter_by(WaterQualityPredictionID=prediction.WaterQualityPredictionID).first()
        if not existing_prediction:
            session.add(prediction)
    session.commit()

# Run the seeder
if __name__ == "__main__":
    seed_data()
    session.close()