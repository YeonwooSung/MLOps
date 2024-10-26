from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.types import JSON

# custom module
from model_db.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(
        String(255),
        primary_key=True,
        comment="project_id",
    )
    project_name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="name of the project",
    )
    description = Column(
        Text,
        nullable=True,
        comment="project description",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
    )


class Model(Base):
    __tablename__ = "models"

    model_id = Column(
        String(255),
        primary_key=True,
        comment="model id",
    )
    project_id = Column(
        String(255),
        ForeignKey("projects.project_id"),
        nullable=False,
        comment="id of the project (foreign key)",
    )
    model_name = Column(
        String(255),
        nullable=False,
        comment="name of the model",
    )
    description = Column(
        Text,
        nullable=True,
        comment="model description",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
    )


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id = Column(
        String(255),
        primary_key=True,
        comment="experiment_id",
    )
    model_id = Column(
        String(255),
        ForeignKey("models.model_id"),
        nullable=False,
        comment="id of the model (foreign key)",
    )
    model_version_id = Column(
        String(255),
        nullable=False,
        comment="model version id",
    )
    parameters = Column(
        JSON,
        nullable=True,
        comment="parameters",
    )
    training_dataset = Column(
        Text,
        nullable=True,
        comment="training data",
    )
    validation_dataset = Column(
        Text,
        nullable=True,
        comment="validation data",
    )
    test_dataset = Column(
        Text,
        nullable=True,
        comment="test data",
    )
    evaluations = Column(
        JSON,
        nullable=True,
        comment="evaluation results",
    )
    artifact_file_paths = Column(
        JSON,
        nullable=True,
        comment="artifact file paths",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
    )
