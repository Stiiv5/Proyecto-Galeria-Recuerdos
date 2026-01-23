import cloudinary.uploader
from fastapi import FastAPI, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import cloudinary
from cloudinary.utils import cloudinary_url
import os


cloudinary.config( 
  cloud_name = "dtbbgw8jx", 
  api_key = "216869891311618", 
  api_secret = "qIOlQbPWpfz40X1oeqfGq1wO5z0",
  secure = True
)

# 1. Configuración de la Base de Datos
DATABASE_URL = "postgresql://db_recuerdos_user:IfmlFq5IsBRcKHLohglRDBMxmBHvQwC7@dpg-d5pdi814tr6s73aplskg-a/db_recuerdos"
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
    foto: UploadFile = File(...)
):
    
    try: 
        print(f"Intentando subir foto: {foto.filename}")
        
        # Subimos el archivo a cloudinary        
        upload_result = cloudinary.uploader.upload(foto.file)
        print("Subida exitosa a Cloudinary")
        
        # Extraemos la URL segura que nos da cloudinary        
        url_foto = upload_result['secure_url']
        print(f"URL generada: {url_foto}")


        # 3. GUARDAMOS EN LA DB  la URL, no la ruta local
        db = SessionLocal()
        nuevo_recuerdo = RecuerdoDB (
            titulo=titulo, 
            desc=desc, 
            palabra=palabra, 
            ruta_foto=url_foto 
        )
        db.add(nuevo_recuerdo)
        db.commit()
        db.refresh(nuevo_recuerdo)
        db.close()

        return {"status": "Succes", "url": url_foto}
    except Exception as e:
        print(f"ERROR CRITICO: {e}")
        return {"status": "error", "message": str(e)}


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
    