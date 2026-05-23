from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.inference_log import InferenceLog

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(InferenceLog.id).label("total_requests"),
            func.avg(InferenceLog.latency_ms).label("avg_latency_ms"),
            func.percentile_cont(0.95).within_group(
                InferenceLog.latency_ms.asc()
            ).label("p95_latency_ms"),
            func.sum(InferenceLog.total_tokens).label("total_tokens"),
            func.count(InferenceLog.id).filter(
                InferenceLog.status == "error"
            ).label("error_count"),
        )
    )
    row = result.one()
    total = row.total_requests or 0
    errors = row.error_count or 0
    return {
        "total_requests": total,
        "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
        "p95_latency_ms": round(row.p95_latency_ms or 0, 1),
        "total_tokens": row.total_tokens or 0,
        "error_rate_pct": round((errors / total * 100) if total else 0, 1),
        "error_count": errors,
    }
