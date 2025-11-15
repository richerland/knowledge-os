# knowledge_os_loader.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.entity import Entity, StructType, LogicalEntityType


@dataclass
class EntityDef:
    id: str
    name: str
    struct_type: str
    entity_type: Optional[str]
    domain_entity_type: Optional[str]
    range_entity_type: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class RelationDef:
    id: str
    name: str
    struct_type: str
    domain_entity_type: str
    range_entity_type: str
    metadata: Dict[str, Any]


@dataclass
class Ontology:
    ontology_id: str
    version: str
    entity_types: List[str]
    struct_types: List[str]
    entities: List[EntityDef]
    relations: List[RelationDef]


def load_ontology_from_file(path: str | Path) -> Ontology:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    entities = [
        EntityDef(
            id=e["id"],
            name=e["name"],
            struct_type=e["struct_type"],
            entity_type=e.get("entity_type"),
            domain_entity_type=e.get("domain_entity_type"),
            range_entity_type=e.get("range_entity_type"),
            metadata=e.get("metadata", {}),
        )
        for e in raw.get("entities", [])
    ]

    relations = [
        RelationDef(
            id=r["id"],
            name=r["name"],
            struct_type=r["struct_type"],
            domain_entity_type=r["domain_entity_type"],
            range_entity_type=r["range_entity_type"],
            metadata=r.get("metadata", {}),
        )
        for r in raw.get("relations", [])
    ]

    return Ontology(
        ontology_id=raw.get("ontology_id", "knowledge_os_core"),
        version=raw.get("version", "0.0.0"),
        entity_types=raw.get("entity_types", []),
        struct_types=raw.get("struct_types", []),
        entities=entities,
        relations=relations,
    )


def validate_ontology(ontology: Ontology) -> None:
    expected_entity_types = {t.value for t in LogicalEntityType}
    expected_struct_types = {s.value for s in StructType}

    if set(ontology.entity_types) != expected_entity_types:
        raise ValueError(
            f"Entity types mismatch. Expected {sorted(expected_entity_types)}, "
            f"got {sorted(ontology.entity_types)}."
        )

    if set(ontology.struct_types) != expected_struct_types:
        raise ValueError(
            f"Struct types mismatch. Expected {sorted(expected_struct_types)}, "
            f"got {sorted(ontology.struct_types)}."
        )

    for entity in ontology.entities:
        if entity.struct_type not in expected_struct_types:
            raise ValueError(
                f"Entity {entity.id} has invalid struct_type "
                f"{entity.struct_type}."
            )

        if entity.struct_type in {"canonical", "class", "instance"}:
            if (
                entity.entity_type is None
                or entity.entity_type not in expected_entity_types
            ):
                raise ValueError(
                    f"Entity {entity.id} with struct_type "
                    f"{entity.struct_type} must have entity_type in entity_types."
                )
            if entity.domain_entity_type is not None:
                raise ValueError(
                    f"Entity {entity.id} with struct_type "
                    f"{entity.struct_type} cannot have domain_entity_type."
                )
            if entity.range_entity_type is not None:
                raise ValueError(
                    f"Entity {entity.id} with struct_type "
                    f"{entity.struct_type} cannot have range_entity_type."
                )

        if entity.struct_type == "relation":
            if entity.entity_type is not None:
                raise ValueError(
                    f"Relation-entity {entity.id} must have entity_type = null."
                )
            if (
                entity.domain_entity_type is None
                or entity.domain_entity_type not in expected_entity_types
            ):
                raise ValueError(
                    f"Relation-entity {entity.id} must have valid "
                    f"domain_entity_type in entity_types."
                )
            if (
                entity.range_entity_type is None
                or entity.range_entity_type not in expected_entity_types
            ):
                raise ValueError(
                    f"Relation-entity {entity.id} must have valid "
                    f"range_entity_type in entity_types."
                )

    for rel in ontology.relations:
        if rel.struct_type != "relation":
            raise ValueError(
                f"Relation {rel.id} must have struct_type='relation'."
            )
        if rel.domain_entity_type not in expected_entity_types:
            raise ValueError(
                f"Relation {rel.id} has invalid domain_entity_type "
                f"{rel.domain_entity_type}."
            )
        if rel.range_entity_type not in expected_entity_types:
            raise ValueError(
                f"Relation {rel.id} has invalid range_entity_type "
                f"{rel.range_entity_type}."
            )


def _get_struct_type(value: str) -> StructType:
    return StructType(value)


def _get_entity_type(value: Optional[str]) -> Optional[LogicalEntityType]:
    if value is None:
        return None
    return LogicalEntityType(value)


def seed_ontology(session: Session, ontology: Ontology) -> None:
    """Popula a tabela Entity via ORM, a partir de um objeto Ontology.

    Usa UniqueConstraint (name, struct_type, entity_type) para upsert.
    """
    validate_ontology(ontology)

    # Seed entidades (CANONICAL / CLASS / INSTANCE / RELATION modeladas em 'entities')
    for entity_def in ontology.entities:
        struct_type = _get_struct_type(entity_def.struct_type)
        entity_type = _get_entity_type(entity_def.entity_type)
        domain_type = _get_entity_type(entity_def.domain_entity_type)
        range_type = _get_entity_type(entity_def.range_entity_type)

        db_entity = (
            session.query(Entity)
            .filter(
                Entity.name == entity_def.name,
                Entity.struct_type == struct_type,
                Entity.entity_type == entity_type,
            )
            .one_or_none()
        )

        if db_entity is None:
            db_entity = Entity(
                name=entity_def.name,
                struct_type=struct_type,
                entity_type=entity_type,
                domain_entity_type=domain_type,
                range_entity_type=range_type,
                meta=entity_def.metadata or {},
            )
            session.add(db_entity)
        else:
            db_entity.domain_entity_type = domain_type
            db_entity.range_entity_type = range_type
            db_entity.meta = entity_def.metadata or {}

    # Seed relations da seção 'relations' como entidades struct_type=relation
    for rel_def in ontology.relations:
        struct_type = StructType.RELATION
        domain_type = _get_entity_type(rel_def.domain_entity_type)
        range_type = _get_entity_type(rel_def.range_entity_type)

        db_entity = (
            session.query(Entity)
            .filter(
                Entity.name == rel_def.name,
                Entity.struct_type == struct_type,
                Entity.entity_type.is_(None),
            )
            .one_or_none()
        )

        if db_entity is None:
            db_entity = Entity(
                name=rel_def.name,
                struct_type=struct_type,
                entity_type=None,
                domain_entity_type=domain_type,
                range_entity_type=range_type,
                meta=rel_def.metadata or {},
            )
            session.add(db_entity)
        else:
            db_entity.domain_entity_type = domain_type
            db_entity.range_entity_type = range_type
            db_entity.meta = rel_def.metadata or {}

    session.commit()


def seed_from_path(session: Session, path: str | Path) -> None:
    ontology = load_ontology_from_file(path)
    seed_ontology(session, ontology)
