# Background Job System - Phase 6B Implementation

**Implementation Date**: January 2025
**Status**: ✅ **COMPLETE**
**Project**: Habeas Emergency Notification System

---

## 🎯 **Overview**

The background job system provides automated scheduling infrastructure for emergency notifications using **Celery** with **Redis** as the message broker. This system ensures reliable delivery of time-sensitive notifications to attorneys without blocking the main application.

## 🔧 **Architecture**

### **Core Components**

1. **Celery App** (`app/celery_app.py`)
   - Celery application configuration
   - Task routing and queue management
   - Beat schedule for periodic tasks
   - Database session handling

2. **Background Tasks** (`app/tasks.py`)
   - `send_escalated_notifications` - 1-hour follow-up notifications
   - `send_daily_digest` - Daily attorney digest
   - `schedule_escalated_notification` - Case-specific scheduling
   - `health_check` - Worker health monitoring

3. **Redis Message Broker**
   - Task queue management
   - Result storage
   - High availability and persistence

4. **Docker Services**
   - `celery-worker` - Task processing
   - `celery-beat` - Task scheduling
   - `celery-flower` - Web-based monitoring
   - `redis` - Message broker and result backend

## 📋 **Task Schedule**

### **Periodic Tasks**

| Task | Schedule | Purpose | Queue |
|------|----------|---------|-------|
| **Escalated Notifications** | Every 15 minutes | Check for cases >1 hour old | `priority` |
| **Daily Digest** | Daily at 8:00 AM UTC | Send attorney case digest | `default` |

### **On-Demand Tasks**

| Task | Trigger | Purpose | Timing |
|------|---------|---------|--------|
| **Case-Specific Escalation** | Emergency case creation | Schedule 1-hour follow-up | 1 hour after case creation |
| **Manual Triggers** | API endpoints | Testing and debugging | Immediate |

## 🚀 **Getting Started**

### **Development Setup**

1. **Install Dependencies**
   ```bash
   cd apps/backend
   uv sync
   ```

2. **Start Redis**
   ```bash
   docker-compose up redis -d
   ```

3. **Start Celery Worker**
   ```bash
   python run_celery_worker.py
   # Or using Docker:
   docker-compose up celery-worker -d
   ```

4. **Start Celery Beat Scheduler**
   ```bash
   python run_celery_beat.py
   # Or using Docker:
   docker-compose up celery-beat -d
   ```

5. **Monitor with Flower (Optional)**
   ```bash
   docker-compose up celery-flower -d
   # Access at http://localhost:5555
   ```

### **Production Setup**

1. **Full Stack with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Configure Redis URLs and notification settings
   - Set appropriate daily digest timing

3. **Monitoring**
   - Flower web interface: `http://localhost:5555`
   - Health check endpoint: `GET /emergency/jobs/health-check`
   - Job statistics: `GET /emergency/jobs/stats`

## 🔗 **API Endpoints**

### **Job Management**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/emergency/jobs/escalated-notifications` | POST | Trigger escalated notifications |
| `/emergency/jobs/daily-digest` | POST | Trigger daily digest |
| `/emergency/jobs/schedule-escalated/{case_id}` | POST | Schedule case-specific escalation |
| `/emergency/jobs/{task_id}/status` | GET | Get job status |
| `/emergency/jobs/health-check` | GET | Check Celery health |
| `/emergency/jobs/stats` | GET | Get job statistics |

### **Example Usage**

```bash
# Manually trigger escalated notifications
curl -X POST http://localhost:8000/emergency/jobs/escalated-notifications

# Schedule escalated notification for case 42 in 2 hours
curl -X POST "http://localhost:8000/emergency/jobs/schedule-escalated/42?delay_hours=2"

# Check job status
curl http://localhost:8000/emergency/jobs/{task_id}/status

# Health check
curl http://localhost:8000/emergency/jobs/health-check
```

## ⚙️ **Configuration**

### **Environment Variables**

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Background Job Configuration
DAILY_DIGEST_HOUR=8                 # UTC hour for daily digest
DAILY_DIGEST_MINUTE=0               # UTC minute for daily digest
ESCALATED_CHECK_INTERVAL=15         # Minutes between escalated checks
MAX_TASK_RETRIES=3                  # Maximum retry attempts
TASK_RETRY_DELAY=300                # Seconds to wait between retries
```

### **Docker Compose Services**

```yaml
# Redis with persistence
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data

# Celery Worker
celery-worker:
  command: celery -A app.celery_app worker --loglevel=info --queues=default,priority
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0

# Celery Beat Scheduler
celery-beat:
  command: celery -A app.celery_app beat --loglevel=info --scheduler=celery.beat:PersistentScheduler
  volumes:
    - celery_beat_data:/app/celerybeat-schedule

# Flower Monitoring
celery-flower:
  command: celery -A app.celery_app flower --port=5555
  ports:
    - "127.0.0.1:5555:5555"
