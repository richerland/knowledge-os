# Knowledge-OS

Sistema de ontologia para representação estruturada de conhecimento baseado em grafos, com suporte a projeção semântica de eventos.

## Visão Geral

O **Knowledge-OS** é um sistema ontológico formal que utiliza dois sistemas independentes de tipagem para representar conhecimento de forma estruturada e matematicamente coerente:

- **Tipagem Estrutural** (`struct_type`): Define a natureza estrutural das entidades
- **Tipagem Lógica** (`entity_type`): Define a categoria semântica das entidades

O sistema suporta tanto grafos ontológicos (meta-nível) quanto grafos instanciados de dados, permitindo representação completa de conhecimento factual sem perda de informação.

## Arquivos do Projeto

### Ontologias Core

- **`knowledge_os_ontology.json`** - Especificação formal núcleo (fonte de verdade)
  - Entidades canônicas fundamentais
  - Relações básicas do sistema
  - Axiomas formais da ontologia

- **`knowledge_os_snapshot_v1_0.json`** - Snapshot v1.0 enriquecido
  - Entidades canônicas + classes de domínio básicas
  - Classes de documentos (Reference Letter, Petition Letter)
  - Classes de papéis (Beneficiary, Attorney of Record)

### Ontologias Especializadas

- **`event_ontology.json`** - Ontologia de Projeção Semântica de Eventos
  - 15 frames de eventos especializados
  - Papéis semânticos estruturados (N1 e N2)
  - Preservação factual completa

- **`knowledge_os_seeds_operational_v1_0.json`** - Seeds operacionais
  - Classes operacionais para fluxos de imigração
  - Documentos especializados (Expert Letter, Support Letter)
  - Papéis de caso (Beneficiary, Petitioner)

### Representações Alternativas

- **`knowledge_os_ontology.owl`** - Espelho OWL (formato Turtle)
  - Representação em OWL 2 da ontologia core
  - Compatível com reasoners padrão

### Código

- **`knowledge_os_loader.py`** - Módulo Python de carregamento
  - Usa SQLAlchemy ORM (Session + Entity)
  - Validação automática de ontologias
  - Suporte a upsert via UniqueConstraint

## Especificação Formal da Ontologia

### 1. Tipagem Estrutural (`struct_type`)

Cada entidade `e` no universo `E` possui um tipo estrutural:

```
struct_type(e) ∈ {CANONICAL, CLASS, RELATION, INSTANCE}
```

**Significado:**

- **CANONICAL**: Um dos nove fundamentos semânticos da ontologia. Representa as bases lógicas do sistema e não possui pai. Entidades canônicas não derivam de nenhum outro tipo.

- **CLASS**: Uma especialização conceitual derivada de exatamente um tipo CANONICAL. Classes são agrupamentos semânticos abstratos (como "Cientista", "Assessor", "Referenciador", "Startup") e não possuem materialidade no nível de instância.

- **INSTANCE**: Uma materialização concreta de uma CLASS. Instâncias herdam seu tipo lógico da CLASS da qual são instância.

- **RELATION**: Uma relação binária primitiva. No nível ontológico, RELATION é um vértice no meta-grafo, com propriedades definíveis (nome, domínio, alcance, restrições). No nível de dados, RELATION torna-se rótulo de aresta entre nós INSTANCE.

### 2. Tipagem Lógica (`entity_type`)

O tipo lógico de uma entidade provém do conjunto:

```
L = {PERSON, ORGANIZATION, PLACE, TIME, VALUE, DOCUMENT, EVENT, ROLE, UNKNOWN}
```

A função:

```
entity_type : E → L ∪ {∅}
```

é restringida por:

- Se `struct_type(e) = CANONICAL`: `entity_type(e) = e`
- Se `struct_type(e) = CLASS`: `entity_type(e) ∈ L`
- Se `struct_type(e) = INSTANCE`: `entity_type(e) = entity_type(parent_class(e))`
- Se `struct_type(e) = RELATION`: `entity_type(e) = ∅`

