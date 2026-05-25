"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils import validate_prompt_structure

PROMPT_FILE = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")

PROMPT_KEY = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.prompt_data = load_prompts(PROMPT_FILE)
        self.system_prompt = self.prompt_data.get(PROMPT_KEY).get("system_prompt", "")
        self.techniques = self.prompt_data.get(PROMPT_KEY).get("techniques_applied", [])

    def test_prompt_has_system_prompt(self):
        assert self.system_prompt is not None
        assert str(self.system_prompt).strip() != ""


    def test_prompt_has_role_definition(self):
        assert "você é" in self.system_prompt.lower()
        assert re.search(r"Analista de Sistemas | sênior", self.system_prompt, re.IGNORECASE)


    def test_prompt_mentions_format(self):
        re.search(r"[Ator/Tipo de usuário]", self.system_prompt, re.IGNORECASE)
        re.search(r"Critérios de Aceitação", self.system_prompt, re.IGNORECASE)

    def test_prompt_has_few_shot_examples(self):
        re.search(r"EXEMPLOS DE REFERÊNCIA", self.system_prompt, re.IGNORECASE)
        re.search(r"EXEMPLO 1", self.system_prompt, re.IGNORECASE)
        re.search(r"EXEMPLO 2", self.system_prompt, re.IGNORECASE)

    def test_prompt_no_todos(self):
        re.search(r"TODO", self.system_prompt, re.IGNORECASE)

    def test_minimum_techniques(self):
        assert isinstance(self.techniques, list)
        assert len(self.techniques) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])