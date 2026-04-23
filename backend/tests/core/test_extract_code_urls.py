import pytest

from app.core.utils import extract_code_urls, CodePlatform, CodeUrlInfo


class TestExtractCodeUrlsGitHub:
    def test_extract_github_url(self):
        text = "Check out our code at https://github.com/openai/gpt-3"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.GITHUB
        assert result[0].owner == "openai"
        assert result[0].repo == "gpt-3"
        assert result[0].url == "https://github.com/openai/gpt-3"

    def test_extract_github_url_with_hyphen_and_underscore(self):
        text = "Code: https://github.com/my-org/my_awesome-project"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].owner == "my-org"
        assert result[0].repo == "my_awesome-project"

    def test_extract_multiple_github_urls(self):
        text = """
        Main repo: https://github.com/user/repo1
        Demo: https://github.com/user/repo2
        """
        result = extract_code_urls(text)
        
        assert len(result) == 2

    def test_extract_github_url_case_insensitive(self):
        text = "Code: HTTPS://GITHUB.COM/User/Repo"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/User/Repo"

    def test_extract_github_url_with_trailing_punctuation(self):
        text = "See https://github.com/user/repo."
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_github_url_with_trailing_comma(self):
        text = "Code at https://github.com/user/repo, and more"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_github_url_with_query_params(self):
        text = "https://github.com/user/repo?tab=readme"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"


class TestExtractCodeUrlsGitHubPages:
    def test_extract_github_pages_url(self):
        text = "Demo: https://spanvla.github.io/"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.GITHUB_PAGES
        assert result[0].owner == "spanvla"
        assert result[0].repo is None
        assert result[0].url == "https://spanvla.github.io"

    def test_extract_github_pages_url_with_project(self):
        text = "Project: https://tri-ml.github.io/vla_foundry"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.GITHUB_PAGES
        assert result[0].owner == "tri-ml"
        assert result[0].repo == "vla_foundry"
        assert result[0].url == "https://tri-ml.github.io/vla_foundry"

    def test_extract_github_pages_url_without_trailing_slash(self):
        text = "Visit https://user.github.io"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://user.github.io"

    def test_extract_github_pages_url_with_trailing_slash(self):
        text = "Visit https://user.github.io/"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://user.github.io"


class TestExtractCodeUrlsGitLab:
    def test_extract_gitlab_url(self):
        text = "Code: https://gitlab.com/user/project"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.GITLAB
        assert result[0].owner == "user"
        assert result[0].repo == "project"
        assert result[0].url == "https://gitlab.com/user/project"

    def test_extract_gitlab_url_with_hyphen(self):
        text = "https://gitlab.com/my-org/my-project"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].owner == "my-org"
        assert result[0].repo == "my-project"


class TestExtractCodeUrlsBitbucket:
    def test_extract_bitbucket_url(self):
        text = "Code: https://bitbucket.org/user/repo"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.BITBUCKET
        assert result[0].owner == "user"
        assert result[0].repo == "repo"
        assert result[0].url == "https://bitbucket.org/user/repo"


class TestExtractCodeUrlsHuggingFace:
    def test_extract_huggingface_url(self):
        text = "Model: https://huggingface.co/google/bert-base-uncased"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.HUGGINGFACE
        assert result[0].owner == "google"
        assert result[0].repo == "bert-base-uncased"
        assert result[0].url == "https://huggingface.co/google/bert-base-uncased"

    def test_extract_huggingface_url_with_repo(self):
        text = "https://huggingface.co/facebook/bart-large"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].platform == CodePlatform.HUGGINGFACE
        assert result[0].owner == "facebook"
        assert result[0].repo == "bart-large"


class TestExtractCodeUrlsMixed:
    def test_extract_multiple_platforms(self):
        text = """
        GitHub: https://github.com/user/repo
        GitLab: https://gitlab.com/user/project
        HuggingFace: https://huggingface.co/user/model
        """
        result = extract_code_urls(text)
        
        assert len(result) == 3
        platforms = [r.platform for r in result]
        assert CodePlatform.GITHUB in platforms
        assert CodePlatform.GITLAB in platforms
        assert CodePlatform.HUGGINGFACE in platforms

    def test_extract_priority_github_first(self):
        text = """
        https://github.com/user/repo
        https://gitlab.com/user/project
        """
        result = extract_code_urls(text)
        
        assert result[0].platform == CodePlatform.GITHUB

    def test_extract_duplicate_urls_only_once(self):
        text = "See https://github.com/user/repo and also https://github.com/user/repo"
        result = extract_code_urls(text)
        
        assert len(result) == 1


class TestExtractCodeUrlsEdgeCases:
    def test_extract_empty_text(self):
        result = extract_code_urls("")
        assert result == []

    def test_extract_none_text(self):
        result = extract_code_urls(None)
        assert result == []

    def test_extract_no_urls(self):
        text = "This is a paper about machine learning."
        result = extract_code_urls(text)
        
        assert result == []

    def test_extract_url_in_parentheses(self):
        text = "Code available (https://github.com/user/repo)"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_url_in_brackets(self):
        text = "Code [https://github.com/user/repo] available"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_url_with_anchor(self):
        text = "https://github.com/user/repo#readme"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_url_with_multiple_trailing_punctuation(self):
        text = "Check https://github.com/user/repo!!!"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_url_at_end_of_sentence(self):
        text = "The code is at https://github.com/user/repo."
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].url == "https://github.com/user/repo"

    def test_extract_url_with_numbers(self):
        text = "https://github.com/user123/repo456"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].owner == "user123"
        assert result[0].repo == "repo456"

    def test_extract_url_with_period_in_repo_name(self):
        text = "https://github.com/user/repo.name"
        result = extract_code_urls(text)
        
        assert len(result) == 1
        assert result[0].repo == "repo.name"

    def test_extract_realistic_abstract(self):
        text = """
        Abstract: We present a novel approach to natural language processing.
        Our code is available at https://github.com/research-lab/nlp-project.
        Additional resources can be found at https://our-team.github.io/demo/.
        For the pre-trained model, see https://huggingface.co/team/model-v2.
        """
        result = extract_code_urls(text)
        
        assert len(result) == 3
        platforms = [r.platform for r in result]
        assert CodePlatform.GITHUB in platforms
        assert CodePlatform.GITHUB_PAGES in platforms
        assert CodePlatform.HUGGINGFACE in platforms


class TestCodeUrlInfo:
    def test_code_url_info_creation(self):
        info = CodeUrlInfo(
            url="https://github.com/user/repo",
            platform=CodePlatform.GITHUB,
            owner="user",
            repo="repo"
        )
        
        assert info.url == "https://github.com/user/repo"
        assert info.platform == CodePlatform.GITHUB
        assert info.owner == "user"
        assert info.repo == "repo"

    def test_code_url_info_with_none_values(self):
        info = CodeUrlInfo(
            url="https://user.github.io",
            platform=CodePlatform.GITHUB_PAGES,
            owner="user"
        )
        
        assert info.repo is None


class TestCodePlatform:
    def test_platform_values(self):
        assert CodePlatform.GITHUB.value == "github"
        assert CodePlatform.GITLAB.value == "gitlab"
        assert CodePlatform.BITBUCKET.value == "bitbucket"
        assert CodePlatform.HUGGINGFACE.value == "huggingface"
        assert CodePlatform.GITHUB_PAGES.value == "github_pages"
