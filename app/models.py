# Importamos los tipos de columnas necesarios de SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
# Importamos la clase Base desde nuestro módulo de base de datos
from .database import Base
from enum import Enum as PyEnum

# Definimos las categorías de licores
class LiquorCategory(PyEnum):
    WHISKEY = "whiskey"
    VODKA = "vodka"
    RON = "ron"
    TEQUILA = "tequila"
    GINEBRA = "ginebra"
    VINO = "vino"
    CERVEZA = "cerveza"
    OTRO = "otro"

# Definimos el modelo Liquor que hereda de Base
class Liquor(Base):
    # Especificamos el nombre de la tabla en la base de datos
    __tablename__ = "liquors"

    # Definimos las columnas de la tabla:
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=False)
    description = Column(String(500))
    category = Column(Enum(LiquorCategory), nullable=False)
    price = Column(Float, nullable=False)
    alcohol_content = Column(Float)
    volume_ml = Column(Integer)
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    supplier = Column(String(100))
    minimum_stock = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con las líneas de venta
    sale_lines = relationship("SaleLine", back_populates="liquor")

# Modelo para las ventas
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_id = Column(String(50))  # Documento de identidad
    total = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="completed")  # completed, cancelled, pending

    # Relación con las líneas de venta
    sale_lines = relationship("SaleLine", back_populates="sale")

# Modelo para las líneas de venta
class SaleLine(Base):
    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    liquor_id = Column(Integer, ForeignKey("liquors.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relaciones
    sale = relationship("Sale", back_populates="sale_lines")
    liquor = relationship("Liquor", back_populates="sale_lines")