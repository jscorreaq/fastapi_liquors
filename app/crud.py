from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError

#############################################
# OPERACIONES CRUD PARA LICORES
#############################################

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_liquors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Liquor]:
    """Obtiene lista de licores con paginación"""
    try:
        logger.info(f"Obteniendo licores (skip={skip}, limit={limit})")
        liquors = db.query(models.Liquor).offset(skip).limit(limit).all()
        logger.info(f"Se encontraron {len(liquors)} licores")
        return liquors
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener licores: {str(e)}")
        raise

def get_liquor(db: Session, liquor_id: int) -> Optional[models.Liquor]:
    """Obtiene un licor por su ID"""
    try:
        logger.info(f"Buscando licor con ID: {liquor_id}")
        liquor = db.query(models.Liquor).filter(models.Liquor.id == liquor_id).first()
        if liquor:
            logger.info(f"Licor encontrado: {liquor.name}")
        else:
            logger.warning(f"No se encontró licor con ID: {liquor_id}")
        return liquor
    except SQLAlchemyError as e:
        logger.error(f"Error al buscar licor: {str(e)}")
        raise

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
    try:
        logger.info(f"Creando nuevo licor: {liquor.dict()}")
        db_liquor = models.Liquor(**liquor.dict())
        db.add(db_liquor)
        db.flush()  # Flush para obtener el ID antes del commit
        logger.info(f"Licor creado con ID: {db_liquor.id}")
        db.commit()
        logger.info("Transacción completada exitosamente")
        db.refresh(db_liquor)
        return db_liquor
    except SQLAlchemyError as e:
        logger.error(f"Error al crear licor: {str(e)}")
        db.rollback()
        raise

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
    try:
        logger.info(f"Actualizando licor ID: {liquor_id}")
        db_liquor = get_liquor(db, liquor_id)
        if db_liquor:
            update_data = liquor_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_liquor, key, value)
            db_liquor.updated_at = datetime.utcnow()
            db.flush()
            logger.info(f"Licor actualizado: {db_liquor.name}")
            db.commit()
            db.refresh(db_liquor)
        return db_liquor
    except SQLAlchemyError as e:
        logger.error(f"Error al actualizar licor: {str(e)}")
        db.rollback()
        raise

def delete_liquor(db: Session, liquor_id: int) -> Optional[models.Liquor]:
    """Elimina un licor de la base de datos"""
    try:
        logger.info(f"Eliminando licor ID: {liquor_id}")
        db_liquor = get_liquor(db, liquor_id)
        if db_liquor:
            db.delete(db_liquor)
            db.commit()
            logger.info(f"Licor eliminado: {db_liquor.name}")
        return db_liquor
    except SQLAlchemyError as e:
        logger.error(f"Error al eliminar licor: {str(e)}")
        db.rollback()
        raise

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
    try:
        logger.info("Iniciando creación de venta")
        # 1. Crear la venta principal
        db_sale = models.Sale(
            customer_name=sale.customer_name,
            customer_id=sale.customer_id,
            total=sale.total,
            payment_method=sale.payment_method
        )
        db.add(db_sale)
        db.flush()  # Obtenemos el ID de la venta antes de crear las líneas
        logger.info(f"Venta creada con ID: {db_sale.id}")

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
                liquor.is_available = liquor.stock > 0
                logger.info(f"Stock actualizado para licor {liquor.id}: {liquor.stock}")

        # Confirmamos todos los cambios en una sola transacción
        db.commit()
        logger.info("Venta completada exitosamente")
        db.refresh(db_sale)
        return db_sale
    except SQLAlchemyError as e:
        logger.error(f"Error al crear venta: {str(e)}")
        db.rollback()
        raise

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