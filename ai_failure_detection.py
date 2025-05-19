import openai
import json
import time
import os
from openai._exceptions import RateLimitError


# Use environment variable for safety
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIFailureDetection:
    def __init__(self, failure_logs_path, network_logs_path=None, environment_logs_path=None):
        with open(failure_logs_path, "r") as f:
            self.failure_logs = json.load(f)

        self.network_logs = {}
        self.environment_logs = {}

        if network_logs_path and os.path.exists(network_logs_path):
            with open(network_logs_path, "r") as f:
                self.network_logs = json.load(f)

        if environment_logs_path and os.path.exists(environment_logs_path):
            with open(environment_logs_path, "r") as f:
                self.environment_logs = json.load(f)

    def analyze_failures(self, max_retries=5):
        # Limit the size of the logs sent to GPT
        failure_data = self.failure_logs[-10:] if len(self.failure_logs) > 10 else self.failure_logs

        prompt = (
            "You are an AI analyzing server failures. Below are the failure logs, network conditions, and environmental conditions:\n\n"
            f"Failure Logs:\n{json.dumps(failure_data, indent=2)}\n\n"
            f"Network Conditions:\n{json.dumps(self.network_logs, indent=2)}\n\n"
            f"Environmental Conditions:\n{json.dumps(self.environment_logs, indent=2)}\n\n"
            "Analyze the failures and provide actionable insights. Consider:\n"
            "1. Which servers are failing most frequently?\n"
            "2. Any patterns (time, network, environment)?\n"
            "3. Recommendations to reduce failures.\n"
            "4. Correlations across logs?\n"
            "Structure your answer with clear observations and action points."
        )

        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an AI analyzing server failures."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response["choices"][0]["message"]["content"]

            except RateLimitError:
                wait_time = 2 ** attempt
                print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt + 1})")
                time.sleep(wait_time)

            except Exception as e:
                return f"Error analyzing failures: {str(e)}"

        return "Error: Maximum retry attempts reached due to rate limiting."

if __name__ == "__main__":
    ai_detector = AIFailureDetection(
        failure_logs_path="data/dynamic_failure_logs.json",
        network_logs_path="data/dynamic_network_logs.json",
        environment_logs_path="data/dynamic_environment_logs.json"
    )
    print(ai_detector.analyze_failures())
