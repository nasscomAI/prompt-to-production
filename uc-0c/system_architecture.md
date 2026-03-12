# System Architecture — Citizen Complaint Classification Platform

> High-level architecture for a production-ready, AI-driven city complaint management system.

---

## 1. Data Pipeline

### End-to-End Processing Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DATA PIPELINE                                      │
│                                                                              │
│  ┌──────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐  │
│  │  INGEST   │───▶│ VALIDATE │───▶│ CLASSIFY │───▶│ PRIORITISE│───▶│ ROUTE  │  │
│  │           │    │          │    │          │    │          │    │        │  │
│  │ CSV/API/  │    │ Schema   │    │ NLP +    │    │ Rules +  │    │ Dept   │  │
│  │ Email     │    │ Check    │    │ Keywords │    │ Scoring  │    │ Map    │  │
│  └──────────┘    └─────────┘    └──────────┘    └──────────┘    └───┬────┘  │
│                                                                      │       │
│                                                              ┌───────▼─────┐ │
│                                                              │   REPORT    │ │
│                                                              │ Analytics + │ │
│                                                              │ Export      │ │
│                                                              └─────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

| Stage | Input | Processing | Output | Latency Target |
|---|---|---|---|---|
| **Ingest** | CSV files, API payloads, emails | File parsing, format normalisation | Structured JSON records | < 2s per file |
| **Validate** | JSON records | Schema validation, null detection, dedup | Valid records + rejection report | < 100ms per record |
| **Classify** | Valid records | NLP tokenisation, keyword matching, category assignment | Categorised records with confidence | < 500ms per record |
| **Prioritise** | Categorised records | Keyword trigger scan, SLA check, urgency scoring | Prioritised records (URGENT/HIGH/MEDIUM/LOW) | < 200ms per record |
| **Route** | Prioritised records | Department lookup, cross-dept check, escalation | Routed records with department assignment | < 100ms per record |
| **Report** | All processed records | Aggregation, analytics, charting | CSV/JSON/Markdown reports | < 5s for full dataset |

