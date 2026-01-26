# Architecture Comparison: Cloud Platform Options

> Idea ID: IDEA-011
> Document: Architecture Comparison
> Version: v1
> Created: 2026-01-25
> Status: Draft

## Overview

This document compares cloud platform options for the AI-Integrated Enterprise Knowledge Base, mapping the original multi-cloud architecture to Alibaba Cloud equivalents for China-based development.

## Deployment Context

| Aspect | Decision |
|--------|----------|
| **Primary Cloud** | Alibaba Cloud (China region) |
| **Office Suite** | Microsoft 365 (retained) |
| **Identity Provider** | Azure AD (retained) |
| **Development Center** | China |

---

## Component-by-Component Comparison

### 1. AI/ML Services

#### LLM Provider

| Aspect | Original Options | Alibaba Cloud Option |
|--------|------------------|---------------------|
| **Service** | Azure OpenAI, Anthropic Claude | Tongyi Qianwen (Qwen) via Model Studio |
| **Models** | GPT-4, Claude 3.5 | Qwen 2.5, Qwen 3, Qwen-Max |
| **API Compatibility** | OpenAI API | OpenAI-compatible + DashScope native |
| **Language Support** | Strong English | 119+ languages, excellent Chinese |
| **Latency (China)** | High (cross-border) | Low (local) |
| **Data Residency** | International | China-compliant |
| **Cost** | $$ - $$$ | $ - $$ |

**Recommendation**: ✅ **Qwen via Model Studio** - Native China support, lower latency, OpenAI API compatibility enables easy migration.

#### Embedding Service

| Aspect | Original Options | Alibaba Cloud Option |
|--------|------------------|---------------------|
| **Service** | OpenAI ada-002, Cohere Embed | gte-Qwen2 via DashScope |
| **Model** | text-embedding-ada-002 | gte-Qwen2-7B-instruct |
| **Dimensions** | 1536 | 1024-4096 (configurable) |
| **Benchmark** | Strong MTEB scores | #1 on MTEB (Chinese), Top-5 (English) |
| **Languages** | English-focused | Multilingual (Chinese/English optimized) |

**Recommendation**: ✅ **gte-Qwen2** - Superior performance for Chinese content, competitive for English.

#### Reranker

| Aspect | Original Options | Alibaba Cloud Option |
|--------|------------------|---------------------|
| **Service** | Cohere Rerank, BGE Reranker | gte-rerank via DashScope |
| **Integration** | API-based | Native DashScope integration |
| **Performance** | Industry standard | Optimized for Qwen ecosystem |

**Recommendation**: ✅ **gte-rerank** - Native integration with Qwen embeddings, optimized RAG pipeline.

---

### 2. Vector Database

| Aspect | Original Options | Alibaba Cloud Options |
|--------|------------------|----------------------|
| **Managed Service** | Pinecone, Weaviate Cloud | AnalyticDB for PostgreSQL |
| **Self-hosted** | Milvus, Qdrant | Milvus on PAI/ECS |
| **Hybrid Capability** | Limited | SQL + Vector in one DB |
| **Scale** | Billion vectors | Billion vectors (MPP) |
| **Index Types** | HNSW, IVF | FastANN (HNSW, IVF, Flat) |

#### Detailed Comparison

| Feature | Pinecone | Milvus | AnalyticDB-PG |
|---------|----------|--------|---------------|
| **Managed** | ✅ Full SaaS | ❌ Self-host (or Zilliz) | ✅ Alibaba managed |
| **SQL Support** | ❌ | ❌ | ✅ Full PostgreSQL |
| **Hybrid Search** | Limited | Yes | ✅ Native SQL+Vector |
| **China Availability** | ❌ | ✅ (self-host) | ✅ Native |
| **Cost Model** | Per-vector | Infrastructure | Query-based |
| **ACID** | ❌ | ❌ | ✅ |

**Recommendation**: ✅ **AnalyticDB for PostgreSQL** - Best for hybrid workloads combining metadata queries with vector search. Consider **Milvus on PAI** for pure vector workloads at extreme scale.

---

### 3. Document Storage

