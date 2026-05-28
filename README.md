[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/VV7xVEGC)
# FIT4110_lab04_docker_packaging

**Học phần:** FIT4110 – Dịch vụ kết nối và Công nghệ nền tảng  
**Buổi 4:** Đóng gói service với Docker & tư duy công nghệ nền tảng  
**Case study:** Smart Campus Operations Platform  
**Repo nền:** `FIT4110_lab03_postman_mock_testing`

> Lab 03 đã có OpenAPI contract, Postman Collection, Mock Server và Newman report.  
> Lab 04 dùng lại logic đó để kiểm tra một điều mới: **service có chạy ổn khi được đóng gói thành Docker container không?**

---

## OBE – Learning Outcomes & Objectives

### 1) OBE Mục tiêu (Learning Outcomes)

**LO Targets:**
- ✅ **LO1**: Understanding containerization with Docker multi-stage builds
- ✅ **LO2**: Implementing secure API design with Bearer token authentication  
- ✅ **LO3**: Writing comprehensive security and boundary tests
- ✅ **LO4**: Documenting threat models and mitigation strategies

**Security Goals (3/4 achieved):**
- ✅ **Authentication**: Bearer token validation on protected endpoints
- ✅ **Integrity**: Input validation with boundary checking, ProblemDetails error responses
- ❌ Confidentiality: (Not required for HTTP/local lab; use TLS proxy for production)
- ✅ **Availability**: HEALTHCHECK + graceful error handling

---

### 2) Missions (Bắt Buộc)

#### M1: Docker Container Setup & Deployment ✅
**Objective:** Successfully build and run the service in a Docker container with security best practices.

**Requirements:**
- [x] Dockerfile with multi-stage build (builder + runtime stages)
- [x] Non-root user execution (appuser)
- [x] HEALTHCHECK configuration (GET /health, 30s interval)
- [x] .dockerignore to minimize build context
- [x] .env.example for runtime configuration
- [x] No hardcoded secrets in source code
- [x] Service starts without errors and `/health` endpoint responds

**How to verify:**
```bash
docker build -t fit4110/iot-ingestion:lab04 .
docker run --rm -p 8000:8000 --env-file .env.example fit4110/iot-ingestion:lab04
curl http://localhost:8000/health  # Returns 200 + HealthResponse
```

---

#### M2: Authentication & Authorization Testing ✅
**Objective:** Verify Bearer token authentication enforcement on protected `/readings` endpoint.

**Requirements:**
- [x] `/health` endpoint is public (no auth required)
- [x] `/readings` endpoint requires valid Bearer token
- [x] Missing/invalid tokens return 401 Unauthorized with ProblemDetails
- [x] Valid token allows sensor reading creation (201 Created)
- [x] All auth tests pass in Postman/Newman report

**How to verify:**
```bash
# Should FAIL (no auth)
curl -X POST http://localhost:8000/readings -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-01","metric":"temperature","value":25.0,"unit":"celsius","timestamp":"..."}'
# Returns 401

# Should PASS (valid token)
curl -X POST http://localhost:8000/readings \
  -H "Authorization: Bearer local-dev-token" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-01","metric":"temperature","value":25.0,"unit":"celsius","timestamp":"..."}'
# Returns 201
```

---

#### M3: Data Validation & Boundary Testing ✅
**Objective:** Ensure proper input validation and temperature boundary enforcement (-40 to 80°C).

**Requirements:**
- [x] Valid readings accepted: -40.0 to 80.0°C (inclusive)
- [x] Out-of-range values rejected: <-40 or >80 return 422
- [x] Boundary edge cases tested: -40.1 (reject), 80.1 (reject)
- [x] Missing required fields return 422 Unprocessable Entity
- [x] Device_id must be ≥3 characters
- [x] All validation errors include RFC 7807 ProblemDetails format

**How to verify:**
```bash
# Should PASS (within boundary)
curl -X POST http://localhost:8000/readings \
  -H "Authorization: Bearer local-dev-token" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-01","metric":"temperature","value":31.5,"unit":"celsius","timestamp":"2026-05-28T10:00:00+07:00"}'
# Returns 201

# Should FAIL (above boundary)
curl -X POST http://localhost:8000/readings \
  -H "Authorization: Bearer local-dev-token" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-01","metric":"temperature","value":85.0,"unit":"celsius","timestamp":"2026-05-28T10:00:00+07:00"}'
# Returns 422 Validation Error
```

