# Ooumph SHAKTI MVP Development Plan

## Anganwadi Supply Chain Optimization - AI-Powered Ecosystem

***

## Project Overview

### Technology Stack

- **Backend:** Python (FastAPI/Fastify)
- **Frontend:** React + Vite + TypeScript
- **AI/ML:** OpenAI API (GPT-4 for AI agents)
- **Database:** PostgreSQL + Redis (caching)
- **Deployment:** Docker + Docker Compose
- **Testing:** Pytest (backend), Vitest/Jest (frontend)

### Key Constraints

- No government API keys available - use stub/mock services
- OpenAI API for all AI-powered features
- MVP for demo purposes - all core features included
- Maximum 5 development phases

***

## Phase 1: Foundation & Core Infrastructure (Week 1-2)

### Backend Development

#### 1.1 Project Setup

```
/backend
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment & settings
│   ├── database.py             # PostgreSQL connection
│   ├── dependencies.py         # DI container
│   │
│   ├── models/                 # SQLAlchemy/Pydantic models
│   │   ├── user.py
│   │   ├── stakeholder.py
│   │   ├── supply_chain.py
│   │   ├── anganwadi.py
│   │   ├── trust_score.py
│   │   ├── grievance.py
│   │   └── recommendation.py
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── supply.py
│   │   └── agent.py
│   │
│   ├── api/                    # API routes
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── stakeholders.py
│   │   │   ├── supply_chain.py
│   │   │   ├── anganwadi.py
│   │   │   ├── agents/
│   │   │   │   ├── route_intelligence.py
│   │   │   │   ├── supply_sentinel.py
│   │   │   │   ├── demand_forecast.py
│   │   │   │   ├── offline_sync.py
│   │   │   │   ├── grievance.py
│   │   │   │   ├── compliance.py
│   │   │   │   ├── community.py
│   │   │   │   └── integration.py
│   │   │   ├── trust_score.py
│   │   │   └── recommendations.py
│   │   └── __init__.py
│   │
│   ├── services/               # Business logic
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── openai_client.py
│   │   │   ├── base_agent.py
│   │   │   ├── route_intelligence_agent.py
│   │   │   ├── supply_sentinel_agent.py
│   │   │   ├── demand_forecast_agent.py
│   │   │   ├── offline_sync_agent.py
│   │   │   ├── grievance_agent.py
│   │   │   ├── compliance_agent.py
│   │   │   ├── community_agent.py
│   │   │   └── integration_agent.py
│   │   ├── trust_score_service.py
│   │   ├── recommendation_service.py
│   │   └── notification_service.py
│   │
│   ├── stubs/                  # Mock services for govt APIs
│   │   ├── poshan_tracker.py
│   │   ├── icds_cas.py
│   │   ├── rtgs_dashboard.py
│   │   ├── grievance_portal.py
│   │   ├── weather_service.py
│   │   └── road_infrastructure.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── cache.py
│       └── helpers.py
│
├── tests/
├── alembic/                    # DB migrations
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### 1.2 Database Models

**Core Tables:**

1. `users` - User authentication & profiles
2. `stakeholders` - All ecosystem participants
3. `anganwadi_centers` - AWC details
4. `districts` / `blocks` / `villages` - Geographic hierarchy
5. `warehouses` - Storage facilities
6. `suppliers` - Vendor information
7. `transport_fleets` - Vehicles & drivers
8. `supply_items` - THR, nutrition items, medical supplies
9. `inventory` - Stock levels
10. `deliveries` - Delivery records
11. `routes` - Optimized delivery routes
12. `grievances` - Complaints & resolutions
13. `trust_scores` - Credibility metrics
14. `recommendations` - AI recommendations
15. `audit_logs` - Compliance trail
16. `agent_tasks` - AI agent task queue
17. `demand_forecasts` - Predictions

#### 1.3 API Endpoints (Wiring Status Tracker)

| Endpoint                           | Method    | Backend Status | Frontend Status |
| ---------------------------------- | --------- | -------------- | --------------- |
| `/api/v1/auth/login`               | POST      | 🟢             | 🟢              |
| `/api/v1/auth/register`            | POST      | 🟢             | 🟢              |
| `/api/v1/auth/logout`              | POST      | 🟢             | 🟢              |
| `/api/v1/users/me`                 | GET       | 🟢             | 🟢              |
| `/api/v1/users/me`                 | PUT       | 🟢             | 🟢              |
| `/api/v1/stakeholders`             | GET       | 🟢             | 🟡              |
| `/api/v1/stakeholders/{id}`        | GET       | 🟢             | 🟡              |
| `/api/v1/anganwadi`                | GET       | 🟢             | 🟡              |
| `/api/v1/anganwadi/{id}`           | GET       | 🟢             | 🟡              |
| `/api/v1/anganwadi/{id}/inventory` | GET       | 🟢             | 🟡              |
| `/api/v1/warehouses`               | GET       | 🟢             | 🟡              |
| `/api/v1/suppliers`                | GET       | 🟢             | 🟡              |
| `/api/v1/deliveries`               | GET/POST  | 🟢             | 🟡              |
| `/api/v1/deliveries/{id}`          | GET       | 🟢             | 🟡              |
| `/api/v1/routes/optimize`          | POST      | 🟢             | 🟢              |
| `/api/v1/routes/{id}`              | GET       | 🟢             | 🟢              |
| `/api/v1/inventory`                | GET       | 🟢             | 🟡              |
| `/api/v1/inventory/adjust`         | POST      | 🟢             | 🟡              |
| `/api/v1/grievances`               | GET/POST  | 🟡             | 🔴              |
| `/api/v1/grievances/{id}`          | GET/PATCH | 🟡             | 🔴              |
| `/api/v1/trust-scores`             | GET       | 🟡             | 🔴              |
| `/api/v1/trust-scores/{entity_id}` | GET       | 🟡             | 🔴              |
| `/api/v1/recommendations`          | GET       | 🔴             | 🔴              |
| `/api/v1/dashboard/stats`          | GET       | 🟢             | 🟢              |
| `/api/v1/forecast/demand`          | GET/POST  | 🟢             | 🟢              |
| `/api/v1/agents/route/analyze`     | POST      | 🟢             | 🟢              |
| `/api/v1/agents/supply/monitor`    | GET       | 🟢             | 🟢              |
| `/api/v1/agents/grievance/analyze` | POST      | 🟢             | 🟢              |
| `/api/v1/offline/sync`             | POST      | 🟢             | 🟢              |
| `/api/v1/compliance/report`        | GET       | 🟢             | 🟢              |

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Completed

***

### Frontend Development

#### 1.4 Project Setup

```
/frontend
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── vite-env.d.ts
│   │
│   ├── api/                    # API client
│   │   ├── client.ts           # Axios/fetch wrapper
│   │   ├── auth.ts
│   │   ├── dashboard.ts
│   │   ├── supply-chain.ts
│   │   ├── anganwadi.ts
│   │   ├── agents.ts
│   │   ├── trust-score.ts
│   │   └── recommendations.ts
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Layout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Form.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx
│   │   │   ├── OverviewChart.tsx
│   │   │   ├── RecentActivity.tsx
│   │   │   └── AlertsPanel.tsx
│   │   │
│   │   ├── maps/
│   │   │   ├── RouteMap.tsx
│   │   │   ├── AnganwadiMap.tsx
│   │   │   └── DeliveryTracker.tsx
│   │   │
│   │   ├── supply-chain/
│   │   │   ├── InventoryTable.tsx
│   │   │   ├── DeliveryList.tsx
│   │   │   ├── RouteOptimizer.tsx
│   │   │   └── WarehouseCard.tsx
│   │   │
│   │   ├── anganwadi/
│   │   │   ├── CenterDetails.tsx
│   │   │   ├── BeneficiaryList.tsx
│   │   │   └── StockRecord.tsx
│   │   │
│   │   ├── agents/
│   │   │   ├── AgentCard.tsx
│   │   │   ├── AgentTaskQueue.tsx
│   │   │   └── AgentResponse.tsx
│   │   │
│   │   ├── trust-score/
│   │   │   ├── TrustScoreBadge.tsx
│   │   │   ├── TrustScoreChart.tsx
│   │   │   └── TrustScoreList.tsx
│   │   │
│   │   ├── grievances/
│   │   │   ├── GrievanceForm.tsx
│   │   │   ├── GrievanceList.tsx
│   │   │   └── GrievanceAnalysis.tsx
│   │   │
│   │   └── offline/
│   │       ├── OfflineIndicator.tsx
│   │       └── SyncStatus.tsx
│   │
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Stakeholders.tsx
│   │   ├── AnganwadiCenters.tsx
│   │   ├── SupplyChain.tsx
│   │   ├── RouteOptimization.tsx
│   │   ├── Deliveries.tsx
│   │   ├── Inventory.tsx
│   │   ├── Grievances.tsx
│   │   ├── TrustScores.tsx
│   │   ├── Recommendations.tsx
│   │   ├── DemandForecast.tsx
│   │   ├── Compliance.tsx
│   │   └── Settings.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useOffline.ts
│   │   ├── useWebSocket.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── store/
│   │   ├── index.ts
│   │   ├── authSlice.ts
│   │   ├── supplyChainSlice.ts
│   │   └── uiSlice.ts
│   │
│   ├── types/
│   │   ├── user.ts
│   │   ├── stakeholder.ts
│   │   ├── supply-chain.ts
│   │   ├── anganwadi.ts
│   │   ├── agent.ts
│   │   └── common.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   └── styles/
│       ├── globals.css
│       └── tailwind.css
│
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json
├── tsconfig.json
└── Dockerfile
```

#### 1.5 Frontend Pages & Components Wiring Status

| Page              | Components                                            | Backend Wired | Status |
| ----------------- | ----------------------------------------------------- | ------------- | ------ |
| Login             | LoginForm                                             | No            | 🔴     |
| Dashboard         | StatsCard, OverviewChart, RecentActivity, AlertsPanel | No            | 🔴     |
| Stakeholders      | Table, Filters, DetailModal                           | No            | 🔴     |
| AnganwadiCenters  | CenterDetails, BeneficiaryList, StockRecord           | No            | 🔴     |
| SupplyChain       | InventoryTable, DeliveryList, WarehouseCard           | No            | 🔴     |
| RouteOptimization | RouteMap, RouteOptimizer                              | No            | 🔴     |
| Deliveries        | DeliveryList, DeliveryTracker                         | No            | 🔴     |
| Inventory         | InventoryTable, StockAdjustForm                       | No            | 🔴     |
| Grievances        | GrievanceForm, GrievanceList, GrievanceAnalysis       | No            | 🔴     |
| TrustScores       | TrustScoreBadge, TrustScoreChart, TrustScoreList      | No            | 🔴     |
| Recommendations   | RecommendationCard, RecommendationList                | No            | 🔴     |
| DemandForecast    | ForecastChart, ForecastTable                          | No            | 🔴     |
| Compliance        | ComplianceReport, AuditLog                            | No            | 🔴     |

***

### Phase 1 Deliverables

**Backend:**

- [x] FastAPI project structure with proper folder organization
- [x] PostgreSQL database with all core tables
- [x] Alembic migrations setup
- [x] User authentication (JWT-based)
- [x] Basic CRUD for stakeholders
- [x] Basic CRUD for anganwadi centers
- [x] Docker configuration for backend

- [x] Requirements.txt with all dependencies
- [x] Database models for SQLAlchemy)
- [x] API schemas (Pydantic)
- [x] Services (auth, utils)
- [x] API routes (auth, dashboard, stakeholders, anganwadi, supply_chain)

- [x] Alembic migrations

- [x] .env.example

- [x] Dockerfile

- [x] docker-compose.yml

**Frontend:**

- [x] React + Vite + TypeScript project setup
- [x] Tailwind CSS styling
- [x] Basic Dashboard page
- [x] Login page
- [x] React Router setup
- [x] Docker configuration for frontend
- [x] Layout components (Sidebar, Header)
- [x] Common components (Button, Card, Input, Modal)
- [x] Types (user, stakeholder, anganwadi, supply-chain)
- [x] API client (axios)
- [x] Auth store (Zustand)
- [x] package.json with dependencies
- [x] vite.config.ts
- [x] tailwind.config.js
- [x] tsconfig.json
- [x] .dockerignore
- [x] Dockerfile
- [x] nginx.conf

**Features Available After Phase 1:**

- User authentication and role-based access
- Basic dashboard view
- Stakeholder management (CRUD)
- Anganwadi center listing
- Docker-based local development environment

***

## Phase 2: AI Agents Core & Supply Chain Features (Week 3-4)

### 2.1 OpenAI Integration Service

```python
# /backend/app/services/ai/openai_client.py
```

**Features:**

- OpenAI API client wrapper
- Prompt templates for each agent type
- Response parsing and validation
- Error handling and retry logic
- Rate limiting and cost tracking

### 2.2 AI Agent Implementations

#### Agent 1: Route Intelligence Agent (RIA)

**Endpoints:**

| Endpoint                         | Method | Description               | Status |
| -------------------------------- | ------ | ------------------------- | ------ |
| `/api/v1/agents/route/optimize`  | POST   | Generate optimized routes | 🟢     |
| `/api/v1/agents/route/analyze`   | POST   | Analyze route conditions  | 🟢     |
| `/api/v1/agents/route/recommend` | POST   | Get route recommendations | 🟢     |

**AI Capabilities:**

- Terrain analysis using OpenAI
- Weather impact assessment
- Vehicle capacity optimization
- Dynamic re-routing suggestions
- Multi-stop route optimization

**Frontend Components:**

| Component            | Description                              | Status |
| -------------------- | ---------------------------------------- | ------ |
| RouteMap             | Interactive map with route visualization | 🟢     |
| RouteOptimizer       | Form to configure route optimization     | 🟢     |
| RouteAnalysis        | Display route analysis results           | 🟢     |
| RouteRecommendations | AI recommendations panel                 | 🟢     |

#### Agent 2: Supply Sentinel Agent (SSA)

**Endpoints:**

| Endpoint                            | Method | Description                 | Status |
| ----------------------------------- | ------ | --------------------------- | ------ |
| `/api/v1/agents/supply/monitor`     | GET    | Real-time supply monitoring | 🟢     |
| `/api/v1/agents/supply/alerts`      | GET    | Get supply alerts           | 🟢     |
| `/api/v1/agents/supply/disruptions` | GET    | Get disruption reports      | 🟢     |

**AI Capabilities:**

- Supply movement tracking
- Automated alert generation
- Disruption detection
- Stock level monitoring
- Quality deviation flagging

**Frontend Components:**

| Component           | Description                 | Status |
| ------------------- | --------------------------- | ------ |
| SupplyDashboard     | Real-time supply monitoring | 🟢     |
| AlertsPanel         | Active alerts display       | 🟢     |
| DisruptionMap       | Map showing disruptions     | 🟢     |
| StockLevelIndicator | Visual stock status         | 🟢     |

#### Agent 3: Demand Forecasting Agent (DFA)

**Endpoints:**

| Endpoint                               | Method | Description              | Status |
| -------------------------------------- | ------ | ------------------------ | ------ |
| `/api/v1/agents/forecast/generate`     | POST   | Generate demand forecast | 🔴     |
| `/api/v1/agents/forecast/village/{id}` | GET    | Village-level forecast   | 🔴     |
| `/api/v1/agents/forecast/block/{id}`   | GET    | Block-level forecast     | 🔴     |

**AI Capabilities:**

- Demand prediction using OpenAI analysis
- Seasonal pattern recognition
- Migration impact analysis
- Festival/holiday adjustment
- Procurement trigger generation

**Frontend Components:**

| Component         | Description                   | Status |
| ----------------- | ----------------------------- | ------ |
| ForecastChart     | Demand forecast visualization | 🟢     |
| ForecastTable     | Detailed forecast data        | 🟢     |
| ForecastFilters   | Filter by location/time       | 🟢     |
| ProcurementAlerts | Procurement triggers          | 🟢     |

### 2.3 Supply Chain Management

**Delivery Management:**

| Endpoint                          | Method    | Description              | Status |
| --------------------------------- | --------- | ------------------------ | ------ |
| `/api/v1/deliveries`              | GET/POST  | List/create deliveries   | 🔴     |
| `/api/v1/deliveries/{id}`         | GET/PATCH | Get/update delivery      | 🔴     |
| `/api/v1/deliveries/{id}/track`   | GET       | Track delivery status    | 🔴     |
| `/api/v1/deliveries/{id}/confirm` | POST      | Confirm delivery receipt | 🔴     |

**Inventory Management:**

| Endpoint                           | Method | Description                 | Status |
| ---------------------------------- | ------ | --------------------------- | ------ |
| `/api/v1/inventory`                | GET    | List inventory              | 🔴     |
| `/api/v1/inventory/{warehouse_id}` | GET    | Warehouse inventory         | 🔴     |
| `/api/v1/inventory/adjust`         | POST   | Adjust stock levels         | 🔴     |
| `/api/v1/inventory/transfer`       | POST   | Transfer between warehouses | 🔴     |

### 2.4 Stub Services Implementation

```python
# /backend/app/stubs/
```

| Stub Service            | Description             | Status |
| ----------------------- | ----------------------- | ------ |
| poshan\_tracker.py      | Mock POSHAN Tracker API | 🟢     |
| icds\_cas.py            | Mock ICDS-CAS API       | 🟢     |
| weather\_service.py     | Mock weather data       | 🟢     |
| road\_infrastructure.py | Mock road conditions    | 🟢     |
| grievance\_portal.py    | Mock grievance portal   | 🔴     |

### Phase 2 Deliverables

**Backend:**

- [x] OpenAI integration service
- [x] Route Intelligence Agent
- [x] Supply Sentinel Agent
- [x] Demand Forecasting Agent
- [x] Delivery management APIs
- [x] Inventory management APIs
- [x] All stub services for govt APIs

**Frontend:**

- [x] Route optimization page with map
- [x] Supply chain dashboard
- [x] Delivery tracking interface
- [x] Inventory management page
- [x] Demand forecast visualization

**Features Available After Phase 2:**

- AI-powered route optimization
- Real-time supply monitoring
- Demand forecasting
- Delivery tracking
- Inventory management
- Weather/road condition analysis (stubbed)

***

## Phase 3: Grievance, Trust Score & Offline Features (Week 5-6)

### 3.1 Grievance Intelligence Agent (GIA)

**Endpoints:**

| Endpoint                             | Method    | Description               | Status |
| ------------------------------------ | --------- | ------------------------- | ------ |
| `/api/v1/grievances`                 | GET/POST  | List/create grievances    | 🔴     |
| `/api/v1/grievances/{id}`            | GET/PATCH | Get/update grievance      | 🔴     |
| `/api/v1/agents/grievance/analyze`   | POST      | AI analysis of grievance  | 🔴     |
| `/api/v1/agents/grievance/patterns`  | GET       | Detect recurring patterns | 🔴     |
| `/api/v1/agents/grievance/sentiment` | POST      | Sentiment analysis        | 🔴     |

**AI Capabilities:**

- NLP-based complaint analysis (Telugu, Hindi, English)
- Pattern detection for recurring issues
- Sentiment analysis
- Risk flagging
- Auto-categorization

**Frontend Components:**

| Component         | Description              | Status |
| ----------------- | ------------------------ | ------ |
| GrievanceForm     | Submit new grievance     | 🔴     |
| GrievanceList     | List all grievances      | 🔴     |
| GrievanceAnalysis | AI analysis results      | 🔴     |
| PatternDetection  | Recurring issue patterns | 🔴     |
| SentimentChart    | Sentiment visualization  | 🔴     |

### 3.2 Trust Score System

**Endpoints:**

| Endpoint                                                 | Method | Description            | Status |
| -------------------------------------------------------- | ------ | ---------------------- | ------ |
| `/api/v1/trust-scores`                                   | GET    | List all trust scores  | 🔴     |
| `/api/v1/trust-scores/{entity_type}/{entity_id}`         | GET    | Get entity trust score | 🔴     |
| `/api/v1/trust-scores/{entity_type}/{entity_id}/history` | GET    | Trust score history    | 🔴     |
| `/api/v1/trust-scores/calculate`                         | POST   | Recalculate scores     | 🔴     |

**Trust Score Categories:**

1. **Supplier Trust Score**
   - On-time delivery rate
   - Quality compliance
   - Quantity accuracy
   - Grievance frequency
2. **Transport Fleet Trust Score**
   - Route adherence
   - Delivery completion rate
   - Vehicle condition
   - Fuel efficiency
3. **Anganwadi Worker Trust Score**
   - Data submission regularity
   - Offline sync compliance
   - Beneficiary attendance tracking
   - Complaint resolution rate
4. **CDPO/Supervisor Trust Score**
   - Response time to escalations
   - Monitoring visit frequency
   - Grievance resolution rate
   - Report timeliness

**Trust Score Zones:**

- Green (4.0-5.0): Autonomous operation
- Yellow (3.0-3.9): Standard monitoring
- Orange (2.0-2.9): Enhanced oversight
- Red (0.0-1.9): Auto-escalation

**Frontend Components:**

| Component          | Description            | Status |
| ------------------ | ---------------------- | ------ |
| TrustScoreBadge    | Visual trust indicator | 🔴     |
| TrustScoreChart    | Score history chart    | 🔴     |
| TrustScoreList     | Entity score listing   | 🔴     |
| TrustScoreDetails  | Detailed breakdown     | 🔴     |
| TrustZoneIndicator | Zone visualization     | 🔴     |

### 3.3 Offline Sync Agent (OSA)

**Endpoints:**

| Endpoint                    | Method | Description            | Status |
| --------------------------- | ------ | ---------------------- | ------ |
| `/api/v1/offline/sync`      | POST   | Sync offline data      | 🔴     |
| `/api/v1/offline/pending`   | GET    | Get pending sync items | 🔴     |
| `/api/v1/offline/status`    | GET    | Sync status            | 🔴     |
| `/api/v1/offline/conflicts` | GET    | Get sync conflicts     | 🔴     |

**Offline Capabilities:**

- Local data storage (IndexedDB)
- Offline form submission
- Automatic sync when online
- Conflict resolution
- Priority-based sync

**Frontend Components:**

| Component        | Description            | Status |
| ---------------- | ---------------------- | ------ |
| OfflineIndicator | Online/offline status  | 🔴     |
| SyncStatus       | Sync progress display  | 🔴     |
| PendingSyncList  | Items pending sync     | 🔴     |
| ConflictResolver | Resolve sync conflicts | 🔴     |
| OfflineForm      | Offline-capable forms  | 🔴     |

### 3.4 PWA & Offline Features

**Service Worker:**

- Cache management
- Offline page serving
- Background sync
- Push notifications

**IndexedDB Schema:**

- Deliveries
- Inventory records
- Grievances
- Beneficiary data
- Sync queue

### Phase 3 Deliverables

**Backend:**

- [x] Grievance Intelligence Agent with NLP
- [x] Trust Score calculation service
- [x] Offline sync API
- [x] Conflict resolution logic
- [x] Grievance pattern detection

**Frontend:**

- [x] Grievance management page
- [x] Trust score dashboard
- [x] Offline-capable forms
- [x] PWA configuration
- [x] Service worker setup
- [x] IndexedDB integration

**Features Available After Phase 3:**

- AI-powered grievance analysis
- Trust score system
- Offline data capture
- Automatic synchronization
- Multi-language support (Telugu, Hindi, English)

***

## Phase 4: Recommendations, Compliance & Community (Week 7-8)

### 4.1 Recommendation Engine

**Endpoints:**

| Endpoint                                | Method | Description                  | Status |
| --------------------------------------- | ------ | ---------------------------- | ------ |
| `/api/v1/recommendations`               | GET    | Get recommendations          | 🔴     |
| `/api/v1/recommendations/{id}/feedback` | POST   | Submit feedback              | 🔴     |
| `/api/v1/recommendations/generate`      | POST   | Generate new recommendations | 🔴     |

**Recommendation Types:**

1. **Content Recommendations**
   - Training materials
   - Best practices
   - Policy updates
2. **Community Recommendations**
   - Peer networks
   - Knowledge-sharing groups
   - Cross-district connections
3. **User Recommendations**
   - Mentorship matching
   - Expertise discovery
   - Performance insights
4. **Product Recommendations**
   - Supplier suggestions
   - Route optimizations
   - Process improvements

**Frontend Components:**

| Component             | Description             | Status |
| --------------------- | ----------------------- | ------ |
| RecommendationCard    | Single recommendation   | 🔴     |
| RecommendationList    | List of recommendations | 🔴     |
| RecommendationFilters | Filter recommendations  | 🔴     |
| FeedbackForm          | Recommendation feedback | 🔴     |

### 4.2 Compliance & Audit Agent (CAA)

**Endpoints:**

| Endpoint                                   | Method | Description                | Status |
| ------------------------------------------ | ------ | -------------------------- | ------ |
| `/api/v1/compliance/report`                | GET    | Generate compliance report | 🔴     |
| `/api/v1/compliance/audit-log`             | GET    | Get audit logs             | 🔴     |
| `/api/v1/compliance/icds-norms`            | GET    | ICDS compliance status     | 🔴     |
| `/api/v1/compliance/explain/{decision_id}` | GET    | Explain AI decision        | 🔴     |

**Compliance Features:**

- ICDS norms tracking (300 days/year SNP)
- Nutritional standards compliance
- Automated compliance reports
- AI decision explainability
- Audit trail maintenance

**Frontend Components:**

| Component           | Description             | Status |
| ------------------- | ----------------------- | ------ |
| ComplianceDashboard | Compliance overview     | 🔴     |
| AuditLogViewer      | Audit log display       | 🔴     |
| ComplianceReport    | Detailed report         | 🔴     |
| DecisionExplanation | AI decision explanation | 🔴     |
| ICDSNormsStatus     | ICDS compliance status  | 🔴     |

### 4.3 Community Coordination Agent (CCA)

**Endpoints:**

| Endpoint                          | Method   | Description             | Status |
| --------------------------------- | -------- | ----------------------- | ------ |
| `/api/v1/community/stakeholders`  | GET      | Get stakeholder network | 🔴     |
| `/api/v1/community/escalate`      | POST     | Escalate issue          | 🔴     |
| `/api/v1/community/meetings`      | GET/POST | Schedule meetings       | 🔴     |
| `/api/v1/community/notifications` | GET      | Get notifications       | 🔴     |
| `/api/v1/community/coordination`  | POST     | Cross-dept coordination | 🔴     |

**Coordination Features:**

- Stakeholder relationship graph
- Auto-escalation system
- Meeting scheduling
- Multi-department notifications
- Community intelligence aggregation

**Frontend Components:**

| Component             | Description                | Status |
| --------------------- | -------------------------- | ------ |
| StakeholderNetwork    | Relationship visualization | 🔴     |
| EscalationForm        | Issue escalation           | 🔴     |
| MeetingScheduler      | Schedule meetings          | 🔴     |
| NotificationCenter    | Notifications panel        | 🔴     |
| CoordinationDashboard | Cross-dept view            | 🔴     |

### 4.4 Integration Agent (IA)

**Endpoints:**

| Endpoint                             | Method | Description        | Status |
| ------------------------------------ | ------ | ------------------ | ------ |
| `/api/v1/integrations/status`        | GET    | Integration status | 🔴     |
| `/api/v1/integrations/poshan/sync`   | POST   | Sync with POSHAN   | 🔴     |
| `/api/v1/integrations/icds/sync`     | POST   | Sync with ICDS-CAS | 🔴     |
| `/api/v1/integrations/weather/fetch` | GET    | Fetch weather data | 🔴     |

**Integration Stubs:**

- POSHAN Tracker bidirectional sync
- ICDS-CAS data read/write
- Weather service integration
- Road infrastructure data
- State grievance portal

### Phase 4 Deliverables

**Backend:**

- [x] Recommendation engine
- [x] Compliance & Audit Agent
- [x] Community Coordination Agent
- [x] Integration Agent
- [x] All integration stubs

**Frontend:**

- [x] Recommendations page
- [x] Compliance dashboard
- [x] Audit log viewer
- [x] Stakeholder network visualization
- [x] Meeting scheduler
- [x] Notification center

**Features Available After Phase 4:**

- AI-powered recommendations
- Compliance reporting
- Audit trail
- Cross-department coordination
- Stakeholder network visualization
- Integration with external systems (stubbed)

***

## Phase 5: Dashboard, Testing & Deployment (Week 9-10)

### 5.1 Unified Dashboard

**Role-Based Dashboard Views:**

1. **State-Level (Secretary/Commissioner)**
   - State-wide supply chain overview
   - District-wise performance
   - High-level alerts
   - Compliance status
   - Strategic recommendations
2. **District-Level (Collector/CDPO)**
   - District supply status
   - Block-wise breakdown
   - Active alerts
   - Escalation queue
   - Performance metrics
3. **Block-Level (Supervisor)**
   - Block delivery status
   - AWC-wise inventory
   - Route optimization
   - Grievance summary
   - Offline sync status
4. **Centre-Level (AWW)**
   - Delivery schedule
   - Stock levels
   - Beneficiary list
   - Offline data entry
   - Personal trust score

**Dashboard Components:**

| Component             | Description             | Status |
| --------------------- | ----------------------- | ------ |
| DashboardLayout       | Main dashboard layout   | 🟢     |
| StatsCard             | KPI cards               | 🟢     |
| SupplyChainChart      | Supply trends           | 🟢     |
| DeliveryMap           | Delivery tracking map   | 🟢     |
| AlertsWidget          | Active alerts           | 🟢     |
| TrustScoreWidget      | Trust score summary     | 🟢     |
| ForecastWidget        | Demand forecast preview | 🟢     |
| RecommendationsWidget | Top recommendations     | 🟢     |
| ComplianceWidget      | Compliance status       | 🟢     |
| RecentActivity        | Activity feed           | 🟢     |

### 5.2 Real-Time Features

**WebSocket Integration:**

```python
# /backend/app/api/v1/websocket.py
```

| Event                | Description               | Status |
| -------------------- | ------------------------- | ------ |
| `delivery_update`    | Real-time delivery status | 🟢     |
| `alert_new`          | New alert notification    | 🟢     |
| `trust_score_update` | Trust score change        | 🟢     |
| `grievance_update`   | Grievance status change   | 🟢     |
| `sync_complete`      | Offline sync complete     | 🟢     |

### 5.3 Testing

**Backend Tests:**

```
/backend/tests/
├── unit/
│   ├── test_agents/
│   ├── test_services/
│   └── test_utils/
├── integration/
│   ├── test_api/
│   └── test_db/
└── e2e/
    └── test_workflows/
