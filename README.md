# UER-VMS: Unified Electoral Roll - Voter Management System

A **blockchain-based electoral roll management system** designed to prevent voter fraud through AI-powered deduplication and nationwide vote locking. This system enables secure voter registration, cross-state transfers, and biometrically-verified voting.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

---

## 🎯 Overview

UER-VMS addresses critical challenges in electoral systems:

| Challenge                 | Solution                                             |
| ------------------------- | ---------------------------------------------------- |
| **Duplicate Voters**      | AI-powered face recognition + phonetic name matching |
| **Double Voting**         | Blockchain-based nationwide voter locking            |
| **Inter-state Fraud**     | Smart contract ownership transfer mechanism          |
| **Identity Verification** | Biometric verification at voting time                |

### Key Principles

1. **Blockchain as Source of Truth** - All voter ownership and vote status is immutably recorded
2. **AI Deduplication** - Multi-factor matching (face, name, DOB) prevents duplicate registrations
3. **Decentralized States** - Each state operates independently but shares a common blockchain ledger
4. **Tamper Detection** - Hash-based integrity verification at every step

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Vite + React)                        │
│                    Port: 5174 → Routes to State Backends                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌───────────────────────────────┐     ┌───────────────────────────────┐
│      BACKEND - STATE A        │     │      BACKEND - STATE B        │
│        (Maharashtra)          │     │        (Karnataka)            │
│        Port: 8001             │     │        Port: 8002             │
├───────────────────────────────┤     ├───────────────────────────────┤
│ • Voter Registration          │     │ • Voter Registration          │
│ • Transfer Initiation         │◄───►│ • Transfer Reception          │
│ • Voting & Verification       │     │ • Voting & Verification       │
└───────────────┬───────────────┘     └───────────────┬───────────────┘
                │                                     │
                ▼                                     ▼
┌───────────────────────────────┐     ┌───────────────────────────────┐
│    PostgreSQL - State A       │     │    PostgreSQL - State B       │
│    Port: 5432                 │     │    Port: 5433                 │
│    (Voter Details DB)         │     │    (Voter Details DB)         │
└───────────────────────────────┘     └───────────────────────────────┘
                │                                     │
                └─────────────────┬───────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BLOCKCHAIN LAYER (Simulated)                        │
│         Uses PostgreSQL to store ledger entries for hackathon demo          │
├─────────────────────────────────┬───────────────────────────────────────────┤
│    Blockchain Node A (5434)     │     Blockchain Node B (5435)              │
│    • BlockchainLedger table     │     • VoterAsset table                    │
│    • Immutable transaction log  │     • Ownership tracking                  │
└─────────────────────────────────┴───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI DEDUPLICATION SERVICE                            │
│                              Port: 8003                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ • FaceNet-based Face Recognition                                            │
│ • Phonetic Name Matching (Soundex/Metaphone)                                │
│ • Date of Birth Verification                                                │
│ • Multi-factor Confidence Scoring                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend

| Component   | Technology                 |
| ----------- | -------------------------- |
| Framework   | **FastAPI** (Python 3.10+) |
| Database    | **PostgreSQL 15** (Alpine) |
| ORM         | **SQLAlchemy**             |
| HTTP Client | **httpx** (async)          |
| Task Runner | **Uvicorn**                |

### AI Service

| Component        | Technology                            |
| ---------------- | ------------------------------------- |
| Face Recognition | **face_recognition** (dlib + FaceNet) |
| Image Processing | **Pillow**, **NumPy**                 |
| Similarity       | Custom phonetic matching              |

### Frontend

| Component   | Technology                   |
| ----------- | ---------------------------- |
| Framework   | **React 18** with TypeScript |
| Build Tool  | **Vite 5**                   |
| Styling     | **Tailwind CSS 3**           |
| Camera      | **react-webcam**             |
| HTTP Client | **axios**                    |
| Routing     | **react-router-dom 6**       |

