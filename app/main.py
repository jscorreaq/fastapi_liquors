from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, models, schemas
from .database import engine, get_db, verify_tables
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear las tablas de la base de datos
models.Base.metadata.create_all(bind=engine)

# Verificar las tablas creadas
tables = verify_tables()
logger.info(f"Tablas disponibles en la base de datos: {tables}")

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Licores API",
    description="API para gestión de tienda de licores",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando la aplicación...")
    tables = verify_tables()
    if not tables:
        logger.warning("No se encontraron tablas en la base de datos")
    else:
        logger.info(f"Tablas encontradas: {tables}")

#############################################
# ENDPOINTS PARA LICORES
#############################################

@app.post("/licores/", response_model=schemas.Liquor, tags=["Licores"])
def create_liquor(liquor: schemas.LiquorCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo licor
    - **name**: Nombre del licor
    - **brand**: Marca del licor
    - **description**: Descripción del licor
    - **category**: Categoría (WHISKEY, VODKA, RON, etc.)
    - **price**: Precio (mayor que 0)
    - **alcohol_content**: Contenido de alcohol
    - **volume_ml**: Volumen en mililitros
    - **stock**: Cantidad en inventario
    - **supplier**: Proveedor
    """
    try:
        logger.info(f"Intentando crear licor: {liquor.dict()}")
        db_liquor = crud.create_liquor(db=db, liquor=liquor)
        logger.info(f"Licor creado exitosamente con ID: {db_liquor.id}")
        return db_liquor
    except Exception as e:
        logger.error(f"Error al crear licor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/licores/", response_model=List[schemas.Liquor], tags=["Licores"])
def read_liquors(
    skip: int = 0,
    limit: int = 100,
    category: Optional[models.LiquorCategory] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de licores con filtros opcionales
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **category**: Filtrar por categoría
    """
    try:
        if category:
            logger.info(f"Buscando licores por categoría: {category}")
            liquors = crud.get_liquors_by_category(db, category)
        else:
            logger.info(f"Obteniendo lista de licores (skip={skip}, limit={limit})")
            liquors = crud.get_liquors(db, skip=skip, limit=limit)
        logger.info(f"Se encontraron {len(liquors)} licores")
        return liquors
    except Exception as e:
        logger.error(f"Error al obtener licores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/licores/{liquor_id}", response_model=schemas.Liquor, tags=["Licores"])
def read_liquor(liquor_id: int, db: Session = Depends(get_db)):
    """
    Obtener un licor por su ID
    """
    db_liquor = crud.get_liquor(db, liquor_id=liquor_id)
    if db_liquor is None:
        raise HTTPException(status_code=404, detail="Licor no encontrado")
    return db_liquor

@app.put("/licores/{liquor_id}", response_model=schemas.Liquor, tags=["Licores"])
def update_liquor(
    liquor_id: int,
    liquor_data: schemas.LiquorUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un licor existente
    """
    db_liquor = crud.update_liquor(db, liquor_id=liquor_id, liquor_data=liquor_data)
    if db_liquor is None:
        raise HTTPException(status_code=404, detail="Licor no encontrado")
    return db_liquor

@app.delete("/licores/{liquor_id}", response_model=schemas.Liquor, tags=["Licores"])
def delete_liquor(liquor_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un licor
    """
    db_liquor = crud.delete_liquor(db, liquor_id=liquor_id)
    if db_liquor is None:
        raise HTTPException(status_code=404, detail="Licor no encontrado")
    return db_liquor

#############################################
# ENDPOINTS PARA VENTAS
#############################################

@app.post("/ventas/", response_model=schemas.Sale, tags=["Ventas"])
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva venta
    - Registra la venta
    - Actualiza el inventario
    - Crea las líneas de venta
    """
    return crud.create_sale(db=db, sale=sale)

@app.get("/ventas/", response_model=List[schemas.Sale], tags=["Ventas"])
def read_sales(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de ventas
    - **customer_id**: Filtrar por ID de cliente (opcional)
    """
    if customer_id:
        return crud.get_sales_by_customer(db, customer_id)
    return crud.get_sales(db, skip=skip, limit=limit)

@app.get("/ventas/{sale_id}", response_model=schemas.Sale, tags=["Ventas"])
def read_sale(sale_id: int, db: Session = Depends(get_db)):
    """
    Obtener una venta por su ID
    """
    db_sale = crud.get_sale(db, sale_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return db_sale

@app.put("/ventas/{sale_id}/status", response_model=schemas.Sale, tags=["Ventas"])
def update_sale_status(
    sale_id: int,
    status: str = Query(..., regex="^(completed|cancelled|pending)$"),
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de una venta
    - **status**: Nuevo estado (completed, cancelled, pending)
    """
    db_sale = crud.update_sale_status(db, sale_id=sale_id, status=status)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return db_sale

#############################################
# ENDPOINTS PARA INVENTARIO
#############################################

@app.get("/inventario/bajo-stock", response_model=List[schemas.Liquor], tags=["Inventario"])
def check_low_stock(db: Session = Depends(get_db)):
    """
    Obtener lista de licores con stock bajo
    """
    return crud.check_low_stock(db)

@app.put("/inventario/{liquor_id}/stock", response_model=schemas.Liquor, tags=["Inventario"])
def update_stock(
    liquor_id: int,
    quantity: int = Query(..., description="Cantidad a agregar (positivo) o restar (negativo)"),
    db: Session = Depends(get_db)
):
    """
    Actualizar el stock de un licor
    - **quantity**: Cantidad a agregar (positivo) o restar (negativo)
    """
    db_liquor = crud.update_stock(db, liquor_id=liquor_id, quantity=quantity)
    if db_liquor is None:
        raise HTTPException(status_code=404, detail="Licor no encontrado")
    return db_liquor

# Middleware para CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)
