import logging
from fastapi import APIRouter, Request
from fastapi.responses import Response
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/remote", tags=["remote-proxy"])

ARXIV_API_BASE = "https://export.arxiv.org"


@router.api_route("/api/query", methods=["GET", "POST"])
async def proxy_arxiv_query(request: Request):
    """
    Proxy requests to arXiv API.
    
    This endpoint forwards requests to https://export.arxiv.org/api/query
    to support Electron environment where Vite proxy is not available.
    """
    try:
        query_params = str(request.query_params)
        target_url = f"{ARXIV_API_BASE}/api/query?{query_params}"
        
        logger.info(f"Proxying arXiv request to: {target_url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(target_url)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/xml"
            )
    except httpx.TimeoutException:
        logger.error("arXiv API request timed out")
        return Response(
            content="<error>Request to arXiv API timed out</error>",
            status_code=504,
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error proxying arXiv request: {e}")
        return Response(
            content=f"<error>{str(e)}</error>",
            status_code=500,
            media_type="application/xml"
        )


@router.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy_arxiv_generic(request: Request, path: str):
    """
    Generic proxy for other arXiv API endpoints.
    """
    try:
        query_params = str(request.query_params)
        target_url = f"{ARXIV_API_BASE}/{path}?{query_params}" if query_params else f"{ARXIV_API_BASE}/{path}"
        
        logger.info(f"Proxying arXiv request to: {target_url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            if request.method == "GET":
                response = await client.get(target_url)
            else:
                body = await request.body()
                response = await client.post(target_url, content=body)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/xml")
            )
    except httpx.TimeoutException:
        logger.error("arXiv API request timed out")
        return Response(
            content="<error>Request to arXiv API timed out</error>",
            status_code=504,
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error proxying arXiv request: {e}")
        return Response(
            content=f"<error>{str(e)}</error>",
            status_code=500,
            media_type="application/xml"
        )