### Data Sources

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT SOURCES                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📁 CSV Files          → city-test-files/*.csv          │
│  🌐 REST API           → POST /api/complaints          │
│  📧 Email Parser       → complaints@city.gov.in        │
│  📱 WhatsApp / SMS     → Twilio / MSG91 gateway        │
│  🖥️ Citizen Portal     → Web form submissions          │
│  📞 Phone Helpline     → IVR transcription              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Agent Interaction

### Agent Communication Flow

```
                    ┌─────────────────────────┐
                    │     Orchestrator         │
                    │  (Pipeline Controller)   │
                    └────┬──────────────┬──────┘
                         │              │
            ┌────────────▼──┐    ┌──────▼────────────┐
            │ Data Ingestion │    │  Config Manager   │
            │    Agent       │    │  (Rules, Taxonomy)│
            └───────┬────────┘    └──────────────────┘
                    │
         Validated Records
                    │
            ┌───────▼────────┐
            │   Complaint    │◄─── Skills: text_classification,
            │ Understanding  │     keyword_extraction,
            │    Agent       │     named_entity_recognition
            └───────┬────────┘
                    │
        Classified Records
                    │
            ┌───────▼────────┐
            │   Priority     │◄─── Skills: urgency_detection
            │  Detection     │
            │    Agent       │
            └───────┬────────┘
                    │
       Prioritised Records
                    │
            ┌───────▼────────┐
            │  Department    │◄─── Skills: department_mapping
            │   Routing      │
            │    Agent       │
            └───────┬────────┘
                    │
         Routed Records
                    │
            ┌───────▼────────┐
            │   Reporting    │◄─── Skills: data_validation
            │    Agent       │
            └───────┬────────┘
                    │
           ┌────────┼────────┐
           ▼        ▼        ▼
        CSV      JSON    Dashboard
       Export    Export    (Live)
```

### Inter-Agent Protocol

| From | To | Message Type | Payload |
|---|---|---|---|
| Orchestrator | Data Ingestion | `INGEST_REQUEST` | `{directory: "city-test-files/"}` |
| Data Ingestion | Complaint Understanding | `RECORDS_READY` | `{records: [...], quality_report: {...}}` |
| Complaint Understanding | Priority Detection | `CLASSIFIED` | `{records: [...with category, keywords...]}` |
| Priority Detection | Dept. Routing | `PRIORITISED` | `{records: [...with priority, score...]}` |
| Dept. Routing | Reporting | `ROUTED` | `{records: [...with department...]}` |
| Any Agent | Orchestrator | `ERROR` | `{agent: "...", error: "...", record_id: "..."}` |

---

## 3. ML Components

### Current Architecture (Rule-Based + ML Hybrid)

```
┌──────────────────────────────────────────────────────────────┐
│                    ML COMPONENT STACK                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Rule Engine (Primary — always runs)                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • Keyword trigger matching                            │  │
│  │  • Regex pattern extraction                            │  │
│  │  • Department lookup tables                            │  │
│  │  • SLA threshold calculator                            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  Layer 2: Classical ML (Secondary — for classification)      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • TF-IDF Vectoriser → feature extraction              │  │
│  │  • Logistic Regression → category prediction           │  │
│  │  • XGBoost → priority prediction (multi-factor)        │  │
│  │  • RAKE → keyword extraction                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  Layer 3: Deep Learning (Planned — for complex NLP)          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • BERT / DistilBERT → intent classification           │  │
│  │  • Sentence Transformers → semantic similarity          │  │
│  │  • spaCy NER → entity extraction                       │  │
│  │  • LLM (Gemini/GPT) → zero-shot fallback               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Model Selection Strategy

| Task | Model | Training Data | Accuracy | Latency |
|---|---|---|---|---|
| Category Classification | TF-IDF + Logistic Regression | Labelled complaints | >85% | <50ms |
| Category Classification | Fine-tuned DistilBERT | Labelled complaints | >92% | <200ms |
| Priority Prediction | XGBoost (multi-factor) | Complaints + outcomes | >88% | <30ms |
| Intent Detection | Sentence Transformers | Intent-labelled data | >90% | <150ms |
| NER | spaCy custom pipeline | City-annotated text | >85% | <100ms |
| Fallback Classification | LLM zero-shot (Gemini) | None (zero-shot) | ~80% | <2s |

### ML Training Pipeline

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  Collect   │───▶│  Label    │───▶│  Feature  │───▶│  Train    │───▶│  Deploy   │
│  Data      │    │  Data     │    │  Engineer │    │  Model    │    │  Model    │
│            │    │           │    │           │    │           │    │           │
│ Historical │    │ Human     │    │ TF-IDF,   │    │ Cross-val │    │ REST API  │
│ complaints │    │ annotators│    │ embeddings│    │ + tune    │    │ + monitor │
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
                                                         │
                                                         ▼
                                                   ┌───────────┐
                                                   │  Model    │
                                                   │  Registry │
                                                   │ (MLflow)  │
                                                   └───────────┘
```

---

## 4. Deployment Concept

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT ARCHITECTURE                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    LOAD BALANCER (Nginx)                     │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │                  API GATEWAY (FastAPI)                       │    │
│  │  • POST /api/complaints      → Ingest new complaint         │    │
│  │  • GET  /api/complaints/{id} → Get classification result    │    │
│  │  • GET  /api/reports         → Get analytics reports        │    │
│  │  • GET  /api/health          → Service health check         │    │
│  └──────────────┬──────────────────────────────┬───────────────┘    │
│                 │                              │                    │
│  ┌──────────────▼──────────┐    ┌──────────────▼──────────────┐    │
│  │   Agent Pipeline        │    │   ML Inference Service       │    │
│  │   (Docker Container)    │    │   (Docker Container)         │    │
│  │                         │    │                              │    │
│  │  • Data Ingestion       │    │  • TF-IDF model              │    │
│  │  • Complaint Analysis   │    │  • BERT model                │    │
│  │  • Priority Detection   │    │  • XGBoost model             │    │
│  │  • Dept. Routing        │    │  • spaCy NER pipeline        │    │
│  │  • Reporting            │    │                              │    │
│  └──────────────┬──────────┘    └──────────────────────────────┘    │
│                 │                                                    │
│  ┌──────────────▼──────────────────────────────────────────────┐    │
│  │                    DATA LAYER                                │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐     │    │
│  │  │ PostgreSQL   │  │ Redis Cache  │  │ S3 / MinIO     │     │    │
│  │  │ (complaints  │  │ (session,    │  │ (CSV uploads,  │     │    │
│  │  │  + results)  │  │  rate limit) │  │  model files)  │     │    │
│  │  └─────────────┘  └──────────────┘  └────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI (Python) | REST API for complaint intake and results |
| **Agent Runtime** | Python 3.9+ | Agent pipeline execution |
| **ML Framework** | scikit-learn, PyTorch, spaCy | Model training and inference |
| **Database** | PostgreSQL | Complaint storage, classification results |
| **Cache** | Redis | Session management, rate limiting, hot data |
| **Object Store** | S3 / MinIO | CSV uploads, model artifacts |
| **Model Registry** | MLflow | Model versioning, experiment tracking |
| **Containerisation** | Docker | Agent and ML service packaging |
| **Orchestration** | Kubernetes (K8s) | Horizontal scaling, service discovery |
| **Monitoring** | Prometheus + Grafana | System metrics, model performance |
| **CI/CD** | GitHub Actions | Automated testing, model deployment |
| **Dashboard** | Streamlit / Power BI | Officer analytics interface |

### Scaling Strategy

| Load Level | Infrastructure | Capacity |
|---|---|---|
| **Pilot** (1 city) | Single server, 4 CPU, 16GB RAM | ~1,000 complaints/day |
| **Regional** (5 cities) | 3-node K8s cluster | ~10,000 complaints/day |
| **State-wide** (50+ cities) | Multi-zone K8s, auto-scaling | ~100,000 complaints/day |
| **National** | Multi-region, CDN, read replicas | ~1,000,000 complaints/day |

---

## 5. Optional Advanced Features

### 5.1 Machine Learning Enhancements

| Enhancement | Description | Expected Impact |
|---|---|---|
| **Fine-tuned BERT** | Train BERT on 10,000+ labelled city complaints | +7% classification accuracy |
| **Multi-label classification** | Allow complaints to belong to multiple categories | Better handling of complex complaints |
| **Active learning** | Human-in-the-loop labelling for low-confidence cases | Continuous model improvement |
| **Sentiment analysis** | Detect citizen frustration level from text | Better priority assessment |

### 5.2 Neural Networks for Text Understanding

| Model | Use Case | Architecture |
|---|---|---|
| **BiLSTM + Attention** | Complaint intent classification | Embedding → BiLSTM → Attention → Softmax |
| **CNN-TextClassifier** | Fast category prediction | Embedding → Conv1D → MaxPool → Dense |
| **Transformer (DistilBERT)** | Multi-task: category + priority + intent | Pre-trained → Fine-tuned heads |

### 5.3 CI/CD Pipeline for Model Updates

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Code    │───▶│  Test    │───▶│  Train   │───▶│  Validate│───▶│  Deploy  │
│  Push    │    │  Suite   │    │  Model   │    │  Model   │    │  to Prod │
│          │    │          │    │          │    │          │    │          │
│ Git Push │    │ pytest   │    │ New data │    │ Accuracy │    │ Blue/    │
│ to main  │    │ + lint   │    │ + retrain│    │ > 90%?   │    │ Green    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
                                              ┌──────▼──────┐
                                              │  FAIL?      │
                                              │  → Rollback │
                                              │  → Alert    │
                                              └─────────────┘
```

### 5.4 Dashboard Integration

| Dashboard | Audience | Features |
|---|---|---|
| **Citizen Portal** | Citizens | Submit complaints, track status, view resolution updates |
| **Officer Dashboard** | City officials | Queue management, SLA monitor, complaint details |
| **Commissioner View** | Senior leadership | City-wide analytics, heatmaps, department performance |
| **GIS Map View** | All users | Geospatial complaint hotspots, cluster analysis |

### 5.5 Real-Time Monitoring

```
┌────────────────────────────────────────────────────────┐
│              MONITORING STACK                           │
│                                                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ │
│  │ Prometheus   │   │  Grafana    │   │  PagerDuty  │ │
│  │              │   │             │   │             │ │
│  │ • API latency│   │ • Live      │   │ • SLA breach│ │
│  │ • Queue depth│   │   dashboards│   │   alerts    │ │
│  │ • Model acc. │   │ • Trend     │   │ • System    │ │
│  │ • Error rate │   │   charts    │   │   downtime  │ │
│  └─────────────┘   └─────────────┘   └─────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key Metrics Monitored:**
- Classification accuracy (real-time vs human audit)
- Average complaint processing latency
- SLA compliance rate per department
- URGENT complaint response time
- Model drift detection (accuracy degradation over time)
- System uptime and error rates

---

## 6. Security & Compliance

| Requirement | Implementation |
|---|---|
| **Data Encryption** | AES-256 at rest, TLS 1.3 in transit |
| **Access Control** | RBAC with department-level permissions |
| **Audit Logging** | Every classification decision logged with timestamp |
| **Data Retention** | Complaints retained for 5 years per government policy |
| **PII Protection** | Citizen names/phones masked in analytics dashboards |
| **Compliance** | IT Act 2000, DPDP Act 2023 compliant |
