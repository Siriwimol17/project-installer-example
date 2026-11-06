"""HTTP endpoints for py-svc."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.analyzer import MAX_TEXT_LENGTH, analyze_text
from app.security import require_internal_token

router = APIRouter()


class AnalyzeRequest(BaseModel):
    text: str


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok", "service": request.app.state.settings.service_name}


@router.post("/shutdown", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(require_internal_token)])
async def shutdown(request: Request) -> Response:
    server = getattr(request.app.state, "server", None)
    if server is not None:
        server.should_exit = True
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/analyze", dependencies=[Depends(require_internal_token)])
async def analyze(payload: AnalyzeRequest) -> dict[str, object]:
    if len(payload.text) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="text exceeds 100000 characters")
    if not payload.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="text must not be empty")
    return analyze_text(payload.text)
