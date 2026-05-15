import json

from openai import OpenAI

class AIAnalyzer:
    def __init__(self, api_key: str):
        print("OPEN AI : ", api_key)
        self.client = OpenAI(api_key=api_key)

    def analyze_mr(self, mr_data, mr_diff):
        # Combine code diffs and MR description
        diff_text = "\n".join([diff["diff"] for diff in mr_diff])
        prompt = (
            f"As a senior software developer, review the following GitLab Merge Request:\n"
            f"MR Title: {mr_data['title']}\n"
            f"Description: {mr_data['description']}\n"
            f"Code Changes:\n```diff\n{diff_text}\n```\n"
            f"Provide feedback on performance, readability, potential bugs, and design.\n"
            f"Return the output as JSON in the following format:\n"
            f'{{"summary": "summary", "positives": "positive points", "suggestions": "improvement suggestions"}}'
        )

        # Analyze with OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Recommended model, alternative: "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a senior developer performing code analysis."},
                {"role": "user", "content": prompt}
            ],
        )

        # Get the analysis result in JSON format
        analysis_json = response.choices[0].message.content
        cleaned_analysis_json = analysis_json.strip('`').replace('json\n', '', 1).strip()

        return json.loads(cleaned_analysis_json)