### 3. Relações e Restrições de Tipagem

Uma RELATION `r` define uma relação binária tipada:

```
r ⊆ INSTANCE × INSTANCE
```

com assinatura:

```
dom(r) ∈ L
rng(r) ∈ L
```

e restrição:

```
(s, r, o) ∈ r  ⇒  entity_type(s) = dom(r) ∧ entity_type(o) = rng(r)
```

### 4. Semântica de Dois Grafos

A ontologia possui dois níveis:

- **Grafo Ontológico (Metamodelo)**:
  - Entidades CANONICAL, CLASS, RELATION, INSTANCE são vértices
  - RELATION é vértice e pode participar de arestas de ordem superior

- **Grafo de Dados (Instâncias)**:
  - Apenas INSTANCE são vértices
  - RELATION atua como rótulo de aresta INSTANCE → INSTANCE
  - CANONICAL e CLASS não aparecem como vértices

**RELATION é simultaneamente:**
- vértice no meta-grafo
- rótulo de aresta no grafo instanciado

### 5. Axiomas Centrais

1. `struct_type(e)` está definido para todo `e ∈ E`
2. `entity_type(e)` é definido para todos os não-RELATION
3. CANONICAL são raízes lógicas
4. CLASS deriva de uma raiz CANONICAL
5. INSTANCE materializa uma CLASS
6. RELATION define arestas binárias tipadas
7. RELATION pode ser vértice no meta-grafo para permitir metarrazão

### Versão Minimalista (10 linhas)

```
E = universo; L = {PERSON, ORGANIZATION, PLACE, TIME, VALUE, DOCUMENT, EVENT, ROLE, UNKNOWN}
struct_type: E → {CANONICAL, CLASS, RELATION, INSTANCE}
entity_type: E → L ∪ {∅}
struct_type(e)=CANONICAL ↔ (e∈L ∧ entity_type(e)=e)
struct_type(e)=CLASS → entity_type(e)∈L
struct_type(e)=INSTANCE → entity_type(e)=entity_type(parent(e))
struct_type(e)=RELATION → entity_type(e)=∅
r∈RELATION → r ⊆ INSTANCE×INSTANCE
(s,r,o)∈r → entity_type(s)=dom(r) ∧ entity_type(o)=rng(r)
RELATION é vértice no meta-grafo e aresta no grafo de instâncias
```

### Versão em Lógica de Primeira Ordem (FOL)

```
Canonical(x)  ↔  struct_type(x,CANONICAL)
Class(x)      ↔  struct_type(x,CLASS)
Relation(x)   ↔  struct_type(x,RELATION)
Instance(x)   ↔  struct_type(x,INSTANCE)

Canonical(x) → entity_type(x,x)
Class(x) → ∃t ∈ L [entity_type(x,t)]
Instance(x) → ∃c [Class(c) ∧ parent(x,c) ∧ entity_type(x)=entity_type(c)]
Relation(r) → entity_type(r)=∅
triple(s,r,o) → entity_type(s)=dom(r) ∧ entity_type(o)=rng(r)
```

### Versão em Teoria das Categorias

**Categoria do Metamodelo O:**
```
Obj(O) = { e ∈ E | struct_type(e)∈{CANONICAL,CLASS,RELATION,INSTANCE} }
Hom(O)(a,b) = { * | parent(b)=a } ∪ { * | dom(a)=b ∨ rng(a)=b }
```

**Categoria dos Dados D:**
```
Obj(D) = { i ∈ E | struct_type(i)=INSTANCE }
Hom(D)(s,o) = { r | struct_type(r)=RELATION ∧ (s,r,o)∈r }
```

**Funtor de Instanciação F: O → D:**
```
F(canonical)=Ø
F(class)=conjunto de suas instâncias
F(instance)=ele próprio
F(relation)=morfismos entre instâncias
```

