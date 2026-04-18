# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
- API key hardcode
- Port cố định
- Debug mode
- Không có health check
- Không xử lý shutdown

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcode | Env vars | Tập trung quản lý config một chỗ, dễ dàng chỉnh sửa, không bị lộ thông tin trong code |
| Health check | Không có | Có | Các platform thường có cơ chế kiểm tra định kỳ qua healthcheck, sớm phát hiện và restart khi app sập |
| Logging | print() | JSON | Log cần phân level và có cấu trúc để dễ theo dõi và debug |
| Shutdown | Đột ngột | Graceful | Trước khi shutdown cần chờ request hiện tại hoàn thành, và cần có một thông báo để cung cấp thông tin cho việc maintain |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image là gì?

   Base image là image gốc mà Dockerfile bắt đầu từ đó — mọi layer tiếp theo được xây dựng trên nền này. Nó được chỉ định bằng lệnh `FROM`.

   Cụ thể: **`python:3.11`** — full Python distribution (~1 GB), bao gồm toàn bộ Python runtime và standard library.

2. Working directory là gì?

   Working directory là thư mục làm việc mặc định bên trong container, được đặt bằng lệnh `WORKDIR`. Mọi lệnh `RUN`, `COPY`, `ADD`, `CMD`, `ENTRYPOINT` sau đó đều được thực thi tương đối với thư mục này.

   Cụ thể: **`/app`** — tất cả lệnh tiếp theo (`COPY`, `RUN`, `CMD`) đều chạy trong thư mục này bên trong container.

3. Tại sao COPY requirements.txt trước?

   Docker build cache hoạt động theo từng layer: nếu một layer không thay đổi, Docker tái sử dụng cache thay vì build lại từ đầu. Vì vậy, nên COPY những file ít thay đổi trước để tối ưu tốc độ build.

   **Docker layer cache**: mỗi `RUN`/`COPY` tạo một layer riêng. Nếu `requirements.txt` không thay đổi, Docker tái sử dụng layer `pip install` đã cache → build nhanh hơn nhiều. Nếu copy toàn bộ code trước, mỗi lần sửa code sẽ invalidate cache và phải cài lại dependencies từ đầu.

4. CMD vs ENTRYPOINT khác nhau thế nào?

   Cả hai đều chỉ định lệnh chạy khi container start, nhưng khác nhau về mức độ có thể override từ bên ngoài: `ENTRYPOINT` cố định executable, còn `CMD` cung cấp default có thể bị thay thế hoàn toàn.

   - **`ENTRYPOINT`**: định nghĩa executable cố định, luôn chạy khi container start — không bị ghi đè bởi `docker run <args>`.
   - **`CMD`**: cung cấp lệnh/arguments mặc định, **có thể bị ghi đè** hoàn toàn khi truyền lệnh vào `docker run`. Ví dụ: `CMD ["python", "app.py"]` sẽ bị thay thế nếu chạy `docker run image bash`.
   - Kết hợp cả hai: `ENTRYPOINT` làm executable, `CMD` làm default arguments — cho phép override arguments mà không thay executable.

### Exercise 2.3: Image size comparison
- Develop: 1.15 GB
- Production: 160 MB
- Difference: 86.1%%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: agent-2a202600333-production.up.railway.app
- Screenshot: ([Screenshot](./screenshot.png))

## Part 4: API Security


### Exercise 4.1-4.3: Test results
- Không có key
```bash
PS D:\> Invoke-RestMethod `
>>   -Uri "http://localhost:8000/ask" `
>>   -Method POST `
>>   -ContentType "application/json" `
>>   -Body '{"question": "Hello"}'
Invoke-RestMethod : {"detail":"Missing API key. Include header: X-API-Key: "}
At line:1 char:1
+ Invoke-RestMethod `
+ ~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-RestMethod], WebExc
   eption
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand
```

- Có key
```bash
PS D:\> Invoke-RestMethod `
>>   -Uri "http://localhost:8000/ask" `
>>   -Method POST `
>>   -Headers @{ "X-API-Key" = "my-secret-key" } `
>>   -ContentType "application/json" `
>>   -Body '{"question": "Hello"}'

question answer
-------- ------
Hello    ÄÃ¢y lÃ  cÃ¢u tráº£ lá»i tá»« AI agent (mock). Trong production, ÄÃ¢y sáº½ lÃ  response tá»« OpenAI/Anth...
```


### Exercise 4.4: Cost guard implementation
Kiểm tra budget trước khi gọi LLM.
Dùng Redis để track monthly spending — stateless, scale-safe.
Raise 402 nếu vượt budget, trả về True nếu còn budget.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- 5.1: Health checks
```bash
@app.get("/health")
def health():
    redis_ok = False
    if USE_REDIS:
        try:
            _redis.ping()
            redis_ok = True
        except Exception:
            redis_ok = False

    status = "ok" if (not USE_REDIS or redis_ok) else "degraded"

    return {
        "status": status,
        "instance_id": INSTANCE_ID,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "storage": "redis" if USE_REDIS else "in-memory",
        "redis_connected": redis_ok if USE_REDIS else "N/A",
    }
```

- 5.2: Graceful shutdown
```bash
logger.info("🔄 Graceful shutdown initiated...")

    # Chờ request đang xử lý hoàn thành (tối đa 30 giây)
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} in-flight requests...")
        time.sleep(1)
        elapsed += 1

    logger.info("✅ Shutdown complete")
```