| Aspect | Azure Blob | AWS S3 | Alibaba Cloud OSS |
|--------|------------|--------|-------------------|
| **Durability** | 99.999999999% | 99.999999999% | 99.9999999999% |
| **Availability SLA** | 99.99% | 99.99% | 99.95%-99.995% |
| **Storage Classes** | Hot/Cool/Archive | Standard/IA/Glacier | Standard/IA/Archive |
| **CDN Integration** | Azure CDN | CloudFront | Alibaba CDN |
| **China Compliance** | ⚠️ Via 21Vianet | ⚠️ Limited | ✅ Native |
| **Cost (China)** | Higher | Higher | Lower |

**Recommendation**: ✅ **Alibaba Cloud OSS** - Best cost/performance in China, native compliance.

---

### 4. Metadata Database

| Aspect | Azure SQL | AWS RDS | ApsaraDB RDS for PostgreSQL |
|--------|-----------|---------|----------------------------|
| **Engine** | SQL Server/PG | PostgreSQL/MySQL | PostgreSQL |
| **HA Options** | Geo-replication | Multi-AZ | Multi-zone, cross-region |
| **Read Replicas** | Yes | Yes | Yes |
| **China Availability** | Via 21Vianet | Limited | ✅ Native |

**Recommendation**: ✅ **ApsaraDB RDS for PostgreSQL** - Native support, familiar PostgreSQL interface.

---

### 5. Graph Database

| Aspect | Neo4j | Amazon Neptune | Alibaba Cloud GDB |
|--------|-------|----------------|-------------------|
| **Query Language** | Cypher | Gremlin/SPARQL | Gremlin |
| **Managed** | Marketplace | ✅ Full | ✅ Full |
| **Scale** | Limited (single) | High | High |
| **China Native** | ❌ | ❌ | ✅ |

#### Alternative Options

| Alternative | Strength | When to Use |
|------------|----------|-------------|
| **NebulaGraph** | Massive scale, distributed | Trillions of edges |
| **Memgraph** | Neo4j compatible, fast | Migration from Neo4j |
| **ArangoDB** | Multi-model | Graph + Document needs |

**Recommendation**: ✅ **Alibaba Cloud GDB** for managed simplicity, or **NebulaGraph on ECS** for extreme scale.

---

### 6. Search Engine (Keyword)

| Aspect | Elasticsearch | OpenSearch | Alibaba Cloud ES |
|--------|---------------|------------|------------------|
| **License** | SSPL/Elastic | Apache 2.0 | Managed ES |
| **Features** | Full enterprise | Core + ML | Full enterprise |
| **China Support** | Via marketplace | Self-host | ✅ Native |

**Recommendation**: ✅ **Alibaba Cloud Elasticsearch** - Managed service with full feature set.

---

### 7. API Gateway

| Aspect | Azure APIM | Kong | Alibaba Cloud API Gateway |
|--------|------------|------|---------------------------|
| **Managed** | ✅ Full | Hybrid | ✅ Full |
| **Auth Methods** | Azure AD native | Plugin-based | OIDC/OAuth2/JWT |
| **Rate Limiting** | ✅ | ✅ | ✅ |
| **Analytics** | Azure Monitor | Prometheus | Cloud Monitor |
| **Cost** | $$$ | $$ | $ |

**Recommendation**: ✅ **Alibaba Cloud API Gateway** - Cost-effective, supports Azure AD via OIDC.

---

### 8. ETL/Data Integration

| Aspect | Airbyte | Fivetran | Alibaba DataWorks |
|--------|---------|----------|-------------------|
| **License** | Open Source | SaaS | Managed |
| **Connectors** | 600+ | 700+ | 100+ (China focus) |
| **Custom Connectors** | Easy (CDK) | Limited | Moderate |
| **Orchestration** | Basic | Basic | ✅ Advanced |
| **Data Governance** | ❌ | ❌ | ✅ Built-in |
| **China Sources** | Limited | Limited | ✅ Native |

**Recommendation**: ✅ **DataWorks** for Alibaba-native sources, **Airbyte (self-hosted)** for international connectors (Confluence, SharePoint).

---