### Infrastructure

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Containerization | **Docker** + **Docker Compose** |
| Networking       | Docker Bridge Network           |

---

## 📁 Project Structure

```
uer-vms/
├── backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── registration.py   # POST /api/registration/register
│   │   │       ├── transfer.py       # POST /api/transfer/transfer
│   │   │       ├── voting.py         # POST /api/voting/vote
│   │   │       └── admin.py          # Admin endpoints
│   │   ├── blockchain/
│   │   │   └── smart_contract.py     # Blockchain logic simulation
│   │   ├── core/
│   │   │   └── config.py             # Settings and env variables
│   │   ├── database/
│   │   │   ├── base.py               # DB connection setup
│   │   │   └── models.py             # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── voter.py              # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ai_dedup.py           # AI service client
│   │   │   └── hash_service.py       # Hashing utilities
│   │   └── main.py                   # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
│
├── ai-service/                 # AI Deduplication Microservice
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py             # /api/dedup/check, /api/dedup/store
│   │   ├── core/
│   │   │   └── config.py             # AI service settings
│   │   ├── models/
│   │   │   ├── face_recognition.py   # FaceNet-based recognition
│   │   │   └── similarity.py         # Name/DOB matching
│   │   └── main.py                   # FastAPI app entry point
│   ├── models/                       # Pre-trained model weights
│   ├── storage/                      # Face encodings storage
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Vite + React Frontend
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── RegistrationPage.tsx
│   │   │   ├── TransferPage.tsx
│   │   │   ├── VotingPage.tsx
│   │   │   └── AdminDashboard.tsx
│   │   ├── services/                 # API client
│   │   ├── types/                    # TypeScript interfaces
│   │   └── App.tsx                   # Main app with routing
│   ├── Dockerfile
│   └── package.json
│
├── mock-data/                  # Sample voter data for testing
├── docker-compose.yml          # Full orchestration
└── .env                        # Environment configuration
```

---

## ✨ Core Features

### 1. Voter Registration

**Endpoint:** `POST /api/registration/register`

**Flow:**

1. **Photo Upload** - Validate and store voter photo
2. **AI Deduplication** - Check for existing voter using face + name + DOB
3. **Database Insert** - Create voter record in state database
4. **Blockchain Registration** - Register voter asset on blockchain
5. **Face Encoding Storage** - Store encoding for future verification

**Duplicate Detection:**

- Face similarity threshold: `0.6` (configurable)
- Phonetic name matching
- Date of birth exact match
- Combined confidence score calculation

### 2. Cross-State Transfer

**Endpoint:** `POST /api/transfer/transfer`

**Flow:**

1. **Ownership Verification** - Confirm voter belongs to source state
2. **Vote Lock Check** - Prevent transfer if already voted
3. **Blockchain Transfer** - Update ownership via smart contract
4. **Source State Update** - Mark voter as `MOVED`
5. **Destination State Activation** - Activate voter in new state

**Smart Contract Logic:**

```python
# Ownership transfer atomically updates:
# - BlockchainLedger: New entry with event_type="TRANSFERRED"
# - VoterAsset: current_owner_state → new state
# - transfer_history: Append transfer record
```

### 3. Biometric Voting

**Endpoint:** `POST /api/voting/vote`

**Flow:**

1. **Voter Lookup** - Verify voter exists in state database
2. **Biometric Verification** - Match live photo with registered encoding
3. **Double-Vote Check** - Query blockchain for existing vote
4. **Vote Lock** - Create `VOTED` blockchain entry (nationwide lock)
5. **Audit Log** - Record polling booth and transaction

**Double-Voting Prevention:**

- `VoterAsset.is_voted` flag checked before voting
- `VOTED` event is immutable on blockchain
- All states query same blockchain ledger

---

## 📡 API Reference

### Registration API