## Ontologia de Projeção Semântica de Eventos

### Nome e Conceito

**ID técnico**: `knowledge_os_event_projection`

**Descrição**: Ontologia de Projeção Semântica de Eventos

**Conceito central**: "Redução dimensional com preservação semântica via eventos"

A ontologia projeta texto para um espaço de eventos + papéis, mantendo os fatos e reduzindo o ruído textual.

### Frames de Eventos

A ontologia define 15 frames especializados de eventos:

1. **EMPLOYMENT_EVENT** - Relação de emprego ou contratação
2. **PROMOTION_EVENT** - Promoção ou elevação de posição
3. **PROJECT_CONTRIBUTION_EVENT** - Contribuição significativa a projeto
4. **AWARD_EVENT** - Prêmio ou reconhecimento formal
5. **PUBLICATION_EVENT** - Publicação de artigo, livro ou capítulo
6. **PRESENTATION_EVENT** - Palestra, keynote ou apresentação técnica
7. **MEMBERSHIP_EVENT** - Membro de sociedade profissional ou conselho
8. **EDUCATION_EVENT** - Educação formal, grau ou treinamento avançado
9. **PATENT_EVENT** - Registro ou concessão de patente
10. **PETITION_FILING_EVENT** - Registro de petição de imigração (USCIS)
11. **USCIS_DECISION_EVENT** - Decisão do USCIS sobre petição
12. **RFE_EVENT** - Request for Evidence emitido pelo USCIS
13. **RFE_RESPONSE_EVENT** - Resposta a um RFE
14. **REFERENCE_LETTER_EVENT** - Emissão de carta de referência/recomendação
15. **EXPERT_OPINION_EVENT** - Opinião de especialista ou carta consultiva

### Papéis Semânticos

A ontologia define dois níveis de papéis:

**Papéis N1 (Core Roles)**:
- `agent` - Agente/iniciador do evento
- `patient` - Entidade diretamente afetada
- `theme` - Tema/objeto principal
- `instrument` - Instrumento ou meio utilizado
- `result` - Estado ou resultado do evento

**Papéis N2 (Thematic Roles)**:
- `beneficiary` - Pessoa que se beneficia
- `co_agent` - Agente adicional
- `topic` - Tópico ou assunto
- `medium` - Meio ou canal usado
- `affiliation` - Organização afiliada
- `role` - Papel abstrato desempenhado
- `measure` - Métrica quantitativa
- `purpose` - Propósito ou objetivo
- `cause` - Causa ou razão
- `manner` - Maneira de execução

### Frame-Specific Roles

Cada frame de evento define mapeamentos específicos de papéis para seu domínio. Por exemplo, no `EMPLOYMENT_EVENT`:

```json
"frame_specific_roles": {
  "employer": "agent",
  "employee": "patient",
  "position_title": "role",
  "employment_type": "condition",
  "employment_start_date": "time",
  "employment_end_date": "time",
  "team_size": "measure",
  "reports_to": "co_agent",
  "department": "affiliation"
}
```

### Integração com o Sistema

A ontologia de eventos complementa as ontologias core:

- **`knowledge_os_ontology.json`** - Núcleo (CANONICAL_EVENT, relações básicas)
- **`event_ontology.json`** - Adiciona classes de eventos (FRAME_*_EVENT) e relações de papel semântico
- **`knowledge_os_snapshot_v1_0.json`** - Mistura core + classes de documentos/roles de domínio
- **`knowledge_os_seeds_operational_v1_0.json`** - Classes operacionais específicas

## Uso do Loader

```python
from knowledge_os_loader import seed_from_path

# Core
seed_from_path(session, "knowledge_os_ontology.json")

# Snapshot
seed_from_path(session, "knowledge_os_snapshot_v1_0.json")

# Event projection
seed_from_path(session, "event_ontology.json")

# Operational seeds
seed_from_path(session, "knowledge_os_seeds_operational_v1_0.json")
```

