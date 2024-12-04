from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, DECIMAL
from sqlalchemy.orm import relationship
from database import Base

# LtRole Table
class Role(Base):
    __tablename__ = "LtRole"
    RoleID = Column(Integer, primary_key=True)
    Name = Column(String(36), nullable=False)
    Description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="role")


# MsUser Table
class User(Base):
    __tablename__ = "MsUser"
    UserID = Column(String(36), primary_key=True)
    FirstName = Column(String(36), nullable=True)
    LastName = Column(String(36), nullable=True)
    Email = Column(String(255), nullable=False, unique=True)
    Password = Column(String(255), nullable=False)
    Role = Column(Integer, ForeignKey("LtRole.RoleID"))

    role = relationship("Role", back_populates="users")
    company_mappings = relationship("UserCompanyMapping", back_populates="user")


# MsUserCompanyMapping Table
class UserCompanyMapping(Base):
    __tablename__ = "MsUserCompanyMapping"
    UserCompanyID = Column(Integer, primary_key=True)
    UserID = Column(String(36), ForeignKey("MsUser.UserID"))
    CompanyID = Column(String(36), ForeignKey("MsCompany.CompanyID"))

    user = relationship("User", back_populates="company_mappings")
    company = relationship("Company", back_populates="user_mappings")


# MsCompany Table
class Company(Base):
    __tablename__ = "MsCompany"
    CompanyID = Column(String(36), primary_key=True)
    Name = Column(String(50), nullable=False)
    Description = Column(Text, nullable=True)
    Address = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    PhoneNumber = Column(String(20), nullable=False)
    Website = Column(String(255), nullable=True)

    user_mappings = relationship("UserCompanyMapping", back_populates="company")
    products = relationship("Product", back_populates="company")


# MsProduct Table
class Product(Base):
    __tablename__ = "MsProduct"
    ProductID = Column(String(36), primary_key=True)
    Name = Column(String(50), nullable=False)
    Description = Column(String(255), nullable=True)
    Image = Column(Text, nullable=True)
    CompanyID = Column(String(36), ForeignKey("MsCompany.CompanyID"))

    company = relationship("Company", back_populates="products")
    water_data = relationship("WaterData", back_populates="product")


# LtWaterProperty Table
class WaterProperty(Base):
    __tablename__ = "LtWaterProperty"
    WaterPropertyID = Column(Integer, primary_key=True)
    Name = Column(String(36), nullable=False)
    Description = Column(String(255), nullable=True)


# TrWaterData Table
class WaterData(Base):
    __tablename__ = "TrWaterData"
    WaterDataID = Column(Integer, primary_key=True)
    ProductID = Column(String(36), ForeignKey("MsProduct.ProductID"))
    Date = Column(DateTime, nullable=False)
    Image = Column(Text, nullable=True)
    Description = Column(String(255), nullable=True)

    product = relationship("Product", back_populates="water_data")
    water_details = relationship("WaterDataDetail", back_populates="water_data")
    quality_predictions = relationship("WaterQualityPrediction", back_populates="water_data")


# TrWaterDataDetail Table
class WaterDataDetail(Base):
    __tablename__ = "TrWaterDataDetail"
    WaterDataDetailID = Column(Integer, primary_key=True)
    WaterDataID = Column(Integer, ForeignKey("TrWaterData.WaterDataID"))
    WaterPropertyID = Column(Integer, ForeignKey("LtWaterProperty.WaterPropertyID"))
    Value = Column(DECIMAL, nullable=False)

    water_data = relationship("WaterData", back_populates="water_details")


# TrWaterQualityPrediction Table
class WaterQualityPrediction(Base):
    __tablename__ = "TrWaterQualityPrediction"
    WaterQualityPredictionID = Column(Integer, primary_key=True)
    WaterDataID = Column(Integer, ForeignKey("TrWaterData.WaterDataID"))
    WaterQualityID = Column(Integer, ForeignKey("LtWaterQuality.WaterQualityID"))

    water_data = relationship("WaterData", back_populates="quality_predictions")


# LtWaterQuality Table
class WaterQuality(Base):
    __tablename__ = "LtWaterQuality"
    WaterQualityID = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False)
    Description = Column(String(255), nullable=True)
