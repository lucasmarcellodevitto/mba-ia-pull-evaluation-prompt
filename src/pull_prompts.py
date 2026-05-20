"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_mba_v1

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header
from datetime import datetime
load_dotenv()

REMOTE_PROMPT_PATH = "leonanluppi/bug_to_user_story_v1"
LOCAL_PROMPT_PATH = "prompts/bug_to_user_story_mba_v1.yml"
DATE_FORMAT = datetime.now().strftime("%Y-%m-%d")

def extract_content(remote_prompt):
    system_prompt = ""
    user_prompt = ""
    for msg in remote_prompt.messages:
        template = msg.prompt.template if hasattr(msg, 'prompt') else str(msg)
        if msg.__class__.__name__ == "SystemMessagePromptTemplate":
           system_prompt = template
        if msg.__class__.__name__ == "HumanMessagePromptTemplate":
           user_prompt = template
    return system_prompt, user_prompt

def pull_prompts_from_langsmith():
    
    print_section_header("Starting process: Pull prompt")
    
    required_vars = [
        "LANGSMITH_API_KEY",
        "LANGSMITH_ENDPOINT",
     ]

    if not check_env_vars(required_vars):
        return False

    print(f"Buscando prompt remoto: {REMOTE_PROMPT_PATH}")
    remote_prompt = hub.pull(REMOTE_PROMPT_PATH)
    
    if remote_prompt is None:
        print("The remote prompt could not be loaded.")
        return False

    system_prompt, user_prompt = extract_content(remote_prompt)

    yaml_data = {
        "bug_to_user_story_mba_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source": REMOTE_PROMPT_PATH,
            "created_at": datetime.now().strftime(DATE_FORMAT),
            "tags": [
                "bug-analysis",
                "user-story",
                "langsmith-import",
            ],
        } 
    }    

    if not save_yaml(yaml_data, LOCAL_PROMPT_PATH):
        print("Failed to save the prompt locally.")
        return False
        
    print(f"Prompt saved locally in:{LOCAL_PROMPT_PATH}")
    
    print_section_header("Ending process: Pull prompt")


def main():
    pull_prompts_from_langsmith()


if __name__ == "__main__":
    sys.exit(main())
