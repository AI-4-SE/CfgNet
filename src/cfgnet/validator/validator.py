import os
import backoff
import logging
import json
from openai import OpenAI, RateLimitError, APIError, APIConnectionError, Timeout
from typing import List
from cfgnet.validator.prompts import Templates
from cfgnet.conflicts.conflict import Conflict
from cfgnet.utility.util import transform


class Validator:
    def __init__(self) -> None:
        self.model_name= os.getenv("MODEL_NAME", default="gpt-4o-mini-2024-07-18")
        self.temperature = os.getenv("TEMPERATURE", default=0.4)
        self.max_tokens = os.getenv("TEMPERATURE", default=250)
        self.templates = Templates()

    @backoff.on_exception(backoff.expo, (RateLimitError, APIError, APIConnectionError, Timeout, Exception), max_tries=5)
    def generate(self, messages: List) -> str:
        client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        
        response = client.chat.completions.create(
            model=self.model_name, 
            messages=messages,        
            temperature=self.temperature,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens
        )
    
        response_content = response.choices[0].message.content

        if not response or len(response_content.strip()) == 0:
            logging.eror("Response content was empty.")
        
        return response_content

    def validate(self, conflict: Conflict) -> bool:
        
        dependency = transform(link=conflict.link)

        system_prompt = self.templates.system.format(project=dependency.project)
        format_str = self.templates.format.format()
        task_prompt = self.templates.task.format(
            nameA=dependency.option_name,
            typeA=dependency.option_type,
            valueA=dependency.option_value,
            fileA=dependency.option_file,
            technologyA=dependency.option_technology,
            nameB=dependency.dependent_option_name,
            typeB=dependency.dependent_option_type,
            valueB=dependency.dependent_option_value,
            fileB=dependency.dependent_option_file,
            technologyB=dependency.dependent_option_technology,
        )

        user_prompt = f"{task_prompt}\n\n{format_str}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # TODO: Add multi-aggregation
        response = self.generate(messages=messages)

        
        
        dependency


    