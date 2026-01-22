from fastapi import FastAPI, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import shutil
import os


# 1. Configuración de la Base de Datos
DATABASE_URL = "sqlite:///./momentos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo de la Tabla (Cómo se ve en la base de datos)
class RecuerdoDB(Base):
    __tablename__ = "recuerdos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    desc = Column(String)
    palabra = Column(String)
    ruta_foto = Column(String)

# Creamos la tabla físicamente
Base.metadata.create_all(bind=engine)

# 3. Esquema para recibir datos (Pydantic)
class RecuerdoSchema(BaseModel):
    titulo: str
    desc: str
    palabra: str

    class Config:
        orm_mode = True

app = FastAPI()

# Seguridad CORS (La que ya tenías)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Función para conectar a la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- RUTAS ---

@app.get("/recuerdos")
def obtener_recuerdos(db: Session = Depends(get_db)):
    # Buscamos todos los recuerdos en la base de datos
    return db.query(RecuerdoDB).all()

@app.post("/recuerdos")
def guardar_recuerdo(nuevo: RecuerdoSchema, db: Session = Depends(get_db)):
    # Creamos un registro nuevo
    db_recuerdo = RecuerdoDB(titulo=nuevo.titulo, desc=nuevo.desc, palabra=nuevo.palabra)
    db.add(db_recuerdo)
    db.commit() # ¡Guardado permanente!
    return {"mensaje": "Guardado en disco duro"}

@app.post("/recuerdos-con-foto")
async def guardar_con_foto(
    titulo: str = Form(...),
    desc: str = Form(...),
    palabra: str = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Definimos la ruta donde se guardará físicamente
    ruta_archivo = os.path.join("uploads", foto.filename)
    
    # 2. Guardamos el archivo
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    # 3. GUARDAMOS EN LA DB (Fuera del 'with' para mayor seguridad)
    # Guardamos 'uploads/nombre.jpg' para que coincida con el app.mount
    db_recuerdo = RecuerdoDB(
        titulo = titulo,
        desc = desc,
        palabra = palabra,
        ruta_foto = ruta_archivo  # Esto guardará "uploads/nombre_de_la_foto.jpg"
    )
        
    db.add(db_recuerdo)
    db.commit()
    db.refresh(db_recuerdo)
    
    return {"mensaje": "Foto y recuerdo guardados", "id": db_recuerdo.id}

@app.delete("/recuerdos/{recuerdo_id}")
def borrar_recuerdo(recuerdo_id: int, db: Session = Depends(get_db)):
    # 1. Buscar el recuerdo por su ID
    db_recuerdo = db.query(RecuerdoDB).filter(RecuerdoDB.id == recuerdo_id).first()
    
    if not db_recuerdo:
        return {"error": "Recuerdo no encontrado"}

    # 2. Borrar la foto física de la carpeta 'uploads' si existe
    if db_recuerdo.ruta_foto and os.path.exists(db_recuerdo.ruta_foto):
        os.remove(db_recuerdo.ruta_foto)

    # 3. Borrar el registro de la base de datos
    db.delete(db_recuerdo)
    db.commit()
    
    return {"mensaje": "Recuerdo eliminado correctamente"}
    