| Method | Endpoint                              | Description                   |
| ------ | ------------------------------------- | ----------------------------- |
| `POST` | `/api/registration/register`          | Register new voter with photo |
| `GET`  | `/api/registration/status/{voter_id}` | Get voter status              |

### Transfer API

| Method | Endpoint                 | Description                   |
| ------ | ------------------------ | ----------------------------- |
| `POST` | `/api/transfer/transfer` | Transfer voter between states |

### Voting API

| Method | Endpoint                             | Description                           |
| ------ | ------------------------------------ | ------------------------------------- |
| `POST` | `/api/voting/vote`                   | Cast vote with biometric verification |
| `GET`  | `/api/voting/eligibility/{voter_id}` | Check voting eligibility              |

### AI Deduplication API

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| `POST` | `/api/dedup/check` | Check for duplicate voter |
| `POST` | `/api/dedup/store` | Store face encoding       |
| `GET`  | `/api/health`      | Service health check      |

---

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.10+** (for local development)
- **Node.js 18+** (for frontend development)

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd uer-vms

# Start all services
docker-compose up --build

# Services will be available at:
# - Frontend:        http://localhost:5174
# - Backend State A: http://localhost:8001
# - Backend State B: http://localhost:8002
# - AI Service:      http://localhost:8003
```

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

#### AI Service

```bash
cd ai-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# State Configuration
STATE_ID=STATE_A                    # Unique state identifier
STATE_NAME=Maharashtra              # Human-readable state name

# Database
DATABASE_URL=postgresql://voter_admin:voter_pass_123@localhost:5432/voters_db
BLOCKCHAIN_URL=postgresql://blockchain_admin:blockchain_pass_123@localhost:5434/blockchain_db

# Services
AI_SERVICE_URL=http://localhost:8003
PEER_BACKEND_URL=http://localhost:8002

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
PHOTO_STORAGE_PATH=./storage/photos
MAX_PHOTO_SIZE_MB=5

# Frontend
VITE_BACKEND_STATE_A_URL=http://localhost:8001
VITE_BACKEND_STATE_B_URL=http://localhost:8002
```

---

## 🐳 Docker Deployment

### Service Ports

| Service            | Container Port | Host Port |
| ------------------ | -------------- | --------- |
| Frontend           | 5173           | 5174      |
| Backend State A    | 8000           | 8001      |
| Backend State B    | 8000           | 8002      |
| AI Service         | 8000           | 8003      |
| PostgreSQL State A | 5432           | 5432      |
| PostgreSQL State B | 5432           | 5433      |
| Blockchain Node A  | 5432           | 5434      |
| Blockchain Node B  | 5432           | 5435      |

### Volumes

| Volume                  | Purpose                  |
| ----------------------- | ------------------------ |
| `postgres-state-a-data` | State A voter database   |
| `postgres-state-b-data` | State B voter database   |
| `blockchain-a-data`     | Blockchain ledger Node A |
| `blockchain-b-data`     | Blockchain ledger Node B |
| `ai-models`             | AI model weights         |
| `voter-photos-a`        | Voter photos State A     |
| `voter-photos-b`        | Voter photos State B     |

### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend-state-a

# Stop all services
docker-compose down

# Reset all data
docker-compose down -v
```

---

## 🧪 Development

### Database Models

#### `Voter` (State Database)

- Personal info, address, contact
- Photo path, face encoding hash
- Blockchain reference (`blockchain_hash`, `blockchain_transaction_id`)
- Status: `ACTIVE`, `MOVED`, `VOTED`

#### `VoterAsset` (Blockchain)

- Ownership: `current_owner_state`
- Vote lock: `is_voted`, `voted_timestamp`
- Transfer history (JSON array)

#### `BlockchainLedger` (Blockchain)

- Immutable transaction log
- Event types: `REGISTERED`, `TRANSFERRED`, `VOTED`
- Hash chain: `previous_hash` → `current_hash`

### Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

---

## 📜 License

This project was developed for hackathon/demonstration purposes.

---

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.
