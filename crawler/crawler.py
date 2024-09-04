from groq import Groq
from utils import utils
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from pandas import DataFrame
import time

load_dotenv()


class MultipleChoiceQuestion(BaseModel):
    question: str
    A: str
    B: str
    C: str
    D: str
    answer: str
    reasoning: str


class GroqModel:
    def __init__(self, model="llama3-8b-8192", temperature=0, max_tokens=5000):
        self.model = model
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
            max_retries=3,
            timeout=120.0,
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.chat_history = []

    def __call__(self, prompt, role=None):
        """
        Generate a response from the model based on the prompt and role.

        Parameters:
        prompt (str): The prompt to generate a response for.
        role (str): The role of the prompt, either 'user' or 'system'.

        Returns:
        str: The response from the model.
        """
        if role:
            self.chat_history.append({"role": role, "content": prompt})
        response = self.client.chat.completions.create(
            messages=self.chat_history,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        self.chat_history.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

    def set_system_prompt(self, system_prompt):
        self.chat_history.append({"role": "system", "content": system_prompt})

    def generate(self, prompt, system="You are an AI assistant"):
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            stream=False,
        )
        return response.choices[0].message.content


class Crawler:
    def __init__(self, url_list, model_name, site="vietjack_com"):
        self.url_list = url_list
        self.model = GroqModel(model_name)
        self.site = site
        self.question_store = []
        self.question_final = []
        self.system_prompt = f"""You are a Vietnamese AI expert with a specialization in HTML and LaTeX. Your task is to modify a multiple-choice question represented as a JSON object according to the following steps:
        1. Convert Math Formulas: Identify all mathematical formulas within the content, the HTML math tags and convert them to LaTeX format, ensuring the syntax is accurate.
        2. Remove HTML Tags: Strip all HTML tags, MathML namespaces from the content to retain only plain text.
        3. Clean Question Content: In the 'question' field, retain only the core content of the question. For example, transform "Câu 1. <Question's content>" to "<Question's content>". If no question content is present, set this field to an empty string.
        4. Clean Choice Content: For each choice (A, B, C, etc.), retain only the actual content. For example, change "A. 2" to "2". If a choice's content is missing, set that field to an empty string.
        5. Extract Correct Answer: In the 'answer' field, extract and keep only the letter corresponding to the correct answer. For instance, from "Đáp án đúng là A vì 1+1=1", it should be "A". If the correct answer is absent, set this field to an empty string.
        6. Add Reasoning: Introduce a 'reasoning' field in the JSON object that contains the explanation of the answer. For example, split "Đáp án đúng là A vì 1+1=1" into "answer": "A" and "reasoning": "1+1=1". If reasoning is not provided, set this field to an empty string, ensuring that the reasoning aligns with the extracted answer.
        7. Grammar and Spelling Check: Review the content for Vietnamese grammar and spelling, correcting any errors identified.
        The final JSON object must conform to the schema outlined in: {json.dumps(MultipleChoiceQuestion.model_json_schema(), indent=2)}."""

    def get_quest(self, url):
        print(f"Getting questions from {url}...")
        soup = utils.fetch_soup(url)
        quest = utils.fetch_quest(soup, self.site)
        print(f"Got {len(quest)} questions from {url}.")
        self.question_store.extend(quest)

    def get_all_quest(self):
        print("Getting all questions from the given urls...")
        for url in self.url_list:
            self.get_quest(url)

    def reformat_quest(self, quest):
        dump = str(quest)
        try:
            response = self.model.generate(dump, self.system_prompt)
            json_response = json.loads(response)
            print("------------------ADDED-------------------")
            print(json_response)
            print("---------------------------------\n\n")
        except Exception as e:
            print(e.message)
            return None
        self.question_final.append(json_response)

    def reformat_all_quest(self):
        print("Reformatting all questions...")
        for quest in self.question_store:
            try:
                self.reformat_quest(quest)
            except Exception as e:
                print(e)
                print("Waiting for 100 seconds...")
                time.sleep(100)
                self.reformat_quest(quest)

    def crawl(self):
        self.get_all_quest()
        self.reformat_all_quest()

    def save(self, path):
        data = [question for question in self.question_final if question is not None]
        df = DataFrame(
            data, columns=["question", "A", "B", "C", "D", "answer", "reasoning"]
        )
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"Saved {len(df)} questions to {path}.")
