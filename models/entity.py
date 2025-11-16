# models/entity.py
# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SAEnum

from .base import Base


class StructType(str, Enum):
    """Structural type of an entity in the knowledge graph.

    struct_type : E -> {CANONICAL, CLASS, RELATION, INSTANCE}
    """

    CANONICAL = "canonical"
    CLASS = "class"
    RELATION = "relation"
    INSTANCE = "instance"


class LogicalEntityType(str, Enum):
    """Logical (semantic) type of an entity.

    entity_type : E -> L ∪ {∅}
    L = {PERSON, ORGANIZATION, PLACE, TIME, VALUE,
         DOCUMENT, EVENT, ROLE, UNKNOWN}
    """

    PERSON = "person"
    ORGANIZATION = "organization"
    PLACE = "place"
    TIME = "time"
    VALUE = "value"
    DOCUMENT = "document"
    EVENT = "event"
    ROLE = "role"
    UNKNOWN = "unknown"


class Entity(Base):
    __tablename__ = "entity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("entity.id"),
        nullable=True,
    )

    # struct_type: CANONICAL, CLASS, RELATION, INSTANCE
    struct_type: Mapped[StructType] = mapped_column(
        SAEnum(StructType, native_enum=False, length=32),
        nullable=False,
    )

    # entity_type: um dos 9 tipos lógicos, ou NULL para RELATION
    entity_type: Mapped[Optional[LogicalEntityType]] = mapped_column(
        SAEnum(LogicalEntityType, native_enum=False, length=32),
        nullable=True,
    )

    # Para RELATION: define a assinatura lógica dom/rng
    domain_entity_type: Mapped[Optional[LogicalEntityType]] = mapped_column(
        SAEnum(LogicalEntityType, native_enum=False, length=32),
        nullable=True,
    )
    range_entity_type: Mapped[Optional[LogicalEntityType]] = mapped_column(
        SAEnum(LogicalEntityType, native_enum=False, length=32),
        nullable=True,
    )

    fingerprint: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    normalized_name: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        index=True,
    )
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    # Self-referential hierarchy
    parent: Mapped[Optional["Entity"]] = relationship(
        "Entity",
        remote_side="Entity.id",
        back_populates="children",
    )
    children: Mapped[List["Entity"]] = relationship(
        "Entity",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    # Relationships as subject/predicate/object (triples)
    subject_relationships: Mapped[List["EntityRelationship"]] = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.subject_id",
        back_populates="subject",
        cascade="all, delete-orphan",
    )
    predicate_relationships: Mapped[List["EntityRelationship"]] = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.predicate_id",
        back_populates="predicate",
    )
    object_relationships: Mapped[List["EntityRelationship"]] = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.object_id",
        back_populates="object_entity",
    )

    __table_args__ = (
        # Nome + struct_type + entity_type precisa ser único
        UniqueConstraint(
            "name",
            "struct_type",
            "entity_type",
            name="uq_entity_name_struct_type_entity_type",
        ),
        Index("ix_entity_name_struct_type", "name", "struct_type"),
        Index("ix_entity_parent", "parent_id"),
        Index("ix_entity_created", "created_at"),
        CheckConstraint(
            """
            (
                struct_type = 'relation'
                AND entity_type IS NULL
                AND domain_entity_type IS NOT NULL
                AND range_entity_type IS NOT NULL
            )
            OR (
                struct_type <> 'relation'
                AND domain_entity_type IS NULL
                AND range_entity_type IS NULL
            )
            """,
            name="ck_entity_relation_signature_fields",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Entity(id={self.id}, name='{self.name}', "
            f"struct_type='{self.struct_type.value}', "
            f"entity_type='{self.entity_type.value if self.entity_type else None}')>"
        )


class EntityRelationship(Base):
    __tablename__ = "entity_relationship"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entity.id"),
        nullable=False,
    )
    predicate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entity.id"),
        nullable=False,
    )
    object_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entity.id"),
        nullable=False,
    )

    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )

    subject: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[subject_id],
        back_populates="subject_relationships",
    )
    predicate: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[predicate_id],
        back_populates="predicate_relationships",
    )
    object_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[object_id],
        back_populates="object_relationships",
    )

    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "predicate_id",
            "object_id",
            name="uq_triple_subject_pred_obj",
        ),
        Index("ix_rel_subject", "subject_id"),
        Index("ix_rel_object", "object_id"),
        Index("ix_rel_predicate", "predicate_id"),
        Index("ix_rel_weight", "weight"),
        Index("ix_rel_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            "<EntityRelationship(subject=%r, predicate=%r, object=%r)>"
            % (self.subject_id, self.predicate_id, self.object_id)
        )


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )
    normalized_name: Mapped[Optional[str]] = mapped_column(String(200))
    fingerprint: Mapped[Optional[str]] = mapped_column(String(64))
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=[])
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )
    normalized_name: Mapped[Optional[str]] = mapped_column(String(200))
    fingerprint: Mapped[Optional[str]] = mapped_column(String(64))
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=[])
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )


class EntitySynonym(Base):
    __tablename__ = "entity_synonym"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_entity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entity.id", ondelete="CASCADE"),
        nullable=False,
    )
    synonym: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
    )

    canonical_entity: Mapped["Entity"] = relationship("Entity")