## Distinção Fundamental: Identificação vs Redução Semântica

### Categoria do Modelo

✔ **IDENTIFICAÇÃO SEMÂNTICA ESTRUTURADA**
(Semantic Event Identification / Information Extraction)

✘ **NÃO é REDUÇÃO SEMÂNTICA**
(Summarization / Semantic Compression / Abstraction)

### Diferença Conceitual

**A) REDUÇÃO/COMPACTAÇÃO**

→ Objetivo: diminuir o texto mantendo o "sentido essencial"

→ Operações típicas:
- Reduzir redundância
- Comprimir informação
- Eliminar estilo
- Unificar eventos
- Recuperar proposições mínimas

Exemplos: summarization, AMR-to-text simplificado, semantic compression, distil meaning, abstractive summarization

**B) EXTRAÇÃO/IDENTIFICAÇÃO**

→ Objetivo: preservar 100% dos fatos, apenas mudando a forma de representá-los

→ Operações típicas:
- Identificar eventos
- Identificar participantes
- Identificar papéis
- Identificar atributos
- Anotar (não condensar)
- Normalizar papéis (não textos)

Exemplos: SRL, FrameNet parsing, Neo-Davidsonian event extraction, RDF triple extraction, structured IE

💡 **O Knowledge-OS pertence exclusivamente ao segundo grupo.**

### Distinção Operacional

**Em tarefas de REDUÇÃO:**
- Entrada: 30 páginas
- Saída: 1–3 páginas (ou 20–30 proposições)
- Perde detalhes? → **Sim, por definição**

**Em tarefas de EXTRAÇÃO/IDENTIFICAÇÃO (Knowledge-OS):**
- Entrada: 30 páginas
- Saída:
  - 150–500 eventos
  - 1000–3000 relações
  - 500–1200 entidades instanciadas
  - **NENHUM fato perdido**
- Perde detalhes? → **Nunca**

É representação estrutural, não compressão.

### Distinção Matemática

**Redução (Semantic Compression)**

Um operador:

```
C(T) = T' com |T'| < |T|
```

E uma condição de preservação fraca:

```
Meaning(T') ≈ Meaning(T)
```

Ou seja: compacta mantendo essência.

**Extração/Identificação (Event Semantics Extraction)**

Um operador:

```
E(T) = {e₁, e₂, …, eₙ}
```

onde cada:

```
eᵢ = ⟨frame, roles⟩
```

E a propriedade principal:

```
∀f ∈ Facts(T), f ∈ ⋃Roles(eᵢ)
```

Ou seja: **NENHUM fato do texto é perdido**. Cada fato vira um evento + papéis.

💡 **Matematicamente, a função é expansiva, não compressiva.**

### Definição Final e Rigorosa

**Redução Semântica (Semantic Compression)**

Operação que transforma um texto T em uma forma T′ com menor volume, mantendo similaridade semântica global, mas não necessariamente preservando todos os fatos.

**Extração/Identificação Semântica (Semantic Event Identification)**

Operação que transforma um texto T em um conjunto estruturado de eventos e papéis E(T), preservando integralmente todos os fatos explícitos e implícitos factuais do texto, sem reduzir ou condensar o conteúdo.

### Frase Síntese

> "Nosso modelo não é um modelo de compressão semântica. Ele é um modelo de identificação estrutural: converte cada fato do texto em sua representação formal mínima, mantendo 100% da granularidade factual."

## Aplicações

O sistema é especialmente adequado para:

- ✔ Precisão factual absoluta
- ✔ Auditabilidade legal
- ✔ Rastreabilidade
- ✔ Consistência entre documentos
- ✔ Integridade probatória
- ✔ Granularidade máxima

Isso só existe no paradigma de **IE → Identificação Estruturada de Eventos**, e não no paradigma de compressão.

## Versão

**Knowledge-OS Core**: v1.0.0

**Event Projection Ontology**: v1.0.0

## Licença

[Especificar licença]
