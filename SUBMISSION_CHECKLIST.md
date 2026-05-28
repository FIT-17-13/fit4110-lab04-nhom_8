# FIT4110 Lab 04 – Submission Checklist

**Project:** Smart Campus Operations Platform – IoT Ingestion Service  
**Lab:** Docker Packaging & Security Testing  
**Date:** May 2026

---

## 1) OBE Learning Outcomes

### Learning Objectives (LO targets):
- **LO1**: Understanding containerization with Docker multi-stage builds
- **LO2**: Implementing secure API design with Bearer token authentication
- **LO3**: Writing comprehensive security and boundary tests
- **LO4**: Documenting threat models and mitigation strategies

### Security Goals (3/4 achieved):
- ✅ **Authentication**: Bearer token validation on `/readings` endpoint
- ✅ **Integrity**: Input validation with boundary checking, ProblemDetails error responses
- ❌ Confidentiality: (Not required for HTTP/local lab)
- ✅ **Availability**: HEALTHCHECK + graceful error handling

---

## 2) Missions (Bắt Buộc)

### M1: Docker Container Setup & Deployment
**Objective:** Successfully build and run the service in a Docker container that is accessible and passes health checks.

**Requirements:**
- [x] Dockerfile with multi-stage build (builder + runtime)
- [x] Non-root user execution (appuser)
- [x] HEALTHCHECK configuration
- [x] .dockerignore to minimize context
- [x] .env.example for runtime configuration
- [x] Docker image builds without errors
- [x] Container starts and `/health` endpoint responds with `{"status": "ok"}`

**Success Criteria:**
```bash
docker build -t fit4110/iot-ingestion:lab04 .
docker run --rm -p 8000:8000 --env-file .env.example fit4110/iot-ingestion:lab04
curl http://localhost:8000/health  # Returns 200 + HealthResponse
```

---

### M2: Authentication & Authorization Testing
**Objective:** Verify that the service correctly enforces Bearer token authentication on protected endpoints.

**Requirements:**
- [x] `/health` endpoint is public (no auth required)
- [x] `/readings` endpoint requires valid Bearer token
- [x] Invalid/missing tokens return 401 Unauthorized with ProblemDetails
- [x] Valid token allows sensor reading creation
- [x] Postman collection includes auth header configuration
- [x] Newman report shows all auth tests passing

**Success Criteria:**
- POST to `/readings` without Authorization header → 401
- POST to `/readings` with invalid token → 401
- POST to `/readings` with valid token → 201/202
- All tests pass in Newman report

---

### M3: Data Validation & Boundary Testing
**Objective:** Ensure the service properly validates input data and enforces temperature boundary constraints.

**Requirements:**
- [x] Valid readings accepted: -40 to 80°C
- [x] Out-of-range values rejected: <-40 or >80°C
- [x] Boundary edge cases tested: -40.0, 80.0, -40.1 (reject), 80.1 (reject)
- [x] Missing required fields return 422 Unprocessable Entity
- [x] Device_id must be ≥3 characters
- [x] Malformed JSON returns 400 Bad Request
- [x] Response matches OpenAPI schema

**Success Criteria:**
- POST reading with value=31.5 → 201 Created ✓
- POST reading with value=85.0 → 422 Validation Error ✓
- POST reading with value=-50.0 → 422 Validation Error ✓
- POST missing device_id → 422 with detailed location ✓

---

## 3) Boss Fights (Test Lỗi Bắt Buộc)

### BF1: Tampered/Invalid Input – Fast Fail + Clear Error Log
**Attack:** Send boundary-violating or malformed data
**Expected Behavior:** Service rejects with 422, logs error details, continues accepting next requests

```json
Test: Temperature = 85.0 (above boundary)
Expected Response:
{
  "type": "about:blank",
  "title": "Validation error",
  "status": 422,
  "detail": "body.value: ensure this value is less than or equal to 80",
  "instance": "/readings"
}
Log: [2026-05-28 10:15:30] VALIDATION ERROR: body.value exceeds boundary
```

**Implementation:** [tests/test_boss_fight_1_boundary.py](tests/test_boss_fight_1_boundary.py)

---

### BF2: Authentication Bypass Attempt – Reject + Log Security Event
**Attack:** Send request with missing or incorrect Bearer token
**Expected Behavior:** Service returns 401, does NOT process request, logs security event

```
Test A: No Authorization header
Expected: 401 Unauthorized
Log: [2026-05-28 10:16:00] SECURITY: Missing Authorization header

Test B: Wrong token value
Expected: 401 Unauthorized  
Log: [2026-05-28 10:16:05] SECURITY: Invalid bearer token attempted
```

**Implementation:** [tests/test_boss_fight_2_auth.py](tests/test_boss_fight_2_auth.py)

---

### BF3: Schema Validation – Reject Malformed Payloads
**Attack:** Send JSON that violates OpenAPI schema (extra fields, wrong types, missing required fields)
**Expected Behavior:** Service rejects with 422, returns detailed error location

