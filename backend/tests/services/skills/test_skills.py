import pytest
import sys
from unittest.mock import patch, AsyncMock, MagicMock

sys.modules["pymilvus"] = MagicMock()
sys.modules["pymilvus.connections"] = MagicMock()
sys.modules["pymilvus.Collection"] = MagicMock()
sys.modules["pymilvus.utility"] = MagicMock()
sys.modules["pymilvus.DataType"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.skills import router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_skill_service():
    with patch('app.routers.skills.skill_service') as mock:
        yield mock


@pytest.fixture
def sample_skill():
    return {
        "id": "summary",
        "name": "Paper Summary",
        "description": "Generate a concise summary",
        "icon": "file-text",
        "category": "analysis",
        "requires_paper": True,
        "available": True,
        "input_schema": {"type": "object", "properties": {}},
    }


@pytest.fixture
def sample_skills_list():
    return [
        {
            "id": "summary",
            "name": "Paper Summary",
            "description": "Generate a concise summary",
            "icon": "file-text",
            "category": "analysis",
            "requires_paper": True,
            "available": True,
            "input_schema": None,
        },
        {
            "id": "translation",
            "name": "Paper Translation",
            "description": "Translate paper content",
            "icon": "languages",
            "category": "writing",
            "requires_paper": True,
            "available": True,
            "input_schema": None,
        },
        {
            "id": "citation",
            "name": "Citation Generator",
            "description": "Generate citations",
            "icon": "quote",
            "category": "writing",
            "requires_paper": True,
            "available": True,
            "input_schema": None,
        },
    ]


@pytest.fixture
def sample_skill_raw_content():
    return '''---
name: paper-summary
description: Generate a concise summary
icon: file-text
category: analysis
requires_paper: true
---

# Paper Summary Skill

Generate a concise summary of academic papers.

```prompt
Please provide a {detail_level} summary of the following paper:
Title: {paper.title}
Abstract: {paper.abstract}
```
'''


class TestGetSkills:
    def test_get_skills_success(self, client, mock_skill_service, sample_skills_list):
        mock_skill_service.get_all_skills.return_value = sample_skills_list
        
        response = client.get("/skills")
        
        assert response.status_code == 200
        assert "skills" in response.json()
        assert "total" in response.json()
        assert response.json()["total"] == 3
        assert len(response.json()["skills"]) == 3
    
    def test_get_skills_empty(self, client, mock_skill_service):
        mock_skill_service.get_all_skills.return_value = []
        
        response = client.get("/skills")
        
        assert response.status_code == 200
        assert response.json()["skills"] == []
        assert response.json()["total"] == 0


class TestGetSkillsByCategory:
    def test_get_skills_by_category_success(self, client, mock_skill_service):
        mock_skill_service.get_skills_by_category.return_value = {
            "analysis": [
                {"id": "summary", "name": "Paper Summary", "category": "analysis"}
            ],
            "writing": [
                {"id": "translation", "name": "Paper Translation", "category": "writing"},
                {"id": "citation", "name": "Citation Generator", "category": "writing"},
            ],
        }
        
        response = client.get("/skills/categories")
        
        assert response.status_code == 200
        result = response.json()
        assert "analysis" in result
        assert "writing" in result
        assert len(result["writing"]) == 2
    
    def test_get_skills_by_category_empty(self, client, mock_skill_service):
        mock_skill_service.get_skills_by_category.return_value = {}
        
        response = client.get("/skills/categories")
        
        assert response.status_code == 200
        assert response.json() == {}


class TestGetSkill:
    def test_get_skill_success(self, client, mock_skill_service, sample_skill):
        mock_skill_service.get_skill.return_value = sample_skill
        
        response = client.get("/skills/summary")
        
        assert response.status_code == 200
        assert response.json()["id"] == "summary"
        assert response.json()["name"] == "Paper Summary"
        mock_skill_service.get_skill.assert_called_once_with("summary")
    
    def test_get_skill_not_found(self, client, mock_skill_service):
        mock_skill_service.get_skill.return_value = None
        
        response = client.get("/skills/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetSkillRaw:
    def test_get_skill_raw_success(self, client, mock_skill_service, sample_skill_raw_content):
        mock_skill_service.get_skill_raw.return_value = sample_skill_raw_content
        
        response = client.get("/skills/paper-summary/raw")
        
        assert response.status_code == 200
        assert response.json()["skill_id"] == "paper-summary"
        assert "content" in response.json()
        assert "---" in response.json()["content"]
        mock_skill_service.get_skill_raw.assert_called_once_with("paper-summary")
    
    def test_get_skill_raw_not_found(self, client, mock_skill_service):
        mock_skill_service.get_skill_raw.return_value = None
        
        response = client.get("/skills/nonexistent/raw")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_skill_raw_builtin_skill(self, client, mock_skill_service):
        mock_skill_service.get_skill_raw.return_value = None
        
        response = client.get("/skills/summary/raw")
        
        assert response.status_code == 404
        assert "not a dynamic skill" in response.json()["detail"].lower()


class TestReloadSkills:
    def test_reload_skills_success(self, client, mock_skill_service):
        mock_skill_service.reload_skills.return_value = {
            "success": True,
            "loaded": 5,
            "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"]
        }
        
        response = client.post("/skills/reload")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["loaded"] == 5
        mock_skill_service.reload_skills.assert_called_once()
    
    def test_reload_skills_empty(self, client, mock_skill_service):
        mock_skill_service.reload_skills.return_value = {
            "success": True,
            "loaded": 0,
            "skills": []
        }
        
        response = client.post("/skills/reload")
        
        assert response.status_code == 200
        assert response.json()["loaded"] == 0


class TestReloadSkill:
    def test_reload_skill_success(self, client, mock_skill_service):
        mock_skill_service.reload_skill.return_value = {
            "success": True,
            "skill_id": "paper-summary",
            "message": "Skill reloaded"
        }
        
        response = client.post("/skills/paper-summary/reload")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["skill_id"] == "paper-summary"
        mock_skill_service.reload_skill.assert_called_once_with("paper-summary")
    
    def test_reload_skill_not_found(self, client, mock_skill_service):
        mock_skill_service.reload_skill.return_value = {
            "success": False,
            "skill_id": "nonexistent",
            "message": "Skill not found or reload failed"
        }
        
        response = client.post("/skills/nonexistent/reload")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSaveSkill:
    def test_save_skill_success(self, client, mock_skill_service, sample_skill_raw_content):
        mock_skill_service.save_skill.return_value = {
            "success": True,
            "skill_id": "paper-summary",
            "message": "Skill saved and reloaded"
        }
        
        response = client.put(
            "/skills/paper-summary",
            json={"content": sample_skill_raw_content}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["skill_id"] == "paper-summary"
        mock_skill_service.save_skill.assert_called_once_with("paper-summary", sample_skill_raw_content)
    
    def test_save_skill_not_found(self, client, mock_skill_service, sample_skill_raw_content):
        mock_skill_service.save_skill.return_value = {
            "success": False,
            "skill_id": "nonexistent",
            "message": "Failed to save skill content"
        }
        
        response = client.put(
            "/skills/nonexistent",
            json={"content": sample_skill_raw_content}
        )
        
        assert response.status_code == 400
        assert "failed to save" in response.json()["detail"].lower()
    
    def test_save_skill_invalid_content(self, client, mock_skill_service):
        mock_skill_service.save_skill.return_value = {
            "success": False,
            "skill_id": "paper-summary",
            "message": "Failed to save skill content"
        }
        
        response = client.put(
            "/skills/paper-summary",
            json={"content": "invalid content without frontmatter"}
        )
        
        assert response.status_code == 400
    
    def test_save_skill_empty_content(self, client, mock_skill_service):
        mock_skill_service.save_skill.return_value = {
            "success": False,
            "skill_id": "paper-summary",
            "message": "Failed to save skill content"
        }
        
        response = client.put(
            "/skills/paper-summary",
            json={"content": ""}
        )
        
        assert response.status_code == 400


class TestExecuteSkill:
    def test_execute_skill_success(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": True,
            "paper_id": "2301.12345",
            "summary": "This is a test summary.",
        })
        
        response = client.post(
            "/skills/summary/execute",
            json={
                "paper_ids": ["2301.12345"],
                "params": {"detail_level": "brief"},
            }
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "summary" in response.json()
    
    def test_execute_skill_with_provider(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": True,
            "translation": "Translated text",
        })
        
        response = client.post(
            "/skills/translation/execute",
            json={
                "paper_ids": ["2301.12345"],
                "provider": "ollama",
                "model": "llama3",
                "params": {"target_language": "Chinese"},
            }
        )
        
        assert response.status_code == 200
        mock_skill_service.execute_skill.assert_called_once()
        call_kwargs = mock_skill_service.execute_skill.call_args[1]
        assert call_kwargs["provider"] == "ollama"
        assert call_kwargs["model"] == "llama3"
    
    def test_execute_skill_failure(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": False,
            "error": "No papers found",
        })
        
        response = client.post(
            "/skills/summary/execute",
            json={"paper_ids": ["nonexistent"]}
        )
        
        assert response.status_code == 400
        assert "no papers found" in response.json()["detail"].lower()
    
    def test_execute_skill_skill_not_found(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": False,
            "error": "Skill not found: nonexistent",
        })
        
        response = client.post(
            "/skills/nonexistent/execute",
            json={"paper_ids": ["2301.12345"]}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_execute_skill_empty_request(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": True,
            "result": "ok",
        })
        
        response = client.post("/skills/summary/execute", json={})
        
        assert response.status_code == 200
    
    def test_execute_skill_with_context(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": True,
            "result": "ok",
        })
        
        response = client.post(
            "/skills/summary/execute",
            json={
                "paper_ids": ["2301.12345"],
                "context": {"custom_key": "custom_value"},
            }
        )
        
        assert response.status_code == 200
        call_kwargs = mock_skill_service.execute_skill.call_args[1]
        assert call_kwargs["context"] == {"custom_key": "custom_value"}
    
    def test_execute_skill_with_params(self, client, mock_skill_service):
        mock_skill_service.execute_skill = AsyncMock(return_value={
            "success": True,
            "result": "ok",
        })
        
        response = client.post(
            "/skills/translation/execute",
            json={
                "paper_ids": ["2301.12345"],
                "params": {
                    "target_language": "Chinese",
                    "content_type": "abstract"
                },
            }
        )
        
        assert response.status_code == 200
        call_kwargs = mock_skill_service.execute_skill.call_args[1]
        assert call_kwargs["target_language"] == "Chinese"
        assert call_kwargs["content_type"] == "abstract"
