import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock, MagicMock

sys.modules["pymilvus"] = MagicMock()
sys.modules["pymilvus.connections"] = MagicMock()
sys.modules["pymilvus.Collection"] = MagicMock()
sys.modules["pymilvus.utility"] = MagicMock()
sys.modules["pymilvus.DataType"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

from app.services.skill_service import SkillService
from app.services.skills.base import SkillProvider
from app.services.skills.registry import SkillRegistry
from typing import Dict, Any, List, Optional


class MockSkillProvider(SkillProvider):
    """Mock skill provider for testing."""
    
    def __init__(self, skill_id: str = "mock_skill", available: bool = True, requires_paper: bool = True):
        self._id = skill_id
        self._available = available
        self._requires_paper = requires_paper
        self._execute_called = False
        self._execute_context = None
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return "Mock Skill"
    
    @property
    def description(self) -> str:
        return "A mock skill for testing"
    
    @property
    def icon(self) -> str:
        return "mock"
    
    @property
    def category(self) -> str:
        return "test"
    
    @property
    def requires_paper(self) -> bool:
        return self._requires_paper
    
    @property
    def input_schema(self) -> Optional[Dict[str, Any]]:
        return {"type": "object", "properties": {}}
    
    def is_available(self) -> bool:
        return self._available
    
    async def execute(
        self,
        context: Dict[str, Any],
        paper_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        self._execute_called = True
        self._execute_context = context
        return {"success": True, "result": "mock_result"}


@pytest.fixture
def mock_paper_service():
    mock = Mock()
    mock.get_papers_by_ids = Mock(return_value=[])
    return mock


@pytest.fixture
def skill_service(mock_paper_service):
    with patch('app.services.skill_service.PaperService', return_value=mock_paper_service):
        service = SkillService()
        service.paper_service = mock_paper_service
        yield service


@pytest.fixture
def mock_skill():
    return MockSkillProvider()


@pytest.fixture
def sample_paper():
    return {
        "id": "2301.12345",
        "title": "Test Paper",
        "abstract": "Test abstract",
        "authors": ["Author One"],
    }


class TestSkillServiceGetAllSkills:
    def test_get_all_skills_returns_list(self, skill_service):
        skills = skill_service.get_all_skills()
        
        assert isinstance(skills, list)
    
    def test_get_all_skills_returns_dict_items(self, skill_service):
        skills = skill_service.get_all_skills()
        
        for skill in skills:
            assert isinstance(skill, dict)
            assert "id" in skill
            assert "name" in skill
            assert "description" in skill
            assert "icon" in skill
            assert "category" in skill
            assert "requires_paper" in skill
            assert "available" in skill
    
    def test_get_all_skills_includes_expected_skills(self, skill_service):
        skills = skill_service.get_all_skills()
        skill_ids = [s["id"] for s in skills]
        
        assert "summary" in skill_ids
        assert "translation" in skill_ids
        assert "citation" in skill_ids
        assert "related" in skill_ids


class TestSkillServiceGetSkillsByCategory:
    def test_get_skills_by_category_returns_dict(self, skill_service):
        result = skill_service.get_skills_by_category()
        
        assert isinstance(result, dict)
    
    def test_get_skills_by_category_groups_correctly(self, skill_service):
        result = skill_service.get_skills_by_category()
        
        for category, skills in result.items():
            assert isinstance(category, str)
            assert isinstance(skills, list)
            for skill in skills:
                assert skill["category"] == category
    
    def test_get_skills_by_category_includes_expected_categories(self, skill_service):
        result = skill_service.get_skills_by_category()
        categories = list(result.keys())
        
        assert "analysis" in categories
        assert "writing" in categories
        assert "search" in categories


class TestSkillServiceGetSkill:
    def test_get_skill_returns_skill_dict(self, skill_service):
        skill = skill_service.get_skill("summary")
        
        assert skill is not None
        assert skill["id"] == "summary"
        assert skill["name"] == "Paper Summary"
    
    def test_get_skill_returns_none_for_nonexistent(self, skill_service):
        skill = skill_service.get_skill("nonexistent_skill")
        
        assert skill is None
    
    def test_get_skill_returns_correct_skill(self, skill_service):
        skill = skill_service.get_skill("translation")
        
        assert skill["id"] == "translation"
        assert skill["category"] == "writing"


class TestSkillServiceExecuteSkill:
    @pytest.mark.asyncio
    async def test_execute_skill_not_found(self, skill_service):
        result = await skill_service.execute_skill("nonexistent_skill")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_execute_skill_with_paper_ids(self, skill_service, mock_paper_service, sample_paper):
        mock_paper_service.get_papers_by_ids.return_value = [sample_paper]
        
        with patch.object(SkillRegistry, 'get', return_value=MockSkillProvider()):
            result = await skill_service.execute_skill(
                skill_id="mock_skill",
                paper_ids=["2301.12345"],
            )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_skill_no_papers_found(self, skill_service, mock_paper_service):
        mock_paper_service.get_papers_by_ids.return_value = []
        
        with patch.object(SkillRegistry, 'get', return_value=MockSkillProvider(requires_paper=True)):
            result = await skill_service.execute_skill(
                skill_id="mock_skill",
                paper_ids=["nonexistent"],
            )
        
        assert result["success"] is False
        assert "no papers found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_execute_skill_paper_service_error(self, skill_service, mock_paper_service):
        mock_paper_service.get_papers_by_ids.side_effect = Exception("Database error")
        
        with patch.object(SkillRegistry, 'get', return_value=MockSkillProvider(requires_paper=True)):
            result = await skill_service.execute_skill(
                skill_id="mock_skill",
                paper_ids=["2301.12345"],
            )
        
        assert result["success"] is False
        assert "failed to get papers" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_execute_skill_sets_llm_context(self, skill_service, mock_paper_service, sample_paper):
        mock_paper_service.get_papers_by_ids.return_value = [sample_paper]
        mock_skill = MockSkillProvider()
        
        with patch.object(SkillRegistry, 'get', return_value=mock_skill):
            await skill_service.execute_skill(
                skill_id="mock_skill",
                paper_ids=["2301.12345"],
                provider="openai",
                model="gpt-4",
            )
        
        assert mock_skill._execute_context["llm_provider"] == "openai"
        assert mock_skill._execute_context["llm_model"] == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_execute_skill_skill_execution_error(self, skill_service, mock_paper_service, sample_paper):
        mock_paper_service.get_papers_by_ids.return_value = [sample_paper]
        
        class FailingSkill(MockSkillProvider):
            async def execute(self, context, paper_ids, **kwargs):
                raise Exception("Skill execution failed")
        
        with patch.object(SkillRegistry, 'get', return_value=FailingSkill()):
            result = await skill_service.execute_skill(
                skill_id="failing_skill",
                paper_ids=["2301.12345"],
            )
        
        assert result["success"] is False
        assert "failed to execute skill" in result["error"].lower()


class TestSkillRegistry:
    def test_registry_singleton(self):
        registry1 = SkillRegistry()
        registry2 = SkillRegistry()
        
        assert registry1 is registry2
    
    def test_registry_get_all(self):
        skills = SkillRegistry.get_all()
        
        assert isinstance(skills, list)
    
    def test_registry_get_by_id(self):
        skill = SkillRegistry.get("summary")
        
        assert skill is not None
        assert skill.id == "summary"
    
    def test_registry_get_nonexistent(self):
        skill = SkillRegistry.get("nonexistent_skill")
        
        assert skill is None
    
    def test_registry_get_by_category(self):
        skills = SkillRegistry.get_by_category("analysis")
        
        for skill in skills:
            assert skill.category == "analysis"
    
    def test_registry_get_available(self):
        skills = SkillRegistry.get_available()
        
        for skill in skills:
            assert skill.is_available()
    
    def test_registry_get_categories(self):
        categories = SkillRegistry.get_categories()
        
        assert isinstance(categories, list)
        assert "analysis" in categories
        assert "writing" in categories


class TestSkillProviderBaseClass:
    def test_to_dict(self):
        skill = MockSkillProvider()
        result = skill.to_dict()
        
        assert result["id"] == "mock_skill"
        assert result["name"] == "Mock Skill"
        assert result["description"] == "A mock skill for testing"
        assert result["icon"] == "mock"
        assert result["category"] == "test"
        assert result["requires_paper"] is True
        assert result["available"] is True
        assert result["input_schema"] is not None
    
    def test_is_available_default(self):
        skill = MockSkillProvider(available=True)
        assert skill.is_available() is True
    
    def test_is_available_false(self):
        skill = MockSkillProvider(available=False)
        assert skill.is_available() is False
    
    def test_requires_paper_default(self):
        skill = MockSkillProvider(requires_paper=True)
        assert skill.requires_paper is True
    
    def test_requires_paper_false(self):
        skill = MockSkillProvider(requires_paper=False)
        assert skill.requires_paper is False