### 9. Message Queue / Event Streaming

| Aspect | Azure Event Hub | AWS Kinesis | Alibaba MQ for Kafka |
|--------|-----------------|-------------|---------------------|
| **Protocol** | AMQP/Kafka | Kinesis API | Apache Kafka |
| **Throughput** | High | High | High |
| **Partitions** | 32 default | Shards | Unlimited |
| **Retention** | 7 days | 7 days | Configurable |

**Recommendation**: ✅ **Message Queue for Apache Kafka** - Standard Kafka API, easy migration.

---

### 10. Monitoring & Observability

| Aspect | Azure Monitor | AWS CloudWatch | Alibaba Cloud Monitor + ARMS |
|--------|---------------|----------------|------------------------------|
| **Metrics** | ✅ | ✅ | ✅ |
| **Logs** | Log Analytics | CloudWatch Logs | SLS (Log Service) |
| **APM** | App Insights | X-Ray | ARMS |
| **Dashboards** | ✅ | ✅ | ✅ |

**Recommendation**: ✅ **Cloud Monitor + ARMS + SLS** - Comprehensive observability stack.

---

## Cost Comparison (Estimated Monthly)

| Component | Azure/AWS | Alibaba Cloud | Savings |
|-----------|-----------|---------------|---------|
| **LLM API (1M tokens/day)** | $3,000 | $1,500 | 50% |
| **Vector DB (10M vectors)** | $500 | $300 | 40% |
| **Object Storage (1TB)** | $25 | $15 | 40% |
| **Compute (4 nodes)** | $800 | $500 | 38% |
| **Total Estimate** | ~$4,325 | ~$2,315 | **46%** |

*Note: Estimates based on China region pricing. Actual costs vary by usage.*

---

## Migration Complexity

| Component | Complexity | Notes |
|-----------|------------|-------|
| **LLM Integration** | Low | Qwen supports OpenAI-compatible API |
| **Embeddings** | Low | Same vector dimensions available |
| **Vector DB** | Medium | Schema migration, index rebuilding |
| **ETL Pipelines** | Medium | DataWorks has different paradigm |
| **Auth (Azure AD)** | Low | OIDC/OAuth2 standard |
| **MS Graph Connectors** | Low | API calls work globally |

---

## Recommendation Summary

### Primary Stack (Alibaba Cloud)

| Layer | Service | Confidence |
|-------|---------|------------|
| **LLM** | Qwen via Model Studio | ⭐⭐⭐⭐⭐ |
| **Embeddings** | gte-Qwen2 via DashScope | ⭐⭐⭐⭐⭐ |
| **Reranker** | gte-rerank via DashScope | ⭐⭐⭐⭐ |
| **Vector DB** | AnalyticDB for PostgreSQL | ⭐⭐⭐⭐⭐ |
| **Document Store** | OSS | ⭐⭐⭐⭐⭐ |
| **Metadata DB** | ApsaraDB RDS PostgreSQL | ⭐⭐⭐⭐⭐ |
| **Graph DB** | GDB or NebulaGraph | ⭐⭐⭐⭐ |
| **Search** | Elasticsearch | ⭐⭐⭐⭐⭐ |
| **API Gateway** | API Gateway | ⭐⭐⭐⭐ |
| **ETL** | DataWorks + Airbyte | ⭐⭐⭐⭐ |
| **Message Queue** | MQ for Kafka | ⭐⭐⭐⭐⭐ |
| **Monitoring** | Cloud Monitor + ARMS | ⭐⭐⭐⭐ |

### Retained Microsoft Services

| Service | Purpose |
|---------|---------|
| **Azure AD** | SSO, identity management |
| **Microsoft 365** | Office productivity |
| **MS Graph API** | SharePoint/OneDrive/Email connectors |

---

## References

- [Alibaba Cloud RAG Solutions](https://www.alibabacloud.com/en/solutions/generative-ai/rag)
- [Qwen Model Studio](https://www.alibabacloud.com/en/solutions/generative-ai/qwen)
- [AnalyticDB Vector Analysis](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/vector-analysis/)
- [DashScope API Reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-reference)