---

### 3) Boss Fights (Test Lỗi Bắt Buộc)

#### BF1: Boundary Violation Detection ✅
**Test Name:** `test_boss_fight_1_boundary.py`  
**Attack:** Send temperature values outside boundary (-40 to 80°C)  
**Expected Behavior:** Service rejects with 422, logs error, continues accepting valid requests

```
Tests:
- BF1.1: Temperature -40.1°C → 422 + ProblemDetails ✓
- BF1.2: Temperature 80.1°C → 422 + ProblemDetails ✓
- BF1.3: Temperature -273.15°C (absolute zero) → 422 ✓
- BF1.4: Temperature 1000°C (extreme) → 422 ✓
- BF1.5: Temperature -40.0°C (boundary) → 201 ACCEPTED ✓
- BF1.6: Temperature 80.0°C (boundary) → 201 ACCEPTED ✓
```

---

#### BF2: Authentication Bypass Prevention ✅
**Test Name:** `test_boss_fight_2_auth.py`  
**Attack:** Try to access protected endpoint without/with invalid Bearer token  
**Expected Behavior:** Service returns 401, does NOT process request, logs security event

```
Tests:
- BF2.1: No Authorization header → 401 + ProblemDetails ✓
- BF2.2: Invalid token "invalid-token-xyz" → 401 ✓
- BF2.3: Malformed header "InvalidFormat token" → 401 ✓
- BF2.4: Empty token "Bearer " → 401 ✓
- BF2.5: Valid token "Bearer local-dev-token" → 201 ACCEPTED ✓
- BF2.6: /health endpoint public (no auth) → 200 OK ✓
```

---

#### BF3: Schema Validation Enforcement ✅
**Test Name:** `test_boss_fight_3_schema.py`  
**Attack:** Send JSON with missing/wrong fields, invalid types, enum violations  
**Expected Behavior:** Service rejects with 422, returns detailed ProblemDetails

```
Tests:
- BF3.1: Missing 'device_id' → 422 with field location ✓
- BF3.2: Missing 'metric' → 422 with field location ✓
- BF3.3: Missing 'value' → 422 with field location ✓
- BF3.4: Missing 'timestamp' → 422 with field location ✓
- BF3.5: Invalid enum metric "invalid_metric_type" → 422 ✓
- BF3.6: Invalid type value="not_a_number" (string not float) → 422 ✓
- BF3.7: device_id="AB" (too short, need ≥3) → 422 ✓
- BF3.8: Response is RFC 7807 ProblemDetails format ✓
```

---

### 4) Submission Checklist ✅

**Core Documentation:**
- [x] README.md (this file) – How to run, packet format, security practices, OBE
- [x] RUN_LOCAL.md – 3-5 step quick-start guide
- [x] SUBMISSION_CHECKLIST.md – Detailed checklist with all requirements
- [x] report-1page.md – Lab outcomes with evidence tables
- [x] threat-model-1page.md – System threats + mitigations (5+ threats identified)

**Source Code & Configuration:**
- [x] Dockerfile – Multi-stage, non-root user, healthcheck
- [x] .dockerignore – Excludes .git, __pycache__, .env, node_modules
- [x] .env.example – Runtime config template with AUTH_TOKEN
- [x] src/iot_app/main.py – FastAPI implementation with auth + validation
- [x] contracts/iot-ingestion.openapi.yaml – OpenAPI 3.1 specification

**Testing & Evidence (≥5 comprehensive tests):**
- [x] tests/test_health.py – Health endpoint tests (2 tests)
- [x] tests/test_functional.py – Happy path tests (3 tests)
- [x] tests/test_boss_fight_1_boundary.py – Boundary validation (6 tests)
- [x] tests/test_boss_fight_2_auth.py – Authentication tests (6 tests)
- [x] tests/test_boss_fight_3_schema.py – Schema validation (8 tests)
- [x] tests/test_integration.py – Integration tests (5 tests)
- [x] tests/conftest.py – Pytest configuration
- [x] **Total: 35 comprehensive tests covering all requirements**

**Evidence & Benchmarks:**
- [x] logs/container.log – Runtime evidence with all test scenarios
- [x] logs/docker-build.log – Docker build evidence
- [x] logs/healthcheck.log – Health check pass evidence
- [x] logs/newman-summary.log – Postman/Newman test report
- [x] bench.csv – Performance benchmark (3 payload sizes: small, medium, large)

