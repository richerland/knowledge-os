# Análise da Organização dos Seeds - Knowledge-OS

## Resumo Executivo

O projeto **knowledge-os** possui **5 arquivos de seeds** organizados hierarquicamente, totalizando **128 entidades únicas** (9 CANONICAL + 119 CLASS).

## Arquivos de Seeds

### 1. knowledge_os_ontology.json (NÚCLEO)

**Ontology ID**: `knowledge_os_core`

**Versão**: 1.0.0

**Propósito**: Fonte de verdade - entidades canônicas fundamentais

**Conteúdo**: 9 entidades CANONICAL

- PERSON
- ORGANIZATION
- PLACE
- TIME
- VALUE
- DOCUMENT
- EVENT
- ROLE
- UNKNOWN

**Status**: NÚCLEO - deve ser carregado primeiro

**Repetições**: As 9 entidades canônicas aparecem também no `snapshot_v1_0.json` (intencional)

---

### 2. knowledge_os_snapshot_v1_0.json (BASE + CLASSES BÁSICAS)

**Ontology ID**: `knowledge_os_snapshot`

**Versão**: 1.0.0

**Propósito**: Snapshot enriquecido v1.0

**Conteúdo**: 13 entidades (9 CANONICAL + 4 CLASS)

**Entidades CANONICAL** (repetidas do ontology.json):
- PERSON, ORGANIZATION, PLACE, TIME, VALUE, DOCUMENT, EVENT, ROLE, UNKNOWN

**Entidades CLASS** (novas):
- Reference Letter
- Petition Letter
- Beneficiary
- Attorney of Record

**Status**: COMPLEMENTAR - adiciona classes de domínio básicas

**Repetições**: 
- 9 canônicos (intencional - snapshot inclui a base)
- "Beneficiary" (duplicado em `operational_seeds.json`)

---

### 3. knowledge_os_seeds_operational_v1_0.json (OPERACIONAL)

**Ontology ID**: `knowledge_os_operational_seeds`

**Versão**: 1.0.0

**Propósito**: Seeds operacionais para fluxos de imigração

**Conteúdo**: 4 entidades CLASS

- Expert Letter
- Support Letter
- Beneficiary
- Petitioner

**Status**: ESPECIALIZADO - classes operacionais

**Repetições**: "Beneficiary" está duplicado no `snapshot_v1_0.json`

---

### 4. event_ontology.json (EVENTOS)

**Ontology ID**: `knowledge_os_event_projection`

**Versão**: 1.0.0

**Propósito**: Ontologia de projeção semântica de eventos

**Conteúdo**: 15 entidades CLASS (frames de eventos)

- EMPLOYMENT_EVENT
- PROMOTION_EVENT
- PROJECT_CONTRIBUTION_EVENT
- AWARD_EVENT
- PUBLICATION_EVENT
- PRESENTATION_EVENT
- MEMBERSHIP_EVENT
- EDUCATION_EVENT
- PATENT_EVENT
- PETITION_FILING_EVENT
- USCIS_DECISION_EVENT
- RFE_EVENT
- RFE_RESPONSE_EVENT
- REFERENCE_LETTER_EVENT
- EXPERT_OPINION_EVENT

**Status**: ESPECIALIZADO - frames de eventos

**Repetições**: Nenhuma

---

### 5. knowledge_os_document_taxonomy_seeds.json (TAXONOMIA)

**Ontology ID**: `knowledge_os_document_taxonomy`

**Versão**: 1.0.0

**Propósito**: Taxonomia hierárquica de documentos em 3 níveis

**Conteúdo**: 97 entidades CLASS

**Estrutura hierárquica**:
- **Nível 1** (superclasses): 4 entidades
  - LETTER_DECLARATION
  - GOV_FORM
  - STRUCTURED_PLAN_OR_REPORT
  - EVIDENCE_PACKET_OR_DOSSIER

