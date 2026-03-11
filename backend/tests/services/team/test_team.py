import pytest
from datetime import datetime

from app.services.team.types import (
    TaskComplexity,
    TeamTaskStatus,
    SubTaskStatus,
    TeamSessionStatus,
    TeamMessageRole,
    SubTask,
    TeamTask,
    TeamMessage,
    SubTaskResult,
    TeamResult,
    LeadAgentConfig,
    TeamSession,
    TeamExecuteRequest,
    DecompositionResult,
    SynthesisResult,
)
from app.services.team.decomposer import TaskDecomposer
from app.services.team.synthesizer import ResultSynthesizer


class TestTaskDecomposer:
    """Tests for TaskDecomposer."""
    
    def setup_method(self):
        self.decomposer = TaskDecomposer()
    
    def test_analyze_simple_task(self):
        """Test analyzing a simple task."""
        instruction = "Summarize paper 2301.00001"
        complexity = self.decomposer.analyze_complexity(instruction)
        assert complexity in [TaskComplexity.SIMPLE, TaskComplexity.STANDARD]
    
    def test_analyze_comparison_task(self):
        """Test analyzing a comparison task."""
        instruction = "Compare Vision Transformers and BERT attention mechanisms"
        complexity = self.decomposer.analyze_complexity(instruction)
        assert complexity in [TaskComplexity.MODERATE, TaskComplexity.HIGH]
    
    def test_analyze_review_task(self):
        """Test analyzing a literature review task."""
        instruction = "Provide a comprehensive review of recent advances in multimodal learning"
        complexity = self.decomposer.analyze_complexity(instruction)
        assert complexity == TaskComplexity.HIGH
    
    def test_should_use_team_mode_simple(self):
        """Test that simple tasks don't use team mode."""
        instruction = "What is machine learning?"
        complexity = self.decomposer.analyze_complexity(instruction)
        use_team = self.decomposer.should_use_team_mode(complexity, instruction)
        assert use_team is False
    
    def test_should_use_team_mode_high(self):
        """Test that high complexity tasks use team mode."""
        complexity = TaskComplexity.HIGH
        instruction = "Compare multiple transformer architectures"
        use_team = self.decomposer.should_use_team_mode(complexity, instruction)
        assert use_team is True
    
    def test_decompose_simple_task(self):
        """Test decomposing a simple task."""
        instruction = "Summarize this paper"
        result = self.decomposer.decompose(instruction)
        
        assert result.complexity in [TaskComplexity.SIMPLE, TaskComplexity.STANDARD]
    
    def test_decompose_comparison_task(self):
        """Test decomposing a comparison task."""
        instruction = "Compare Vision Transformers and BERT"
        result = self.decomposer.decompose(instruction)
        
        assert result.complexity in [TaskComplexity.MODERATE, TaskComplexity.HIGH]
    
    def test_decompose_with_paper_ids(self):
        """Test decomposing with paper IDs."""
        instruction = "Analyze these papers"
        context = {"paper_ids": ["2301.00001", "2301.00002", "2301.00003"]}
        result = self.decomposer.decompose(instruction, context)
        
        assert result.reasoning is not None


