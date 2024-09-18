from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get(
    "/healthz", tags=["Monitoring"], description="Health check endpoint", status_code=status.HTTP_204_NO_CONTENT
)
async def healthz():
    """Checks the condition of the server, check that the server is running."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)
