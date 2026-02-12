# 🔧 Kilo Integration Guide

**How to wire a new tentacle into Kilo's nervous system**

---

## Quick Start (5 Minutes)

### 1. Copy the Integration Module

```bash
cp kilo_integration.py /path/to/your/service/directory/
```

### 2. Update Your Service

```python
# Add imports at the top
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from kilo_integration import KiloNerve

# Initialize after creating FastAPI app
app = FastAPI(title="Your Service")
kilo_nerve = KiloNerve("your_service_name")

# Make endpoints async and add observations
@app.post("/action")
async def do_action(data: Model):
    # Your existing code
    result = process_data(data)

    # Add observation (new code)
    await kilo_nerve.send_observation(
        content=f"Action completed: {data.description}",
        priority="normal",
        metadata={"action_id": result.id}
    )

    return result
```

### 3. Restart and Test

```bash
kubectl rollout restart deployment/your-service -n kilo-guardian

# Check Kilo's brain
kubectl logs -l app=kilo-ai-brain -n kilo-guardian --tail=50 | grep "Action completed"
```

---

## When to Send Observations

### Always Send When:
- ✅ User performs an action (create, update, delete)
- ✅ Important state changes occur
- ✅ Scheduled tasks complete
- ✅ Errors or issues arise

### Don't Send For:
- ❌ Health check pings
- ❌ Read-only operations (GET requests)
- ❌ Background polling
- ❌ Routine internal processes

---

## Priority Levels

```python
# Low - Informational, not time-sensitive
await kilo_nerve.send_observation("Service started", priority="low")

# Normal - Standard operations (DEFAULT)
await kilo_nerve.send_observation("User added transaction", priority="normal")

# High - Important events
await kilo_nerve.send_observation("Budget exceeded!", priority="high")

# Urgent - Requires immediate attention
await kilo_nerve.send_observation("Critical error in payment processing", priority="urgent")
```

---

## Observation Types

### Event Observation
Simple notification of what happened:

```python
await kilo_nerve.send_observation(
    content="User completed workout habit",
    priority="normal",
    metadata={
        "habit_id": 5,
        "habit_name": "Morning Exercise",
        "streak_days": 7
    }
)
```

### Real-time Event
For immediate UI updates:

```python
await kilo_nerve.emit_event(
    "habit_completed",
    {
        "habit_name": "Morning Exercise",
        "timestamp": datetime.now().isoformat()
    }
)
```

### Alert
For issues requiring attention:

```python
await kilo_nerve.alert_kilo(
    alert_type="health",
    message="User missed 3 medications today",
    severity="warning",
    actionable=True
)
```

---

## Complete Integration Examples

### Example 1: Simple CRUD Service

```python
from fastapi import FastAPI
from kilo_integration import KiloNerve

app = FastAPI(title="Tasks Service")
kilo_nerve = KiloNerve("tasks")

@app.post("/tasks")
async def create_task(task: Task):
    # Save to database
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    # Notify Kilo
    await kilo_nerve.send_observation(
        content=f"Task created: {task.title}",
        priority="normal",
        metadata={"task_id": task.id, "due_date": task.due_date}
    )

    await kilo_nerve.emit_event("task_created", {
        "task_id": task.id,
        "title": task.title
    })

    return {"task": task}

@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    # Mark complete
    with Session(engine) as session:
        task = session.get(Task, task_id)
        task.completed = True
        session.commit()

    # Celebrate with Kilo
    await kilo_nerve.send_observation(
        content=f"Task completed: {task.title}",
        priority="normal",
        metadata={"task_id": task_id, "completed_at": datetime.now().isoformat()}
    )

    return {"status": "completed"}
```

### Example 2: Processing Service

```python
@app.post("/process")
async def process_file(file: UploadFile):
    try:
        # Process the file
        result = await process_upload(file)

        # Success observation
        await kilo_nerve.send_observation(
            content=f"Processed file: {file.filename} ({result.size} bytes)",
            priority="low",
            metadata={
                "filename": file.filename,
                "processing_time": result.duration,
                "records_processed": result.count
            }
        )

        return {"result": result}

    except Exception as e:
        # Error alert
        await kilo_nerve.alert_kilo(
            alert_type="system",
            message=f"File processing failed: {file.filename}",
            severity="error",
            actionable=True
        )
        raise
```

### Example 3: Scheduled Task

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

async def daily_summary():
    """Runs every day at 8 AM"""
    # Generate summary
    summary = await calculate_daily_summary()

    # Send to Kilo
    await kilo_nerve.send_observation(
        content=f"Daily summary: {summary.total_items} items processed",
        priority="normal",
        metadata=summary.dict()
    )

    await kilo_nerve.emit_event("daily_summary_ready", summary.dict())

# Schedule it
scheduler.add_job(daily_summary, 'cron', hour=8)
scheduler.start()
```

---

## Testing Your Integration

### 1. Local Test (from service pod)

```bash
kubectl exec -n kilo-guardian your-service-pod -- python3 << EOF
import asyncio
from kilo_integration import KiloNerve