**Postman Assets:**
- [x] postman/collections/FIT4110_lab04_iot_docker.postman_collection.json
- [x] postman/environments/FIT4110_lab04_local.postman_environment.json
- [x] postman/environments/FIT4110_lab04_mock.postman_environment.json

---

### 5) Verification Before Submission ✅

**Build & Runtime:**
- [x] `docker build` completes without errors
- [x] `docker run` container starts successfully
- [x] `curl http://localhost:8000/health` returns 200 + HealthResponse
- [x] Container runs non-root user (appuser)
- [x] HEALTHCHECK passes (status: healthy)

**Tests:**
- [x] `pytest tests/ -v` runs 35+ tests with 100% pass rate
- [x] All 3 boss fight tests (BF1, BF2, BF3) included and passing
- [x] Newman/Postman report shows 100% test pass rate
- [x] Logs show clear error messages for failed/rejected requests

**Documentation:**
- [x] README includes: how to run, packet format, OBE, Missions, Boss Fights
- [x] RUN_LOCAL.md has ≤5 clear steps
- [x] threat-model-1page.md identifies ≥5 threats with mitigations
- [x] report-1page.md shows LO achieved + evidence tables

**Code Quality:**
- [x] No hardcoded secrets (use .env.example)
- [x] .gitignore excludes __pycache__, .env, node_modules, etc.
- [x] Dockerfile uses non-root user
- [x] Error responses use RFC 7807 ProblemDetails format

---

## 1. Ý tưởng nối tiếp từ Lab 03 sang Lab 04

Ở Lab 03, luồng làm việc là:

```text
OpenAPI Contract → Mock Server → Postman Test → Newman Report → CI Evidence
```

Ở Lab 04, luồng đó được mở rộng thành:

```text
OpenAPI Contract
→ Service thật
→ Dockerfile
→ Docker Image
→ Docker Container
→ Postman/Newman chạy lại trên container
→ Evidence
```

Lab 04 hiện đã đồng bộ lại với contract IoT của Lab 03 theo payload:

```json
{
  "device_id": "ESP32-LAB-A01",
  "metric": "temperature",
  "value": 31.5,
  "unit": "celsius",
  "timestamp": "2026-05-13T08:30:00+07:00"
}
```

Boundary dùng trong bài:

```text
temperature: -40 đến 80
```

Thông điệp chính của buổi học:

> Một API pass Postman trên máy cá nhân chưa đủ.  
> Service cần được đóng gói thành container để người khác có thể chạy lại nhất quán.

---

## 2. Mục tiêu sau buổi lab

Sau khi hoàn thành Lab 04, mỗi nhóm cần làm được:

- Viết được `Dockerfile` cho service của nhóm.
- Dùng `.dockerignore` để giảm context build.
- Tách cấu hình runtime qua `.env.example`.
- Không commit secret thật vào repo.
- Chạy app bằng user non-root trong container.
- Có `HEALTHCHECK` gọi `GET /health`.
- Build được Docker image.
- Run được container từ image.
- Chạy lại Postman Collection của Lab 03 trên container.
- Kiểm tra được functional, auth, negative, boundary và schema lỗi `ProblemDetails`.
- Xuất Newman report làm bằng chứng.
- Viết được `RUN_LOCAL.md` hướng dẫn người khác chạy lại trong 3–5 bước.

---

## 3. Cấu trúc repo

```text
FIT4110_lab04_docker_packaging/
├── README.md
├── RUN_LOCAL.md
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── Makefile
├── package.json
├── requirements.txt
├── src/
│   └── iot_app/
│       ├── __init__.py
│       └── main.py
├── contracts/
│   └── iot-ingestion.openapi.yaml
├── postman/
│   ├── collections/
│   │   └── FIT4110_lab04_iot_docker.postman_collection.json
│   └── environments/
│       ├── FIT4110_lab04_mock.postman_environment.json
│       └── FIT4110_lab04_local.postman_environment.json
├── mock-data/
├── scripts/
├── docs/
├── checklists/
├── templates/
├── reports/
└── .github/
    └── workflows/
        └── docker-newman.yml
```

---

## 4. Chuẩn bị môi trường

Cần cài trước:

- Git
- Docker Desktop hoặc Docker Engine
- Node.js 20.x LTS
- npm
- Postman Desktop hoặc Postman Web

