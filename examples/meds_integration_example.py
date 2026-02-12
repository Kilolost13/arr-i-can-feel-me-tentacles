"""
Example: Meds Service Integration
Shows how to add KiloNerve to track medication events
"""
from fastapi import FastAPI
from kilo_integration import KiloNerve

app = FastAPI(title="Kilo Meds Service")
kilo_nerve = KiloNerve("meds")

@app.post("/add")
async def add_med(med: Med):
    with Session(engine) as session:
        session.add(med)
        session.commit()
        session.refresh(med)
        
        # KILO INTEGRATION - Notify brain of new med
        await kilo_nerve.send_observation(
            content=f"New medication added: {med.name} ({med.dosage}) - {med.schedule}",
            priority="normal",
            metadata={
                "med_id": med.id,
                "med_name": med.name,
                "dosage": med.dosage,
                "schedule": med.schedule,
                "times": med.times
            }
        )
        
        # Real-time event for UI
        await kilo_nerve.emit_event(
            "med_added",
            {"med_name": med.name, "dosage": med.dosage}
        )
        
        return {"med": med}

@app.post("/take/{med_id}")
async def take_med(med_id: int):
    med = record_taken(engine, med_id)
    
    # KILO INTEGRATION - Track med being taken
    await kilo_nerve.send_observation(
        content=f"User took {med.name} ({med.dosage})",
        priority="normal",
        metadata={
            "med_id": med.id,
            "med_name": med.name,
            "dosage": med.dosage,
            "time_taken": datetime.now().isoformat()
        }
    )
    
    await kilo_nerve.emit_event(
        "med_taken",
        {"med_name": med.name, "dosage": med.dosage}
    )
    
    return {"med": med}

@app.delete("/{med_id}")
async def delete_med(med_id: int):
    with Session(engine) as session:
        med = session.get(Med, med_id)
        med_name = med.name
        session.delete(med)
        session.commit()
        
        # KILO INTEGRATION - Alert on deletion
        await kilo_nerve.alert_kilo(
            alert_type="health",
            message=f"Medication deleted: {med_name}",
            severity="info"
        )
        
        return {"message": f"{med_name} deleted"}
