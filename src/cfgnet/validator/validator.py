import os
import backoff
import logging
import json
from openai import OpenAI, RateLimitError, APIError, APIConnectionError, Timeout
from typing import List
from collections import Counter
from cfgnet.validator.prompts import Templates
from cfgnet.conflicts.conflict import Conflict
from cfgnet.utility.util import transform


class Validator:
    def __init__(self) -> None:
        self.model_name= "gpt-4o-mini-2024-07-18"
        self.temperature = 0.4
        self.max_tokens = 250
        self.repetition = 3
        self.templates = Templates()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @backoff.on_exception(backoff.expo, (RateLimitError, APIError, APIConnectionError, Timeout, Exception), max_tries=5)
    def generate(self, messages: List) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name, 
            messages=messages,        
            temperature=self.temperature,
            response_format={"type": "json_object"},
            max_tokens=self.max_tokens
        )
    
        response_content = response.choices[0].message.content

        if not response or len(response_content.strip()) == 0:
            logging.error("Response content was empty.")
        
        return response_content

    def validate(self, conflict: Conflict) -> bool:
        """
        Validate whether the underlying dependency is a true dependency for a detected conflict.

        :param conflict: detected dependency conflict.
        :return: true if dependency else false.
        """
        logging.info("Validate dependency conflict.")

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

        dependency_counter = Counter
        for _ in range(self.repetition):
            response = self.generate(messages=messages)
            dependency_counter[response["isDependency"]] += 1

        dominant_is_dependency = dependency_counter.most_common(1)[0][0]

        return dominant_is_dependency



    