```

## 🔍 **Task Details**

### **Escalated Notifications Task**

**Purpose**: Send 1-hour follow-up notifications for unaccepted emergency cases

**Schedule**: Every 15 minutes
**Queue**: `priority`
**Retry Policy**: 3 attempts with exponential backoff

**Logic**:
1. Find active cases created >1 hour ago
2. Filter cases that haven't been escalated recently
3. Send multi-channel notifications to court-admitted attorneys
4. Update escalation timestamp
5. Return count of attorneys notified

### **Daily Digest Task**

**Purpose**: Send daily summary of unassigned cases to all attorneys

**Schedule**: Daily at 8:00 AM UTC
**Queue**: `default`
**Retry Policy**: 3 attempts with exponential backoff

**Logic**:
1. Get all unassigned emergency cases
2. Get court coverage statistics
3. For each attorney, filter cases for their admitted courts
4. Send personalized digest with relevant cases
5. Return count of attorneys notified

### **Case-Specific Escalation**

**Purpose**: Schedule targeted escalation for individual cases

**Trigger**: Emergency case creation
**Queue**: `priority`
**Delay**: 1 hour (configurable)

**Logic**:
1. Schedule escalated notification task with countdown
2. Task executes after specified delay
3. Sends escalated notification for the specific case
4. Integrates with periodic escalation system

## 📊 **Monitoring & Logging**

### **Health Checks**

1. **Worker Health**: `/emergency/jobs/health-check`
   - Tests task execution with timeout
   - Returns worker status and response time

2. **Queue Statistics**: `/emergency/jobs/stats`
   - Active tasks by worker
   - Scheduled tasks
   - Worker statistics and uptime

3. **Task Status**: `/emergency/jobs/{task_id}/status`
   - Individual task status and results
   - Success/failure tracking
   - Result retrieval

### **Logging**

- **Task Execution**: Comprehensive logging of all task executions
- **Error Handling**: Detailed error logging with retry information
- **Performance**: Task timing and performance metrics
- **Integration**: Notification delivery status and statistics

### **Flower Monitoring**

Access Flower at `http://localhost:5555` for:
- Real-time task monitoring
- Worker status and statistics
- Task history and results
- Queue length and processing rates
- Task routing visualization

## 🛠 **Testing**

### **Unit Tests**

```bash
# Run background job tests
cd apps/backend
python -m pytest tests/unit/test_background_jobs.py -v
```

**Test Coverage**:
- Task execution success/failure scenarios
- Retry logic and error handling
- Task scheduling and timing
- Health checks and monitoring
- Configuration validation

### **Integration Testing**

```bash
# Test with real Redis instance
docker-compose up redis -d
python -m pytest tests/integration/ -k background -v
```

### **Manual Testing**

```bash
# Test escalated notifications
curl -X POST http://localhost:8000/emergency/jobs/escalated-notifications

# Test daily digest
curl -X POST http://localhost:8000/emergency/jobs/daily-digest

# Monitor results in Flower
open http://localhost:5555
```

## 🚨 **Error Handling**

### **Task Retry Logic**

- **Exponential Backoff**: `60 * (2 ** retries)` seconds
- **Maximum Retries**: 3 attempts (configurable)
- **Dead Letter Queue**: Failed tasks logged for manual review

### **Common Issues**

1. **Redis Connection Failed**
   - Check Redis service status
   - Verify connection URLs
   - Check firewall/network settings

2. **Task Timeout**
   - Review task complexity
   - Increase worker timeout settings
   - Check database connection pool

3. **Database Session Issues**
   - Verify database connectivity
   - Check session cleanup in DatabaseTask
   - Monitor connection pool usage

### **Recovery Procedures**

1. **Worker Recovery**
   ```bash
   docker-compose restart celery-worker
   ```

2. **Beat Scheduler Recovery**
   ```bash
   docker-compose restart celery-beat
   ```

3. **Clear Task Queue**
   ```bash
   celery -A app.celery_app purge
   ```

## 📈 **Performance Considerations**

### **Scalability**

- **Horizontal Scaling**: Add more workers with `docker-compose scale celery-worker=3`
- **Queue Separation**: Priority queue for urgent tasks
- **Resource Limits**: Configure memory and CPU limits

### **Optimization**

- **Prefetch Multiplier**: Set to 1 for memory optimization
- **Max Tasks Per Child**: 1000 tasks before worker restart
- **Connection Pooling**: Redis connection keep-alive settings

### **Monitoring Metrics**

- Task execution time
- Queue length
- Worker utilization
- Error rates
- Notification success rates

## 📚 **Integration Points**

### **Emergency Service Integration**

- **Case Creation**: Automatic escalation scheduling
- **Status Updates**: Task result integration
- **Notification Service**: Multi-channel delivery

### **API Integration**

- **Manual Triggers**: REST endpoints for testing
- **Status Monitoring**: Real-time job status
- **Statistics**: Performance and health metrics

### **Database Integration**

- **Session Management**: Automatic session handling
- **Transaction Safety**: Proper commit/rollback
- **Connection Pooling**: Shared database connections

---

## ✅ **Implementation Status**

- [x] **Celery Configuration**: App setup with Redis broker
- [x] **Background Tasks**: All notification tasks implemented
- [x] **Task Scheduling**: Beat scheduler with periodic tasks
- [x] **Docker Integration**: Complete service orchestration
- [x] **API Endpoints**: Job management and monitoring
- [x] **Error Handling**: Retry logic and failure recovery
- [x] **Testing**: Comprehensive unit test coverage
- [x] **Documentation**: Complete implementation guide
- [x] **Health Monitoring**: Worker health checks and statistics
- [x] **Integration**: Emergency service integration

**Phase 6B: Background Job System** - ✅ **COMPLETE**

**Next Phase**: Phase 6C - UX/UI Enhancements