- **Nível 2** (famílias funcionais): 38 entidades
  - Exemplos: BANK_FINANCIAL_REFERENCE, BUSINESS_NECESSITY, BUSINESS_PLAN, CLIENT_VENDOR_PARTNER, etc.

- **Nível 3** (templates concretos): 55 entidades
  - Templates específicos vinculados às famílias do Nível 2

**Status**: ESPECIALIZADO - taxonomia completa de documentos

**Repetições**: Nenhuma

---

## Análise de Repetições

### Repetições Intencionais

**9 Entidades CANONICAL** aparecem em:
- `knowledge_os_ontology.json` (fonte de verdade)
- `knowledge_os_snapshot_v1_0.json` (snapshot inclui a base)

**Justificativa**: O snapshot é um arquivo autocontido que inclui tanto as entidades canônicas quanto classes básicas de domínio.

### Repetições Não Intencionais

**1 Entidade CLASS duplicada**:

**"Beneficiary"** aparece em:
- `knowledge_os_snapshot_v1_0.json`
- `knowledge_os_seeds_operational_v1_0.json`

**Recomendação**: Avaliar se a duplicação é necessária ou se deve ser removida de um dos arquivos.

---

## Estatísticas Consolidadas

| Métrica | Valor |
|---------|-------|
| Total de arquivos de seeds | 5 |
| Total de entidades (com repetições) | 138 |
| Total de entidades únicas | 128 |
| Entidades CANONICAL | 9 |
| Entidades CLASS | 119 |
| Repetições intencionais | 9 (canônicos) |
| Repetições não intencionais | 1 (Beneficiary) |

---

## Ordem de Carregamento Recomendada

Para carregar os seeds no banco de dados, recomenda-se a seguinte ordem:

1. **knowledge_os_ontology.json** (núcleo - canônicos)
2. **knowledge_os_snapshot_v1_0.json** (classes básicas) OU carregar apenas as classes (sem canônicos)
3. **knowledge_os_seeds_operational_v1_0.json** (classes operacionais)
4. **event_ontology.json** (frames de eventos)
5. **knowledge_os_document_taxonomy_seeds.json** (taxonomia de documentos)

**Nota**: Se usar `snapshot_v1_0.json`, pular o passo 1 (ontology.json), pois o snapshot já inclui os canônicos.

---

## Organização Conceitual

```
knowledge-os/
│
├── NÚCLEO (9 CANONICAL)
│   └── knowledge_os_ontology.json
│
├── BASE + CLASSES BÁSICAS (9 CANONICAL + 4 CLASS)
│   └── knowledge_os_snapshot_v1_0.json
│
└── ESPECIALIZAÇÕES (119 CLASS)
    ├── Operacional (4 CLASS)
    │   └── knowledge_os_seeds_operational_v1_0.json
    │
    ├── Eventos (15 CLASS)
    │   └── event_ontology.json
    │
    └── Documentos (97 CLASS)
        └── knowledge_os_document_taxonomy_seeds.json
```

---

## Recomendações

### 1. Resolver Duplicação de "Beneficiary"

Decidir se a entidade "Beneficiary" deve estar em:
- Apenas `snapshot_v1_0.json` (classes básicas)
- Apenas `operational_seeds.json` (classes operacionais)
- Ambos (se houver diferença semântica)

### 2. Documentar Estratégia de Carregamento

Criar um script de carregamento que:
- Detecte automaticamente duplicações
- Use upsert via UniqueConstraint
- Registre log de entidades carregadas

### 3. Considerar Arquivo Consolidado

Avaliar a criação de um arquivo consolidado opcional:
- `knowledge_os_all_seeds.json` (todas as 128 entidades únicas)
- Para facilitar carregamento completo em uma única operação

---

## Conclusão

A organização dos seeds está bem estruturada hierarquicamente, com clara separação entre:
- **Núcleo** (canônicos)
- **Base** (classes básicas)
- **Especializações** (operacional, eventos, documentos)

A única questão a resolver é a duplicação da entidade "Beneficiary" entre `snapshot_v1_0.json` e `operational_seeds.json`.
