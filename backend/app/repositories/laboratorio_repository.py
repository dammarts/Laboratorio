from sqlalchemy.orm import Session
from app.models.laboratorio import Laboratorio
from app.schemas.laboratorio_schema import LaboratorioCreate, LaboratorioUpdate

class LaboratorioRepository:

    def obtener_laboratorios(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Laboratorio).order_by(Laboratorio.laboratorio_id).offset(skip).limit(limit).all()

    def obtener_laboratorio_por_id(self, db: Session, laboratorio_id: int):
        """Busca un laboratorio específico por su ID"""
        return db.query(Laboratorio).filter(Laboratorio.laboratorio_id == laboratorio_id).first()

    def crear_laboratorio(self, db: Session, laboratorio: LaboratorioCreate):
        """Guarda un nuevo laboratorio en la base de datos"""
        db_laboratorio = Laboratorio(**laboratorio.model_dump())
        db.add(db_laboratorio)
        db.commit()
        db.refresh(db_laboratorio)
        return db_laboratorio

    def actualizar_laboratorio(self, db: Session, laboratorio_id: int, laboratorio_data: LaboratorioUpdate):
        """Actualiza los datos de un laboratorio existente"""
        db_laboratorio = self.obtener_laboratorio_por_id(db, laboratorio_id)
        if db_laboratorio:
            update_data = laboratorio_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_laboratorio, key, value)
            db.commit()
            db.refresh(db_laboratorio)
        return db_laboratorio

    def desactivar_laboratorio(self, db: Session, laboratorio_id: int):
        """Desactiva un laboratorio en lugar de borrarlo físicamente (Soft Delete)"""
        db_laboratorio = self.obtener_laboratorio_por_id(db, laboratorio_id)

        if db_laboratorio:
            db_laboratorio.estado = False
            db.commit()
            db.refresh(db_laboratorio)

        return db_laboratorio
