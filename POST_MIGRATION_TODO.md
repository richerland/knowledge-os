# Knowledge-OS: Ações Pós-Migração

## 1. Atualizar Código Legado

### 1.1 Substituir Imports
**Arquivos afetados**: 17 arquivos críticos (ver `using_entities_legacy.txt`)

```python
# ANTES (legado)
from models import EntityType

# DEPOIS (novo)
from models import StructType, LogicalEntityType
```

### 1.2 Atualizar Referências a EntityType

**Padrão de substituição**:
```python
# ANTES
entity.entity_type == EntityType.PERSON

# DEPOIS
entity.struct_type == StructType.CANONICAL and entity.entity_type == LogicalEntityType.PERSON
```

**Arquivos prioritários**:
- `api/metadata/entities.py`
- `api/metadata/relationships.py`
- `api/metadata/triples.py`
- `scripts/seed_canonical_graph.py`
- `scripts/normalize_person_roles.py`

### 1.3 Atualizar Queries

```python
# ANTES
session.query(Entity).filter_by(entity_type=EntityType.PERSON)

# DEPOIS
session.query(Entity).filter_by(
    struct_type=StructType.CANONICAL,
    entity_type=LogicalEntityType.PERSON
)
```

## 2. Testar Endpoints

### 2.1 APIs de Metadata
```bash
# Testar cada endpoint
curl -X GET https://docbuilder.d4uimmigration.com/api/metadata/entities
curl -X GET https://docbuilder.d4uimmigration.com/api/metadata/relationships
curl -X GET https://docbuilder.d4uimmigration.com/api/metadata/triples
```

### 2.2 Verificar Respostas
- Checar se entidades retornam `struct_type` e `entity_type`
- Validar hierarquia (parent_id)
- Confirmar 128 entidades carregadas

## 3. Atualizar Scripts

### 3.1 Scripts de Seed
**Arquivos**:
- `scripts/seed_canonical_graph.py`
- `scripts/seed_immigration_vocab.py`
- `scripts/seeds.py`
- `scripts/seeds_consolidated.py`

**Ação**: Substituir por `knowledge_os_loader.py` do repositório knowledge-os

### 3.2 Scripts de Normalização
**Arquivos**:
- `scripts/normalize_person_roles.py`

**Ação**: Atualizar para usar `StructType` + `LogicalEntityType`

## 4. Documentar Migration

### 4.1 Criar Migration Alembic
```bash
cd /home/fastdev/new_docbuilder/backend
alembic revision -m "Add struct_type and domain/range entity types to Entity"
```

### 4.2 Conteúdo da Migration
```python
def upgrade():
    op.add_column('entity', sa.Column('struct_type', sa.String(32)))
    op.add_column('entity', sa.Column('domain_entity_type', sa.String(32)))
    op.add_column('entity', sa.Column('range_entity_type', sa.String(32)))
    op.add_column('entity', sa.Column('aliases', JSONB))
    
    op.drop_constraint('uq_entity_name_type', 'entity')
    op.create_unique_constraint('uq_entity_name_struct_type', 'entity', 
                                ['name', 'struct_type', 'entity_type'])
    op.create_check_constraint('ck_relation_has_domain_range', 'entity',
                               "(struct_type != 'relation') OR "
                               "(domain_entity_type IS NOT NULL AND range_entity_type IS NOT NULL)")
```

## 5. Validar Integridade

### 5.1 Verificar Dados
```sql
-- Total de entidades
SELECT COUNT(*) FROM entity;  -- Deve ser 128

-- Por struct_type
SELECT struct_type, COUNT(*) FROM entity GROUP BY struct_type;
-- canonical: 9
-- class: 119

-- Por entity_type
SELECT entity_type, COUNT(*) FROM entity GROUP BY entity_type;
```

### 5.2 Testar Hierarquia
```sql
-- Entidades com parent
SELECT COUNT(*) FROM entity WHERE parent_id IS NOT NULL;

-- Verificar integridade referencial
SELECT e.name, p.name as parent_name 
FROM entity e 
LEFT JOIN entity p ON e.parent_id = p.id 
WHERE e.parent_id IS NOT NULL 
LIMIT 10;
```

## 6. Atualizar Documentação

### 6.1 README do Projeto
- Adicionar seção sobre Knowledge-OS
- Link para repositório: https://github.com/richerland/knowledge-os
- Explicar nova estrutura de Entity

### 6.2 API Documentation
- Atualizar schemas de resposta
- Adicionar `struct_type` nos exemplos
- Documentar novos campos (`domain_entity_type`, `range_entity_type`)

## 7. Monitoramento

### 7.1 Logs
- Verificar erros relacionados a `EntityType`
- Monitorar queries lentas em Entity
- Checar uso de índices

### 7.2 Performance
```sql
-- Verificar índices
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'entity';
```

## Prioridade de Execução

| Prioridade | Ação | Estimativa |
|------------|------|------------|
| 🔴 Alta | 1.1, 1.2 - Atualizar imports e referências | 2h |
| 🔴 Alta | 2.1 - Testar endpoints de API | 30min |
| 🟡 Média | 3.1 - Atualizar scripts de seed | 1h |
| 🟡 Média | 5.1 - Validar integridade dos dados | 30min |
| 🟢 Baixa | 4.1 - Criar migration Alembic | 1h |
| 🟢 Baixa | 6.1 - Atualizar documentação | 1h |

## Checklist

- [ ] Atualizar imports em 17 arquivos críticos
- [ ] Substituir `EntityType` por `StructType` + `LogicalEntityType`
- [ ] Testar endpoints `/api/metadata/*`
- [ ] Atualizar scripts de seed
- [ ] Validar 128 entidades no banco
- [ ] Criar migration Alembic
- [ ] Atualizar documentação da API
- [ ] Verificar logs de erro
- [ ] Testar hierarquia de entidades
- [ ] Confirmar performance dos índices
