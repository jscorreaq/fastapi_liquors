# Importamos las dependencias necesarias de SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargamos las variables de entorno
load_dotenv()

# Obtenemos la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Definimos la URL de conexión a la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    default=f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"
)

logger.info(f"Usando base de datos en: {DATABASE_URL}")

# Si estamos usando PostgreSQL en Railway, necesitamos modificar la URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuramos el motor de la base de datos
if DATABASE_URL.startswith("sqlite"):
    # Configuración específica para SQLite
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
    logger.info("Usando configuración SQLite")
else:
    # Configuración para PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )
    logger.info("Usando configuración PostgreSQL")

# Creamos una clase de sesión local
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Creamos la clase base para los modelos declarativos
Base = declarative_base()

def verify_tables():
    """
    Verifica qué tablas existen en la base de datos
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tablas existentes en la base de datos: {tables}")
    return tables

def get_db():
    """
    Genera una sesión de base de datos y asegura que se cierre después de usarla
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Crea todas las tablas en la base de datos
    """
    try:
        # Importamos los modelos aquí para evitar importación circular
        from . import models
        logger.info("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        tables = verify_tables()
        if not tables:
            logger.error("No se encontraron tablas después de la creación")
        else:
            logger.info("Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"Error al crear las tablas: {e}")
        raise

def check_db_connection():
    """
    Verifica si la conexión a la base de datos está funcionando
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        return False

# Si este archivo se ejecuta directamente, inicializa la base de datos
if __name__ == "__main__":
    logger.info("Iniciando verificación de la base de datos...")
    
    # Verificar si el archivo de base de datos existe (para SQLite)
    if DATABASE_URL.startswith("sqlite"):
        db_path = os.path.join(BASE_DIR, 'sql_app.db')
        if os.path.exists(db_path):
            logger.info(f"Archivo de base de datos encontrado en: {db_path}")
        else:
            logger.warning(f"No se encontró archivo de base de datos en: {db_path}")
    
    # Verificar conexión
    if check_db_connection():
        # Inicializar la base de datos
        init_db()
        # Verificar tablas
        tables = verify_tables()
        if tables:
            logger.info("Base de datos lista para usar")
        else:
            logger.error("No se encontraron tablas en la base de datos")
