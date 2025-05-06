# API de Gestión de Tienda de Licores

Sistema de gestión para tienda de licores desarrollado con FastAPI y SQLAlchemy. Desplegado en Railway.

## 🌟 Características

- ✨ Gestión completa de inventario de licores
- 🛍️ Sistema de ventas
- 📦 Control de stock
- 📊 Categorización de productos
- 🔍 Búsqueda y filtrado
- 📝 Registro de transacciones
- 🚀 Despliegue automático en Railway

## 🛠️ Requisitos

- Python 3.8+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/jscorreaq/fastapi_liquors.git
cd fastapi_liquors
```

2. Crea un entorno virtual:
```bash
python -m venv liquors
```

3. Activa el entorno virtual:
- Windows:
```bash
.\liquors\Scripts\activate
```
- Linux/Mac:
```bash
source liquors/bin/activate
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
fastapi_liquors/
├── app/
│   ├── __init__.py
│   ├── main.py          # Punto de entrada de la aplicación
│   ├── database.py      # Configuración de la base de datos
│   ├── models.py        # Modelos SQLAlchemy
│   ├── schemas.py       # Esquemas Pydantic
│   └── crud.py         # Operaciones CRUD
├── requirements.txt
├── Procfile            # Configuración para Railway
└── README.md
```

## 💻 Desarrollo Local

1. Inicia el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```

2. Accede a la documentación interactiva:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🌐 Despliegue en Railway

1. Asegúrate de tener una cuenta en [Railway](https://railway.app/)

2. Conecta tu repositorio de GitHub con Railway:
   - Ve a [Railway Dashboard](https://railway.app/dashboard)
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona el repositorio `fastapi_liquors`

3. Configura las variables de entorno en Railway:
   ```
   DATABASE_URL=postgresql://...
   ```

4. Railway detectará automáticamente el Procfile y desplegará la aplicación

5. Accede a tu API en la URL proporcionada por Railway

## 🔄 API Endpoints

### Licores

- `POST /licores/`: Crear nuevo licor
- `GET /licores/`: Listar licores
- `GET /licores/{liquor_id}`: Obtener licor específico
- `PUT /licores/{liquor_id}`: Actualizar licor
- `DELETE /licores/{liquor_id}`: Eliminar licor

### Ventas

- `POST /ventas/`: Crear nueva venta
- `GET /ventas/`: Listar ventas
- `GET /ventas/{sale_id}`: Obtener venta específica
- `PUT /ventas/{sale_id}/status`: Actualizar estado de venta

### Inventario

- `GET /inventario/bajo-stock`: Verificar productos con stock bajo
- `PUT /inventario/{liquor_id}/stock`: Actualizar stock

## 📊 Modelos de Datos

### Licor

```python
{
    "id": int,
    "name": str,
    "brand": str,
    "description": str,
    "category": str,  # (WHISKEY, VODKA, RON, etc.)
    "price": float,
    "alcohol_content": float,
    "volume_ml": int,
    "stock": int,
    "is_available": bool,
    "supplier": str,
    "minimum_stock": int
}
```

### Venta

```python
{
    "id": int,
    "customer_name": str,
    "customer_id": str,
    "sale_lines": [
        {
            "liquor_id": int,
            "quantity": int,
            "unit_price": float,
            "subtotal": float
        }
    ],
    "total": float,
    "payment_method": str,
    "status": str  # (completed, cancelled, pending)
}
```

## 📝 Ejemplos de Uso

### Crear un Nuevo Licor

```bash
curl -X 'POST' \
  'https://fastapi-liquors-production.up.railway.app/licores/' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Johnnie Walker",
    "brand": "Johnnie Walker",
    "description": "Black Label",
    "category": "WHISKEY",
    "price": 89.99,
    "alcohol_content": 40.0,
    "volume_ml": 750,
    "stock": 10,
    "supplier": "Diageo"
  }'
```

### Crear una Nueva Venta

```bash
curl -X 'POST' \
  'https://fastapi-liquors-production.up.railway.app/ventas/' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "Juan Pérez",
    "customer_id": "12345678",
    "sale_lines": [
      {
        "liquor_id": 1,
        "quantity": 2,
        "unit_price": 89.99,
        "subtotal": 179.98
      }
    ],
    "total": 179.98,
    "payment_method": "credit_card"
  }'
```

## 🤝 Contribución

1. Haz un Fork del proyecto
2. Crea una rama para tu función (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 📫 Contacto

Juan Sebastián Correa - [@jscorreaq](https://github.com/jscorreaq)

Link del Proyecto: [https://github.com/jscorreaq/fastapi_liquors](https://github.com/jscorreaq/fastapi_liquors)

API en Railway: [https://fastapi-liquors-production.up.railway.app/](https://fastapi-liquors-production.up.railway.app/)
