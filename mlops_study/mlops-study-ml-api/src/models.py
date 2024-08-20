from sqlalchemy import Column, Integer, String

from src.database import Base


class ModelApiLog(Base):
    __tablename__ = "model_api_log"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    model_version = Column(String)
    log_type = Column(String)
    payload = Column(String)
