import httpx
from typing import Optional
from fastapi import HTTPException

TARGET_BASE_URL = "http://localhost:8000"


async def fetch_openapi_schema() -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TARGET_BASE_URL}/openapi.json", timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to target API at {TARGET_BASE_URL}. Please ensure the main application is running."
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Timeout while fetching OpenAPI schema from target API."
            )


def parse_endpoints(schema: dict) -> list[dict]:
    endpoints = []
    paths = schema.get("paths", {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                endpoint = {
                    "path": path,
                    "method": method.upper(),
                    "tags": details.get("tags", []),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": details.get("parameters", []),
                    "requestBody": details.get("requestBody"),
                    "responses": details.get("responses", {}),
                    "operationId": details.get("operationId", ""),
                }
                endpoints.append(endpoint)
    
    return endpoints


def group_by_tags(endpoints: list[dict]) -> dict[str, list[dict]]:
    grouped = {}
    for endpoint in endpoints:
        tags = endpoint.get("tags", ["default"])
        for tag in tags:
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(endpoint)
    return grouped