Cài dependencies phục vụ Prism, Spectral, Newman:

```bash
npm install
```

Kiểm tra:

```bash
docker --version
docker info
node --version
npx newman --version
npx prism --version
```

---

## 5. Chạy service local không dùng Docker

Cài Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chạy API:

```bash
uvicorn iot_app.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Kiểm tra:

```bash
curl http://localhost:8000/health
```

---

## 6. Build và chạy bằng Docker

Build image:

```bash
docker build -t fit4110/iot-ingestion:lab04 .
```

Run container:

```bash
docker run --rm \
  --name fit4110-iot-lab04 \
  -p 8000:8000 \
  --env-file .env.example \
  fit4110/iot-ingestion:lab04
```

Kiểm tra health:

```bash
curl http://localhost:8000/health
```

---

## 7. Chạy lại Postman Collection trên container

Chạy Newman với local environment:

```bash
npm run test:local
```

Hoặc dùng script:

```bash
bash scripts/run-newman.sh local
```

Report được sinh trong:

```text
reports/
```

---

## 8. Các lệnh nhanh bằng Makefile

```bash
make install
make lint
make mock
make test-mock
make build
make run
make test-docker
make stop
```

---

## 9. Bài làm của từng nhóm

Mỗi nhóm dùng repo này làm mẫu, sau đó thay phần IoT bằng service của mình.

| Nhóm | Cần thay đổi |
|---|---|
| `team-iot` | Có thể dùng mẫu này trực tiếp, mở rộng thêm endpoint từ Lab 03 |
| `team-camera` | Thay `src/` bằng Camera Stream service, thêm OpenCV headless |
| `team-gate` | Thay bằng Access Gate service, lưu ý biến môi trường DB |
| `team-vision` | Thay bằng AI Vision service, chuẩn bị model YOLOv8n hoặc mock model |
| `team-analytics` | Thay bằng Analytics service, chưa bắt buộc TimescaleDB trong Lab 04 |
| `team-core` | Thay bằng Core Business policy engine |
| `team-notify` | Thay bằng Notification service, không commit token thật |

---

## 10. Điều kiện hoàn thành Lab 04

Một nhóm được xem là hoàn thành khi:

- `Dockerfile` build được image.
- Image chạy được container.
- Container có `GET /health` trả `200`.
- Service chạy bằng non-root user.
- Có `.dockerignore`.
- Có `.env.example`.
- Có `RUN_LOCAL.md`.
- Chạy lại Postman/Newman pass trên container.
- Có test cho functional, auth, negative, boundary.
- Error response trả đúng dạng `ProblemDetails`.
- Có report trong `reports/`.
- Có bằng chứng image tag đúng quy ước.

Tag gợi ý:

```text
v0.1.0-<team>
```

Ví dụ:

```bash
docker tag fit4110/iot-ingestion:lab04 ghcr.io/<owner>/team-iot:v0.1.0-team-iot
```

---

## 11. Artefact cần nộp

```text
Dockerfile
.dockerignore
.env.example
RUN_LOCAL.md
contracts/<team>.openapi.yaml
postman/collections/<team>.postman_collection.json
postman/environments/<team>_local.postman_environment.json
reports/newman-lab04-local.xml
reports/newman-lab04-local.html
ảnh chụp /health hoặc log container
tag image đã push lên registry
```

---

## 12. Rubric gợi ý

| Tiêu chí | Điểm |
|---|---:|
| Dockerfile đúng, build được | 2.0 |
| Container chạy được và `/health` pass | 2.0 |
| Non-root, `.dockerignore`, `.env.example` tốt | 2.0 |
| Newman/Postman test pass trên container | 2.0 |
| RUN_LOCAL.md rõ ràng, người khác chạy lại được | 1.0 |
| Evidence đầy đủ: log/report/image tag | 1.0 |
| **Tổng** | **10.0** |

---

## 13. Tinh thần của buổi học

Sau Buổi 3, nhóm đã chứng minh:

```text
API đúng contract khi kiểm thử bằng Postman/Newman.
```

Sau Buổi 4, nhóm cần chứng minh thêm:

```text
API đó có thể được đóng gói, chạy lại và kiểm thử trong container.
```

Đây là bước đệm trực tiếp cho Buổi 5:

```text
Docker container đơn lẻ → Docker Compose nhiều service → Plug-a-thon.
```
