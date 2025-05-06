# Importamos las dependencias necesarias de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Definimos la URL de conexión a la base de datos SQLite
# SQLite es una base de datos ligera que almacena los datos en un archivo local
DATABASE_URL = "sqlite:///./fastapi_liquors.db"

# Creamos el motor de SQLAlchemy
# check_same_thread=False permite que SQLite sea accedido por múltiples hilos
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Creamos una clase de sesión local
# Esta clase se utilizará para crear nuevas sesiones de base de datos
# autocommit=False: Los cambios no se guardan automáticamente
# autoflush=False: Los cambios no se sincronizan automáticamente con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creamos la clase base para los modelos declarativos
# Esta clase será la base para todas las clases/modelos de la BD
Base = declarative_base()