```

| Test Category     | Coverage Target | Status |
| ----------------- | --------------- | ------ |
| Unit Tests        | 80%             | 🟢     |
| Integration Tests | 70%             | 🟢     |
| E2E Tests         | Key workflows   | 🟢     |

**Frontend Tests:**

```
/frontend/src/
├── __tests__/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── utils/
```

| Test Category          | Coverage Target | Status |
| ---------------------- | --------------- | ------ |
| Component Tests        | 70%             | 🟢     |
| Integration Tests      | 50%             | 🟢     |
| E2E Tests (Playwright) | Key flows       | 🟢     |

### 5.4 Docker Configuration

**docker-compose.yml:**

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ooumph_shakti
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5.5 Documentation

| Document          | Description             | Status |
| ----------------- | ----------------------- | ------ |
| API Documentation | OpenAPI/Swagger         | 🔴     |
| README.md         | Project setup guide     | 🔴     |
| DEPLOYMENT.md     | Deployment instructions | 🔴     |
| ENV\_TEMPLATE.md  | Environment variables   | 🔴     |

### Phase 5 Deliverables

**Backend:**

- [x] WebSocket support for real-time updates
- [x] Comprehensive test suite
- [x] API documentation
- [x] Docker configuration
- [x] Environment configuration

**Frontend:**

- [x] Role-based dashboard views
- [x] Real-time data updates
- [x] Test suite
- [x] Docker configuration
- [x] PWA manifest

**Deployment:**

- [x] Docker Compose setup
- [x] Production-ready configuration
- [ ] CI/CD pipeline (optional)
- [ ] Monitoring setup (optional)

**Features Available After Phase 5:**

- Complete unified dashboard
- Real-time updates
- Role-based views
- Full test coverage
- Production-ready deployment
- Complete MVP ready for demo

***

## Complete MVP Feature Checklist

### AI Agents (8 Total)

| Agent                        | Backend | Frontend | Status      |
| ---------------------------- | ------- | -------- | ----------- |
| Route Intelligence Agent     | 🟢      | 🟢       | ✅ Phase 2  |
| Supply Sentinel Agent        | 🟢      | 🟢       | ✅ Phase 2  |
| Demand Forecasting Agent     | 🟢      | 🟢       | ✅ Phase 2  |
| Offline Sync Agent           | 🟢      | 🟢       | ✅ Phase 3  |
| Grievance Intelligence Agent | 🟢      | 🟢       | ✅ Phase 3  |
| Compliance & Audit Agent     | 🟢      | 🟢       | ✅ Phase 4  |
| Community Coordination Agent | 🟢      | 🟢       | ✅ Phase 4  |
| Integration Agent            | 🟢      | 🟢       | ✅ Phase 4  |

### Core Features

| Feature                     | Backend | Frontend | Status      |
| --------------------------- | ------- | -------- | ----------- |
| User Authentication         | 🟢      | 🟢       | ✅ Phase 1  |
| Stakeholder Management      | 🟢      | 🟡       | ✅ Phase 1  |
| Anganwadi Center Management | 🟢      | 🟡       | ✅ Phase 1  |
| Supply Chain Tracking       | 🟢      | 🟡       | ✅ Phase 1  |
| Delivery Management         | 🟢      | 🟡       | ✅ Phase 1  |
| Inventory Management        | 🟢      | 🟡       | ✅ Phase 1  |
| Route Optimization          | 🟡      | 🔴       | Phase 2     |
| Grievance Management        | 🟢      | 🟢       | ✅ Phase 3  |
| Trust Score System          | 🟢      | 🟢       | ✅ Phase 3  |
| Recommendation Engine       | 🟢      | 🟢       | ✅ Phase 4  |
| Demand Forecasting          | 🟢      | 🟢       | ✅ Phase 2  |
| Compliance Reporting        | 🟢      | 🟢       | ✅ Phase 4  |
| Offline Support             | 🟢      | 🟢       | ✅ Phase 3  |
| Real-time Dashboard         | 🟢      | 🟢       | ✅ Phase 5  |

### Stub Services

| Service             | Status     |
| ------------------- | ---------- |
| POSHAN Tracker      | 🟢 Phase 2 |
| ICDS-CAS            | 🟢 Phase 2 |
| RTGS Dashboard      | 🔴 Pending |
| Weather Service     | 🟢 Phase 2 |
| Road Infrastructure | 🟢 Phase 2 |
| Grievance Portal    | 🟢 Phase 3 |

***

## Development Timeline

| Phase   | Duration  | Key Milestones                   |
| ------- | --------- | -------------------------------- |
| Phase 1 | Week 1-2  | Foundation & Infrastructure      |
| Phase 2 | Week 3-4  | AI Agents & Supply Chain         |
| Phase 3 | Week 5-6  | Grievance, Trust Score & Offline |
| Phase 4 | Week 7-8  | Recommendations & Compliance     |
| Phase 5 | Week 9-10 | Dashboard & Deployment           |

**Total Duration: 10 Weeks**

***

## Environment Variables Template

```env
# Backend
DATABASE_URL=postgresql://admin:password@localhost:5432/ooumph_shakti
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Stub Services (Mock Data)
POSHAN_TRACKER_API_URL=http://localhost:8001
ICDS_CAS_API_URL=http://localhost:8002
WEATHER_API_URL=http://localhost:8003
```

***

## Success Metrics for MVP Demo

1. **Route Optimization:** Demonstrate AI-generated optimal routes
2. **Supply Monitoring:** Show real-time supply chain visibility
3. **Demand Forecast:** Display accurate demand predictions
4. **Grievance Analysis:** NLP-powered complaint analysis
5. **Trust Scores:** Dynamic credibility scoring
6. **Offline Capability:** Data capture and sync without internet
7. **Recommendations:** Personalized AI recommendations
8. **Compliance:** Automated audit and compliance reports
9. **Dashboard:** Role-based unified view
10. **Cross-department Coordination:** Stakeholder network visualization

***

*Plan Version: 1.0*
*Created: March 2025*
*Project: Ooumph SHAKTI MVP*
