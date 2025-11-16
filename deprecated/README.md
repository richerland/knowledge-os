# Deprecated Seeds

## Aviso

Os arquivos neste diretório estão **DEPRECATED** (descontinuados) e foram substituídos pelo arquivo consolidado:

**`knowledge_os_all_seeds.json`** (na raiz do projeto)

## Motivo da Descontinuação

Os arquivos individuais de seeds foram consolidados em um único arquivo para:

1. **Eliminar duplicações**: As entidades canônicas estavam repetidas entre `ontology.json` e `snapshot_v1_0.json`
2. **Simplificar carregamento**: Um único arquivo facilita o processo de seed do banco de dados
3. **Manter consistência**: Evita conflitos de versão entre múltiplos arquivos
4. **Melhorar manutenção**: Centraliza todas as entidades em um único local

## Arquivos Descontinuados

| Arquivo | Entidades | Descrição |
|---------|-----------|-----------|
| `knowledge_os_ontology.json` | 9 CANONICAL | Entidades canônicas fundamentais |
| `knowledge_os_snapshot_v1_0.json` | 9 CANONICAL + 4 CLASS | Snapshot com base + classes básicas |
| `knowledge_os_seeds_operational_v1_0.json` | 4 CLASS | Classes operacionais |
| `event_ontology.json` | 15 CLASS | Frames de eventos |
| `knowledge_os_document_taxonomy_seeds.json` | 97 CLASS | Taxonomia de documentos (3 níveis) |

**Total**: 138 entidades (com duplicações)

## Arquivo Consolidado

**`knowledge_os_all_seeds.json`** contém:
- **128 entidades únicas** (sem duplicações)
- 9 CANONICAL
- 119 CLASS

## Uso Recomendado

### ❌ NÃO USE (deprecated):
```python
seed_from_path(session, "deprecated/knowledge_os_ontology.json")
seed_from_path(session, "deprecated/knowledge_os_snapshot_v1_0.json")
# ... etc
```

### ✅ USE (recomendado):
```python
seed_from_path(session, "knowledge_os_all_seeds.json")
```

## Histórico

- **2024-11-16**: Arquivos movidos para `deprecated/` e substituídos por `knowledge_os_all_seeds.json`
- **2024-11-15**: Criação dos arquivos individuais de seeds

## Manutenção Futura

Estes arquivos são mantidos apenas para referência histórica. Todas as atualizações devem ser feitas em:

**`knowledge_os_all_seeds.json`**

---

**Nota**: Se você precisa dos arquivos individuais por algum motivo específico, eles ainda estão disponíveis neste diretório, mas não são mais mantidos ativamente.
