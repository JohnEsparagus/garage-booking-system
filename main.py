import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from db import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once when the server starts
    yield


app = FastAPI(title="Garage Booking", lifespan=lifespan)


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/garages/{garage_id}/slots")
def get_free_slots(garage_id: int, date: datetime.date):
    conn = get_connection()
    garage = conn.execute(
        "SELECT * FROM garages WHERE id = ?", (garage_id,)
    ).fetchone()

    if garage is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Garage not found")

    rows = conn.execute(
        "SELECT time FROM bookings WHERE garage_id = ? AND date = ?",
        (garage_id, date.isoformat()),
    ).fetchall()
    conn.close()

    taken = {row["time"] for row in rows}
    all_slots = [
        f"{hour:02d}:00" for hour in range(garage["opens_at"], garage["closes_at"])
    ]
    free_slots = [slot for slot in all_slots if slot not in taken]

    return {"garage_id": garage_id, "date": date, "free_slots": free_slots}
