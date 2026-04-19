import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

router = APIRouter(prefix="/proxy", tags=["proxy"])

TARGET_BASE_URL = "http://localhost:8000"


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(request: Request, path: str):
    target_url = f"{TARGET_BASE_URL}/{path}"
    
    query_params = dict(request.query_params)
    
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except Exception:
            pass
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                params=query_params,
                content=body,
                headers=headers,
            )
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            }
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to target API at {TARGET_BASE_URL}. Please ensure the main application is running."
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Timeout while connecting to target API."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Proxy error: {str(e)}"
            )
