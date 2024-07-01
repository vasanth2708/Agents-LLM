import asyncio
import json
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel
from researcher.config import Config
from researcher.utils.llm import create_chat_completion
from researcher.researcher.research import GoogleBard


previous_queries = []

class GPTResearcher:
    """GPT Researcher"""

    def __init__(self, query: str, report_type: str = None, report_source=None, source_urls=None, config_path=None, websocket=None, verbose: bool = True):
        self.query: str = query
        self.report_type: str = report_type
        self.report_source: str = report_source
        self.source_urls = source_urls
        self.verbose: bool = verbose
        self.websocket = websocket
        self.cfg = Config(config_path)
        self.agent = None
        self.context = []
        self.type: str = ""
        
    async def conduct_research(self):
        response = await self.get_gpt_response(self.query, self.context)
        return response
    
    async def researcher_openai(self):
        return await self.get_suggestions()
    
    async def researcher_bard(self):
        return await GoogleBard().generate(self.summary_prompt())
    
    async def get_gpt_response(self, pqueries, context):
        messages = [
            {"role": "system", "content": self.auto_questions()},
            {"role": "user", "content": self.generate_response_prompt(pqueries, context)}
        ]
        try:
            response = await create_chat_completion(
                model=self.cfg.smart_llm_model,
                messages=messages,
                temperature=0.7,
                llm_provider=self.cfg.llm_provider,
                stream=True,
                max_tokens=self.cfg.smart_token_limit,
                llm_kwargs=self.cfg.llm_kwargs
            )
            response_data = json.loads(response)
            return response_data["QuestionTask"]
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e} - Response received: '{response}'")
            return {}
        
    async def get_suggestions(self):
        try:
            messages = [
                {"role": "system", "content": "Provide Deep Research."},
                {"role": "user", "content": self.summary_prompt()}
            ]
            response = await create_chat_completion(
                model=self.cfg.smart_llm_model,
                messages=messages,
                temperature=0.7,
                llm_provider=self.cfg.llm_provider,
                stream=True,
                max_tokens=self.cfg.smart_token_limit,
                llm_kwargs=self.cfg.llm_kwargs
            )
            response_data = json.loads(response)
            return response_data
        except Exception as e:
            print(f"Error in get_suggestions: {e}")
            return
        
    def generate_response_prompt(self, query, context):
        context_str = "\n".join(context)
        prompt = f"Query: {query}\n\nContext:\n{context_str}\n\n. You are a Expert - {self.agent[0]}, Provide a detailed response including tasks, objectives, task updates, task types, milestones, and estimates."
        return prompt
    
    def summary_prompt(self):
        return f"You are a Expert - {self.agent[0]}. Detailed Research based on the User Conversation - {self.query}"
    
    def auto_questions(self):
        return """
            Your task is to generate questions based on user query to get more details from User
            examples:
            task: "should I invest in apple stocks?"
            response: 
            {
                "QuestionTask": [
                    {
                        "question": "Why do you want to invest in Apple?",
                        "answer": "string",
                        "answer_type_code": "TEXT" # List of types[ INT, FLOAT, TEXT, STRING, BOOLEAN, SINGLE_CHOICE, MULTI_CHOCIE ]
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": [],
                        "input_text": "Please enter the amount you are planning to invest in Apple.",
                        "validation": "required|min:1"
                    },
                    {
                        "question": "How much are you planning to invest in Apple?",
                        "answer": "number",
                        "answer_type_code": "INT" # List of types[ INT, FLOAT, TEXT, STRING, BOOLEAN, SINGLE_CHOICE, MULTI_CHOCIE ]
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": [],
                        "input_text": "Please enter the amount you are planning to invest in Apple.",
                        "validation": "required|min:1"
                    },
                    {
                        "question": "What is your investment horizon?",
                        "answer": "string",
                        "answer_type_code": "MULTI_CHOICE" # List of types[ INT, FLOAT, TEXT, STRING, BOOLEAN, SINGLE_CHOICE, MULTI_CHOCIE ]
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": ["Short-term (less than 1 year)", "Medium-term (1-5 years)", "Long-term (more than 5 years)"],
                        "other": "Please select one of the options that best describes your investment horizon."
                    },
                    {
                        "question": "What is your risk tolerance?",
                        "answer": "string",
                        "answer_type_code": "MULTI_CHOICE" # List of types[ INT, FLOAT, TEXT, STRING, BOOLEAN, SINGLE_CHOICE, MULTI_CHOCIE ]
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": ["Low", "Moderate", "High"],
                        "other": "Please select your risk tolerance level."
                    }
                ]
            }
                        
            task: "should I buy a house in San Francisco?"
            response: 
            {
                "QuestionTask": [
                    {
                        "question": "Why do you want to buy a house in San Francisco?",
                        "answer": "string",
                        "answer_type_code": "input based",
                        "input_text": "Please provide your reason for wanting to buy a house in San Francisco.",
                        "validation": "required"
                    },
                    {
                        "question": "What is your budget for buying a house?",
                        "answer": "number",
                        "answer_type_code": "input based",
                        "input_text": "Please enter your budget for buying a house in San Francisco.",
                        "validation": "required|min:1"
                    },
                    {
                        "question": "What type of property are you looking for?",
                        "answer": "string",
                        "answer_type_code": "option based",
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": ["Condo", "Single Family Home", "Townhouse", "Multi-Family Home"],
                        "other": "Please select the type of property you are interested in."
                    },
                    {
                        "question": "What is your timeline for purchasing?",
                        "answer": "string",
                        "answer_type_code": "option based",
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": ["Immediately", "Within 6 months", "Within 1 year", "More than 1 year"],
                        "other": "Please select your purchasing timeline."
                    }
                    {
                        
                        "question": "What is your timeline for purchasing?",
                        "answer": "BOOLEAN",
                        "answer_type_code": "option based",
                        "prefix": Answer Prefix if there is anything defaultValue or options list,
                        "suffix": Answer Suffix if there is anything defaultValue or options list,
                        "options": ["True","False"],
                        "other": "Please select your purchasing timeline."
                    }
                ]
            }
        """
    async def stream_output(self, type, output, websocket=None, logging=True):
        if logging:
            print(output)
        if websocket:
            await websocket.send_json({"type": type, "output": output})