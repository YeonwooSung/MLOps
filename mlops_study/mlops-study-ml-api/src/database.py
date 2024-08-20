import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Metadata 저장소
ml_metadata_url = os.getenv(
    "ML_METADATA_URL",
    "mysql+pymysql://root:root@localhost/mlops_meta"
)
engine = create_engine(ml_metadata_url)
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
