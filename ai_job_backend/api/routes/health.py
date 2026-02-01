from fastapi import APIRouter

from api.limiter import limiter

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
@limiter.exempt
def health_check():
    """Root and /health for Render/load balancer probes."""
    return {"status": "online", "service": "ai-job-assistant"}