- 5.3: Stateless design
```bash
# Tạo hoặc dùng session hiện có
session_id = body.session_id or str(uuid.uuid4())

# Thêm câu hỏi vào history
append_to_history(session_id, "user", body.question)

# Gọi LLM với context (trong mock, ta chỉ dùng câu hỏi hiện tại)
session = load_session(session_id)
history = session.get("history", [])
answer = ask(body.question)

# Lưu response vào history
append_to_history(session_id, "assistant", answer)
```

- 5.4: Load balancing
```bash
agent-3  | {"time":"2026-04-17 16:12:23,881","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-3  | INFO:     172.20.0.6:47270 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 120 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-2  | {"time":"2026-04-17 16:12:24,044","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-2  | INFO:     172.20.0.6:45496 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 120 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-1  | {"time":"2026-04-17 16:12:24,199","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-1  | INFO:     172.20.0.6:43450 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 128 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-3  | {"time":"2026-04-17 16:12:24,353","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 120 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-3  | INFO:     172.20.0.6:47270 - "POST /ask HTTP/1.1" 200 OK
agent-2  | {"time":"2026-04-17 16:12:24,496","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-2  | INFO:     172.20.0.6:45496 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 120 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-1  | {"time":"2026-04-17 16:12:24,643","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-1  | INFO:     172.20.0.6:43450 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 151 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-3  | {"time":"2026-04-17 16:12:24,780","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-3  | INFO:     172.20.0.6:47270 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:24 +0000] "POST /ask HTTP/1.1" 200 128 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-2  | {"time":"2026-04-17 16:12:24,919","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:25 +0000] "POST /ask HTTP/1.1" 200 120 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-2  | INFO:     172.20.0.6:45496 - "POST /ask HTTP/1.1" 200 OK
agent-1  | {"time":"2026-04-17 16:12:25,044","level":"INFO","msg":"{"event": "request", "q_len": 9}"}
agent-1  | INFO:     172.20.0.6:43450 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:25 +0000] "POST /ask HTTP/1.1" 200 151 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
agent-3  | {"time":"2026-04-17 16:12:25,175","level":"INFO","msg":"{"event": "request", "q_len": 10}"}
agent-3  | INFO:     172.20.0.6:47270 - "POST /ask HTTP/1.1" 200 OK
nginx-1  | 172.20.0.1 - - [17/Apr/2026:16:12:25 +0000] "POST /ask HTTP/1.1" 200 128 "-" "Mozilla/5.0 (Windows NT; Windows NT 10.0; en-US) WindowsPowerShell/5.1.26100.8115"
```

- 5.5: Test stateless

Chạy 06-lab-complete với 3 replicas, gửi 6 requests qua nginx load-balancer, xác nhận mỗi request đều thành công dù instance nào xử lý. Session history được lưu Redis (stateless) nên bất kỳ instance nào cũng trả kết quả nhất quán.

```bash
# Scale lên 3 agent
PS> cd 06-lab-complete ; docker compose up -d --scale agent=3
[+] Running 5/5
 ✔ Container 06-lab-complete-redis-1  Healthy    0.6s
 ✔ Container 06-lab-complete-agent-1  Running    0.0s
 ✔ Container 06-lab-complete-agent-3  Started    1.2s
 ✔ Container 06-lab-complete-agent-2  Started    0.9s
 ✔ Container 06-lab-complete-nginx-1  Running    0.0s

# Gửi 6 requests liên tiếp — tất cả thành công
PS> 1..6 | ForEach-Object {
  $r = Invoke-RestMethod -Uri http://localhost:8080/ask `
    -Method POST -Body '{"question":"Hello"}' `
    -ContentType "application/json" `
    -Headers @{"X-API-Key"="dev-key-change-me-in-production"}
  "Request $_: served_by=$($r.served_by)"
}
Request 1: served_by=agent-b06db56a
Request 2: served_by=agent-b06db56a
Request 3: served_by=agent-b06db56a
Request 4: served_by=agent-b06db56a
Request 5: served_by=agent-b06db56a
Request 6: served_by=agent-b06db56a

# Requests đều thành công. Tất cả đi qua cùng 1 instance do nginx keepalive
# connection reuse (keepalive 16 trong nginx.conf). Khi dùng nhiều concurrent
# connections (ab, wrk, k6, v.v.) sẽ thấy phân bổ đều giữa 3 instances.
# ✅ Stateless: mỗi request độc lập, không phụ thuộc vào instance cụ thể.
```

Production readiness check:
```bash
PS> python check_production_ready.py

=======================================================
  Production Readiness Check — Day 12 Lab
=======================================================

📁 Required Files
  ✅ Dockerfile exists
  ✅ docker-compose.yml exists
  ✅ .dockerignore exists
  ✅ .env.example exists
  ✅ requirements.txt exists
  ✅ railway.toml or render.yaml exists

🔒 Security
  ✅ .env in .gitignore
  ✅ No hardcoded secrets in code

🌐 API Endpoints (code check)
  ✅ /health endpoint defined
  ✅ /ready endpoint defined
  ✅ Authentication implemented
  ✅ Rate limiting implemented
  ✅ Graceful shutdown (SIGTERM)
  ✅ Structured logging (JSON)

🐳 Docker
  ✅ Multi-stage build
  ✅ Non-root user
  ✅ HEALTHCHECK instruction
  ✅ Slim base image
  ✅ .dockerignore covers .env
  ✅ .dockerignore covers __pycache__

=======================================================
  Result: 20/20 checks passed (100%)
  🎉 PRODUCTION READY! Deploy nào!
=======================================================
```