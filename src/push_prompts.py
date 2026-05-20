"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain.prompts import PromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

LOCAL_PROMPT_PATH_V2 = "prompts/bug_to_user_story_mba_v2.yml"
PROMPT_KEY = "bug_to_user_story_mba_v2"

def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    
    errors = []

    required_fields = ['system_prompt', 'user_prompt', 'version', 'description', 'techniques', 'tags']

    for field in required_fields:
        if not prompt_data.get(field):
            errors.append(f"Required field missing: ")
    
    if not prompt_data.get('system_prompt').strip():
        errors.append(f"The attribute cannot be empty: system_prompt")

    if not prompt_data.get('user_prompt').strip():
        errors.append(f"The attribute cannot be empty: user_prompt")

    if not prompt_data.get('version').strip():
        errors.append(f"The attribute cannot be empty: version")

    if not prompt_data.get('description').strip():
        errors.append(f"The attribute cannot be empty: description")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith():
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).
    """
    
    print_section_header("Starting process: Push prompt")

    required_vars = [
        "LANGSMITH_API_KEY",
        "LANGSMITH_ENDPOINT",
        "USERNAME_LANGSMITH_HUB",
    ]
    
    if not check_env_vars(required_vars):
        return False
    
    yaml_data = load_yaml(LOCAL_PROMPT_PATH_V2)
    
    if not yaml_data:
        print(f"File {LOCAL_PROMPT_PATH_V2} not found, check the folder prompt.")
        return False

    prompt_data = yaml_data.get(PROMPT_KEY)

    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print("Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return False

    system_prompt = prompt_data.get("system_prompt")

    user_prompt = prompt_data.get("user_prompt")

    description = prompt_data.get("description")

    tags = prompt_data.get("tags", [])
    
    tags_list = []
    
    for tag in tags:
        tags_list.append(tag)

    techniques = prompt_data.get("techniques", [])
    
    techniques_list = []
    
    for technique in techniques:
        techniques_list.append(technique)

    full_repo_name = f"{os.getenv('USERNAME_LANGSMITH_HUB')}/{PROMPT_KEY}"

    print(f"Push prompt to LangSmith Hub: {full_repo_name}")
        
    prompt_template = PromptTemplate(
        input_variables=user_prompt,
        template=system_prompt,
        partial_variables={
            "description": description.strip(),
            "techniques": ", ".join(techniques_list)
        }
    )

    try:
        hub.push(
            repo_full_name=full_repo_name,
            object=prompt_template,
            new_repo_is_public=True,
            tags=tags or [],
        )

        print(f"Checking if the prompt was published: {full_repo_name}")

        remote_prompt = hub.pull(full_repo_name)

        if remote_prompt is None:
            print("The remote prompt could not be loaded.")
            return False
        
        print(f"Prompt was published")

    except Exception as e:
        error_text = str(e)
        if "Nothing to commit" in error_text:
            print(f"The prompt shows no changes; to make a new commit, modify something in the file. {LOCAL_PROMPT_PATH_V2}")
            print_section_header("Ending process: Push prompt")
            return True

    print_section_header("Ending process: Push prompt")
    
    return True


def main():
    return push_prompt_to_langsmith()


if __name__ == "__main__":
    sys.exit(main())
