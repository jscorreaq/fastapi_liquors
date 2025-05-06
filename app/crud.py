from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime

#############################################
# OPERACIONES CRUD PARA LICORES
#############################################

def get_liquors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Liquor]:
    """Obtiene lista de licores con paginación"""
    return db.query(models.Liquor).offset(skip).limit(limit).all()

def get_liquor(db: Session, liquor_id: int) -> Optional[models.Liquor]:
    """Obtiene un licor por su ID"""
    return db.query(models.Liquor).filter(models.Liquor.id == liquor_id).first()

def get_liquors_by_category(db: Session, category: models.LiquorCategory) -> List[models.Liquor]:
    """Obtiene licores por categoría"""
    return db.query(models.Liquor).filter(models.Liquor.category == category).all()

def create_liquor(db: Session, liquor: schemas.LiquorCreate) -> models.Liquor:
    """
    Crea un nuevo licor en la base de datos
    Args:
        db: Sesión de la base de datos
        liquor: Datos del licor a crear
    Returns:
        El licor creado
    """
    db_liquor = models.Liquor(**liquor.dict())
    db.add(db_liquor)
    db.commit()
    db.refresh(db_liquor)
    return db_liquor

def update_liquor(db: Session, liquor_id: int, liquor_data: schemas.LiquorUpdate) -> Optional[models.Liquor]:
    """
    Actualiza un licor existente
    Args:
        db: Sesión de la base de datos
        liquor_id: ID del licor a actualizar
        liquor_data: Datos nuevos del licor
    Returns:
        El licor actualizado o None si no existe
    """
    db_liquor = get_liquor(db, liquor_id)
    if db_liquor:
        # Actualizamos solo los campos que vienen en la petición
        update_data = liquor_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_liquor, key, value)
        db_liquor.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_liquor)
    return db_liquor

def delete_liquor(db: Session, liquor_id: int) -> Optional[models.Liquor]:
    """Elimina un licor de la base de datos"""
    db_liquor = get_liquor(db, liquor_id)
    if db_liquor:
        db.delete(db_liquor)
        db.commit()
    return db_liquor

#############################################
# OPERACIONES CRUD PARA VENTAS
#############################################

def create_sale(db: Session, sale: schemas.SaleCreate) -> models.Sale:
    """
    Crea una nueva venta y actualiza el inventario
    Este proceso incluye:
    1. Crear el registro de la venta
    2. Crear las líneas de venta
    3. Actualizar el inventario de los productos vendidos
    """
    # 1. Crear la venta principal
    db_sale = models.Sale(
        customer_name=sale.customer_name,
        customer_id=sale.customer_id,
        total=sale.total,
        payment_method=sale.payment_method
    )
    db.add(db_sale)
    db.flush()  # Obtenemos el ID de la venta antes de crear las líneas

    # 2. Crear las líneas de venta y 3. Actualizar inventario
    for line in sale.sale_lines:
        # Creamos la línea de venta
        db_sale_line = models.SaleLine(
            sale_id=db_sale.id,
            liquor_id=line.liquor_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            subtotal=line.subtotal
        )
        db.add(db_sale_line)

        # Actualizamos el inventario del licor
        liquor = get_liquor(db, line.liquor_id)
        if liquor:
            liquor.stock -= line.quantity
            # Actualizamos la disponibilidad basada en el stock
            liquor.is_available = liquor.stock > 0

    # Confirmamos todos los cambios en una sola transacción
    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sale(db: Session, sale_id: int) -> Optional[models.Sale]:
    """Obtiene una venta específica por su ID"""
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()

def get_sales(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sale]:
    """Obtiene lista de ventas con paginación"""
    return db.query(models.Sale).offset(skip).limit(limit).all()

def get_sales_by_customer(db: Session, customer_id: str) -> List[models.Sale]:
    """Obtiene todas las ventas de un cliente específico"""
    return db.query(models.Sale).filter(models.Sale.customer_id == customer_id).all()

def update_sale_status(db: Session, sale_id: int, status: str) -> Optional[models.Sale]:
    """
    Actualiza el estado de una venta
    Estados posibles: "completed", "cancelled", "pending"
    """
    db_sale = get_sale(db, sale_id)
    if db_sale:
        db_sale.status = status
        db.commit()
        db.refresh(db_sale)
    return db_sale

#############################################
# FUNCIONES DE UTILIDAD PARA INVENTARIO
#############################################

def check_low_stock(db: Session) -> List[models.Liquor]:
    """
    Obtiene lista de licores con stock bajo
    Útil para sistema de alertas de reabastecimiento
    """
    return db.query(models.Liquor).filter(
        models.Liquor.stock <= models.Liquor.minimum_stock
    ).all()

def update_stock(db: Session, liquor_id: int, quantity: int) -> Optional[models.Liquor]:
    """
    Actualiza el stock de un licor
    Args:
        quantity: Cantidad a agregar (positivo) o restar (negativo)
    """
    db_liquor = get_liquor(db, liquor_id)
    if db_liquor:
        db_liquor.stock += quantity
        db_liquor.is_available = db_liquor.stock > 0
        db_liquor.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_liquor)
    return db_liquor