async def test():
    nerve = KiloNerve('test')
    result = await nerve.send_observation('Test message', 'normal')
    print(f'Result: {result}')

asyncio.run(test())
EOF
```

### 2. Check AI Brain Logs

```bash
kubectl logs -l app=kilo-ai-brain -n kilo-guardian --tail=100 | grep "Test message"
```

Expected output:
```
🧠 [DEBUG] Analyze function called for: Test message
INFO: 10.42.0.xxx:xxxxx - "POST /observations HTTP/1.1" 200 OK
```

### 3. End-to-End Test

```bash
# Trigger your service endpoint
curl -X POST http://your-service:port/action -d '{"test": "data"}'

# Watch Kilo's brain in real-time
kubectl logs -l app=kilo-ai-brain -n kilo-guardian -f
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'kilo_integration'"

**Problem**: Python can't find kilo_integration.py

**Solutions**:
```python
# Option 1: Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Option 2: Use absolute path (for services in /app)
sys.path.insert(0, "/app/services")

# Option 3: Copy kilo_integration.py to service directory
cp kilo_integration.py /path/to/service/
```

### "Failed to send observation: 404"

**Problem**: AI_BRAIN_URL environment variable pointing to wrong path

**Check current value**:
```bash
kubectl exec -n kilo-guardian your-pod -- env | grep AI_BRAIN_URL
```

**Should be**: `http://kilo-ai-brain:9004`
**Not**: `http://kilo-ai-brain:9004/ingest/something`

**Fix**:
```bash
# Remove explicit env var from deployment
kubectl patch deployment your-service -n kilo-guardian --type=json \
  -p='[{"op": "remove", "path": "/spec/template/spec/containers/0/env/X"}]'
```

### "RuntimeWarning: coroutine was never awaited"

**Problem**: Forgot to make endpoint async or use await

**Fix**:
```python
# Before (wrong)
@app.post("/action")
def do_action():
    kilo_nerve.send_observation(...)  # Missing await!

# After (correct)
@app.post("/action")
async def do_action():
    await kilo_nerve.send_observation(...)
```

---

## Best Practices

### 1. Be Specific in Content

```python
# Bad - Too vague
await kilo_nerve.send_observation("Update completed")

# Good - Descriptive
await kilo_nerve.send_observation("User updated email to john@example.com")
```

### 2. Include Useful Metadata

```python
# Good metadata example
await kilo_nerve.send_observation(
    content="Purchase completed",
    priority="normal",
    metadata={
        "order_id": 12345,
        "amount": 49.99,
        "items": 3,
        "payment_method": "credit_card",
        "shipping_address": "truncated...",
        "estimated_delivery": "2026-02-15"
    }
)
```

### 3. Use Appropriate Event Types

```python
# For database operations - send observation
await kilo_nerve.send_observation("Record created")

# For UI updates - emit event
await kilo_nerve.emit_event("record_created", {...})

# For problems - send alert
await kilo_nerve.alert_kilo("system", "Database connection lost", "error")
```

### 4. Handle Errors Gracefully

```python
try:
    await kilo_nerve.send_observation(...)
except Exception as e:
    # Log error but don't crash the service
    logger.error(f"Failed to send observation: {e}")
    # Service continues working even if observation fails
```

---

## Advanced: Custom Integration Patterns

### Pattern 1: Batch Observations

```python
async def process_batch(items):
    results = []
    for item in items:
        result = await process_item(item)
        results.append(result)

    # Send single observation for entire batch
    await kilo_nerve.send_observation(
        content=f"Batch processed: {len(results)} items",
        priority="low",
        metadata={
            "total_items": len(results),
            "success_count": sum(1 for r in results if r.success),
            "error_count": sum(1 for r in results if not r.success)
        }
    )
```

### Pattern 2: Threshold Alerts

```python
async def check_usage():
    usage = await get_current_usage()

    if usage.percentage > 90:
        await kilo_nerve.alert_kilo(
            alert_type="system",
            message=f"Disk usage at {usage.percentage}%",
            severity="critical",
            actionable=True
        )
    elif usage.percentage > 75:
        await kilo_nerve.send_observation(
            content=f"Disk usage at {usage.percentage}%",
            priority="high"
        )
```

### Pattern 3: State Change Tracking

```python
@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    old_status = order.status
    order.status = status

    # Track state transitions
    await kilo_nerve.send_observation(
        content=f"Order {order_id}: {old_status} → {status}",
        priority="normal",
        metadata={
            "order_id": order_id,
            "old_status": old_status,
            "new_status": status,
            "changed_by": current_user.id
        }
    )
```

---

## Checklist for New Integration

- [ ] Import KiloNerve module
- [ ] Initialize kilo_nerve instance
- [ ] Make key endpoints async
- [ ] Add observations to create/update/delete operations
- [ ] Add metadata for context
- [ ] Test observation flow
- [ ] Check AI Brain logs
- [ ] Verify real-time events (if using emit_event)
- [ ] Document service-specific events
- [ ] Update service README

---

**Questions? Issues? The octopus is here to help!** 🐙
