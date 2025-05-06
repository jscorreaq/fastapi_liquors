# Importamos las clases necesarias de Pydantic
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# Enumeración para las categorías de licores
class LiquorCategory(str, Enum):
    WHISKEY = "whiskey"
    VODKA = "vodka"
    RON = "ron"
    TEQUILA = "tequila"
    GINEBRA = "ginebra"
    VINO = "vino"
    CERVEZA = "cerveza"
    OTRO = "otro"

# Esquema base para los licores
class LiquorBase(BaseModel):
    name: str                    # Nombre del licor
    brand: str                   # Marca del licor
    description: str             # Descripción detallada
    category: LiquorCategory     # Categoría del licor
    price: float = Field(gt=0)   # Precio (debe ser mayor que 0)
    alcohol_content: float       # Contenido de alcohol (%)
    volume_ml: int              # Volumen en mililitros
    stock: int = Field(ge=0)    # Cantidad en inventario
    is_available: bool = True    # Disponibilidad
    supplier: str               # Proveedor
    minimum_stock: int = 5      # Stock mínimo para alertas

# Esquema para crear nuevos licores
class LiquorCreate(LiquorBase):
    pass

# Esquema para actualizar licores existentes
# Hacemos los campos opcionales para actualizaciones parciales
class LiquorUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    category: Optional[LiquorCategory] = None
    price: Optional[float] = None
    alcohol_content: Optional[float] = None
    volume_ml: Optional[int] = None
    stock: Optional[int] = None
    is_available: Optional[bool] = None
    supplier: Optional[str] = None
    minimum_stock: Optional[int] = None

# Esquema para respuestas de la API
class Liquor(LiquorBase):
    id: int                     # ID único del licor
    created_at: datetime        # Fecha de creación
    updated_at: datetime        # Fecha de última actualización
    
    class Config:
        orm_mode = True

# Esquema para ventas de licores
class SaleLine(BaseModel):
    liquor_id: int
    quantity: int = Field(gt=0)
    unit_price: float
    subtotal: float

# Esquema para crear una venta
class SaleCreate(BaseModel):
    customer_name: str
    customer_id: Optional[str]  # Documento de identidad del cliente
    sale_lines: list[SaleLine]
    total: float
    payment_method: str

# Esquema para respuesta de ventas
class Sale(SaleCreate):
    id: int
    sale_date: datetime
    status: str  # "completed", "cancelled", "pending"

    class Config:
        orm_mode = True