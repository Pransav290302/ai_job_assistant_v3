from fastapi import APIRouter

from api.limiter import limiter

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
@router.get("/api/health")
@limiter.exempt
def health_check():
    """Root, /health, and /api/health for Render/load balancer probes."""
    return {"status": "online", "service": "ai-job-assistant"}
