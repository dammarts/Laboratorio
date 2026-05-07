from sqlalchemy.orm import Session
from app.repositories.laboratorio_repository import LaboratorioRepository
from app.schemas.laboratorio_schema import LaboratorioCreate, LaboratorioUpdate

# Instanciar el repositorio
repo = LaboratorioRepository()

class LaboratorioService:

    def obtener_todos(self, db: Session, skip: int = 0, limit: int = 100):
        return repo.obtener_laboratorios(db, skip=skip, limit=limit)

    def obtener_por_id(self, db: Session, laboratorio_id: int):
        # Agregar lógica más adelante para lanzar error 404 por si no se encuentra
        return repo.obtener_laboratorio_por_id(db, laboratorio_id)

    def crear(self, db: Session, laboratorio: LaboratorioCreate):
        # Mandar a guardar al repositorio
        return repo.crear_laboratorio(db, laboratorio)

    def actualizar(self, db: Session, laboratorio_id: int, laboratorio_data: LaboratorioUpdate):
        return repo.actualizar_laboratorio(db, laboratorio_id, laboratorio_data)

    def desactivar(self, db: Session, laboratorio_id: int):
        return repo.desactivar_laboratorio(db, laboratorio_id)