```json
Test: Missing required field "metric"
{
  "device_id": "ESP32-01",
  "value": 25.0,
  "unit": "celsius",
  "timestamp": "2026-05-28T10:00:00+07:00"
}
Expected: 422 Unprocessable Entity
{
  "type": "about:blank",
  "title": "Validation error", 
  "status": 422,
  "detail": "body.metric: field required",
  "instance": "/readings"
}
```

**Implementation:** [tests/test_boss_fight_3_schema.py](tests/test_boss_fight_3_schema.py)

---

## 4) Submission Files Checklist

### Core Documentation
- [x] **README.md** – How to run, packet format, ethics, OBE objectives
- [x] **RUN_LOCAL.md** – 3-5 step quick-start guide
- [x] **SUBMISSION_CHECKLIST.md** – This file
- [x] **report-1page.md** – Lab outcome summary with evidence
- [x] **threat-model-1page.md** – System threat model and mitigations

### Source Code & Configuration
- [x] **Dockerfile** – Multi-stage build, non-root user, healthcheck
- [x] **.dockerignore** – Excludes .git, __pycache__, .env, etc.
- [x] **.env.example** – Runtime config template
- [x] **src/iot_app/main.py** – FastAPI service implementation
- [x] **contracts/iot-ingestion.openapi.yaml** – OpenAPI 3.1 specification

### Testing & Evidence
- [x] **tests/** (≥5 comprehensive test files)
  - test_health.py – Health endpoint tests
  - test_functional.py – Happy path reading creation
  - test_boss_fight_1_boundary.py – Temperature boundary tests (BF1)
  - test_boss_fight_2_auth.py – Authentication tests (BF2)
  - test_boss_fight_3_schema.py – Schema validation tests (BF3)
  - test_integration.py – End-to-end container tests
- [x] **logs/** – Runtime evidence (container logs, health checks)
- [x] **bench.csv** – Performance benchmark (3 payload sizes)
- [x] **reports/** – Newman reports, screenshots

### Postman Assets
- [x] **postman/collections/FIT4110_lab04_iot_docker.postman_collection.json**
- [x] **postman/environments/FIT4110_lab04_local.postman_environment.json**
- [x] **postman/environments/FIT4110_lab04_mock.postman_environment.json**

---

## 5) Submission Steps

### In Submissions Portal (FIT4012):

1. **Create New Submission Item**
   - Title: "FIT4110 Lab 04 – IoT Docker – Group 8"
   - Description: Brief service description + link to github repo

2. **Attach Evidence**
   - Link to GitHub repo with this checklist complete
   - Docker Hub image tag (if pushed): `ghcr.io/your-org/fit4110-iot-ingestion:lab04`
   - Demo video link (optional): Running container + Postman tests

3. **Set Status = "Submitted"**

4. **Select Learning Outcomes Achieved**
   - ✅ LO1: Container design & Docker best practices
   - ✅ LO2: API security (authentication + validation)
   - ✅ LO3: Comprehensive testing (functional + security)
   - ✅ LO4: Threat model & mitigation strategies

---

## 6) Verification Checklist (Before Submitting)

### Build & Runtime
- [ ] `docker build` completes without errors or warnings
- [ ] `docker run` container starts and outputs no critical errors
- [ ] `curl http://localhost:8000/health` returns `{"status":"ok",...}`
- [ ] Container stops gracefully when sent SIGTERM

### Tests
- [ ] `pytest tests/` runs all ≥5 tests successfully
- [ ] All boss fight tests (BF1, BF2, BF3) are included and passing
- [ ] Newman report shows 100% test pass rate
- [ ] Logs show clear error messages for failed tests

### Documentation
- [ ] README.md includes: how to run, packet format, security practices
- [ ] RUN_LOCAL.md has ≤5 clear steps for reproduction
- [ ] threat-model-1page.md identifies ≥3 threats and mitigations
- [ ] report-1page.md shows lab objectives + evidence

### Code Quality
- [ ] No hardcoded secrets in source (use .env.example)
- [ ] .gitignore excludes __pycache__, .env, node_modules, etc.
- [ ] Code follows PEP 8 style guide (can check with `pylint` or `flake8`)
- [ ] Dockerfile uses non-root user (appuser)

---

## 7) Notes for Evaluators

**Service Overview:**
- Language: Python 3.11 + FastAPI
- Endpoints: `/health` (public), `/readings` (protected)
- Auth: Bearer token (default: `local-dev-token`)
- Validation: Temperature -40 to 80°C, device_id ≥3 chars
- Error Format: RFC 7807 Problem Details (application/problem+json)

**Expected Behavior:**
1. Service is stateless (in-memory READINGS list)
2. Each POST request generates a unique reading_id
3. All errors include proper HTTP status + ProblemDetails
4. HEALTHCHECK calls `/health` every 30 seconds

**Boundary Test Results:**
- `-40.0°C` → ✅ Accepted (inclusive lower bound)
- `80.0°C` → ✅ Accepted (inclusive upper bound)
- `-40.1°C` → ❌ Rejected 422
- `80.1°C` → ❌ Rejected 422

---

**Submission Date:** 2026-05-28  
**Group:** nhom_8 (FIT4110 Lab 04)  
**Status:** Ready for review ✅