class TestResultSynthesizer:
    """Tests for ResultSynthesizer."""
    
    def setup_method(self):
        self.synthesizer = ResultSynthesizer()
    
    def test_synthesize_empty_results(self):
        """Test synthesizing empty results."""
        result = self.synthesizer.synthesize(
            original_instruction="Test instruction",
            subtask_results=[],
        )
        
        assert result.output == "No results to synthesize."
        assert result.confidence == 0.0
        assert result.needs_more_info is True
    
    def test_synthesize_successful_results(self):
        """Test synthesizing successful results."""
        results = [
            SubTaskResult(
                subtask_id="sub_1",
                agent_id="research-agent",
                status=SubTaskStatus.COMPLETED,
                result="Found relevant papers about transformers.",
            ),
            SubTaskResult(
                subtask_id="sub_2",
                agent_id="analysis-agent",
                status=SubTaskStatus.COMPLETED,
                result="Analyzed attention mechanisms.",
            ),
        ]
        
        result = self.synthesizer.synthesize(
            original_instruction="Research transformer attention",
            subtask_results=results,
        )
        
        assert len(result.output) > 0
        assert result.confidence > 0
    
    def test_synthesize_failed_results(self):
        """Test synthesizing failed results."""
        results = [
            SubTaskResult(
                subtask_id="sub_1",
                agent_id="research-agent",
                status=SubTaskStatus.FAILED,
                error="Search failed",
            ),
        ]
        
        result = self.synthesizer.synthesize(
            original_instruction="Test instruction",
            subtask_results=results,
        )
        
        assert "failed" in result.output.lower() or "error" in result.output.lower()
    
    def test_compress_result(self):
        """Test result compression."""
        long_result = "This is a very long result. " * 100
        compressed = self.synthesizer.compress_result(long_result, max_length=100)
        
        assert len(compressed) <= 103


class TestTypes:
    """Tests for type definitions."""
    
    def test_subtask_creation(self):
        """Test SubTask creation."""
        subtask = SubTask(
            parent_task_id="task_1",
            instruction="Test instruction",
            assigned_agent="research-agent",
        )
        
        assert subtask.status == SubTaskStatus.PENDING
        assert subtask.dependencies == []
        assert subtask.result is None
    
    def test_team_task_creation(self):
        """Test TeamTask creation."""
        task = TeamTask(
            instruction="Test task",
            complexity=TaskComplexity.MODERATE,
        )
        
        assert task.status == TeamTaskStatus.PENDING
        assert task.subtasks == []
        assert task.complexity == TaskComplexity.MODERATE
    
    def test_team_message_creation(self):
        """Test TeamMessage creation."""
        message = TeamMessage(
            role=TeamMessageRole.USER,
            content="Test message",
        )
        
        assert message.role == TeamMessageRole.USER
        assert message.content == "Test message"
    
    def test_team_session_creation(self):
        """Test TeamSession creation."""
        session = TeamSession()
        
        assert session.status == TeamSessionStatus.INITIALIZING
        assert session.messages == []
    
    def test_team_session_add_message(self):
        """Test adding message to session."""
        session = TeamSession()
        message = session.add_message(
            role=TeamMessageRole.USER,
            content="Test message",
        )
        
        assert len(session.messages) == 1
        assert session.messages[0].content == "Test message"
    
    def test_decomposition_result_creation(self):
        """Test DecompositionResult creation."""
        result = DecompositionResult(
            complexity=TaskComplexity.MODERATE,
            use_team_mode=True,
            subtasks=[{"instruction": "Test"}],
            reasoning="Test reasoning",
        )
        
        assert result.complexity == TaskComplexity.MODERATE
        assert result.use_team_mode is True
        assert len(result.subtasks) == 1
    
    def test_synthesis_result_creation(self):
        """Test SynthesisResult creation."""
        result = SynthesisResult(
            output="Test output",
            sources=["2301.00001"],
            confidence=0.8,
        )
        
        assert result.output == "Test output"
        assert result.confidence == 0.8
    
    def test_to_dict_methods(self):
        """Test to_dict methods."""
        subtask = SubTask(
            parent_task_id="task_1",
            instruction="Test",
        )
        subtask_dict = subtask.to_dict()
        
        assert isinstance(subtask_dict, dict)
        assert subtask_dict["instruction"] == "Test"
        
        task = TeamTask(instruction="Test task")
        task_dict = task.to_dict()
        
        assert isinstance(task_dict, dict)
        assert task_dict["instruction"] == "Test task"
    
    def test_team_execute_request(self):
        """Test TeamExecuteRequest creation."""
        request = TeamExecuteRequest(
            instruction="Test instruction",
            paper_ids=["2301.00001"],
            force_team_mode=True,
        )
        
        assert request.instruction == "Test instruction"
        assert request.paper_ids == ["2301.00001"]
        assert request.force_team_mode is True
