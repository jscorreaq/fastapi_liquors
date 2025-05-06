# Importamos las dependencias necesarias de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

# Obtenemos la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Definimos la URL de conexión a la base de datos
# En Railway usaremos PostgreSQL, en local SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    default=f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"
)

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
else:
    # Configuración para PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        echo=True
    )

# Creamos una clase de sesión local
# Esta clase se utilizará para crear nuevas sesiones de base de datos
# autocommit=False: Los cambios no se guardan automáticamente
# autoflush=False: Los cambios no se sincronizan automáticamente con la BD
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Creamos la clase base para los modelos declarativos
# Esta clase será la base para todas las clases/modelos de la BD
Base = declarative_base()

# Función para obtener una sesión de base de datos
def get_db():
    """
    Genera una sesión de base de datos y asegura que se cierre después de usarla
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para inicializar la base de datos
def init_db():
    """
    Crea todas las tablas en la base de datos
    """
    import app.models  # Importamos los modelos aquí para evitar importación circular
    Base.metadata.create_all(bind=engine)

# Función para verificar la conexión a la base de datos
def check_db_connection():
    """
    Verifica si la conexión a la base de datos está funcionando
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return False

# Si este archivo se ejecuta directamente, inicializa la base de datos
if __name__ == "__main__":
    print("Inicializando la base de datos...")
    init_db()
    if check_db_connection():
        print("Base de datos inicializada correctamente")
    else:
        print("Error al inicializar la base de datos")
