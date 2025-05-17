import json
import os
import random

class Environment:
    def __init__(self, demand_path="data/dynamic_demand.json", network_path="data/dynamic_network_logs.json",
                 environment_path="data/dynamic_environment_logs.json", failure_path="data/dynamic_failure_logs.json"):
        """Load dynamically generated data from separate files."""
        self.failure_history = {}
        self.environment_conditions = {}
        self.network_conditions = {}
        self.server_demand = {}
        self.servers = {}  # ✅ Fix: Define servers

        # Load each dataset if the file exists
        self.load_demand(demand_path)
        self.load_network(network_path)
        self.load_environment(environment_path)
        self.load_failures(failure_path)

    def load_demand(self, path):
        """Load demand data (which may include server configurations)."""
        if os.path.exists(path):
            with open(path, "r") as file:
                data = json.load(file)
                self.server_demand = data.get("server_demand", {})
                self.servers = data.get("servers", {})  # ✅ Fix: Store server info
        else:
            print(f"⚠️ Warning: Demand file '{path}' not found. Using defaults.")

    def load_network(self, path):
        """Load network conditions."""
        if os.path.exists(path):
            with open(path, "r") as file:
                self.network_conditions = json.load(file)
        else:
            print(f"⚠️ Warning: Network file '{path}' not found. Using defaults.")

    def load_environment(self, path):
        """Load environmental conditions."""
        if os.path.exists(path):
            with open(path, "r") as file:
                self.environment_conditions = json.load(file)
        else:
            print(f"⚠️ Warning: Environment file '{path}' not found. Using defaults.")

    def load_failures(self, path):
        """Load failure history."""
        if os.path.exists(path):
            with open(path, "r") as file:
                self.failure_history = json.load(file)
        else:
            print(f"⚠️ Warning: Failure file '{path}' not found. Using defaults.")

    def get_environment_factor(self, server_id):
        """Retrieve environmental factors with slight variations."""
        env_data = self.environment_conditions.get(server_id, {
            "temperature": 50, "humidity": 50, "power_stability": "stable", "cooling_efficiency": 80
        })
       
        # Introduce slight variations for unpredictability
        env_data["temperature"] += random.uniform(-5, 5)  
        env_data["cooling_efficiency"] += random.uniform(-5, 5)
       
        return env_data

    def get_network_factor(self, server_id):
        """Retrieve network conditions from loaded data."""
        return self.network_conditions.get(server_id, {
            "latency": 100, "packet_loss": 5, "network_outages": 0
        })

    def get_failure_rate(self, server_id):
        """Retrieve failure rate based on historical failures with random variability."""
        failure_history = self.failure_history.get(server_id, [])
        if not failure_history:
            return round(random.uniform(0.01, 0.05), 2)  # Introduce randomness in default failure rate

        recent_failures = sum(failure_history[-10:]) / max(len(failure_history[-10:]), 1)
        variability = random.uniform(-0.02, 0.02)  # Add slight randomness
        return round(min(0.4, recent_failures + 0.05 + variability), 2)

    def get_demand_factor(self, server_id):
        """Retrieve server demand."""
        return self.server_demand.get(server_id, 100)  # Default moderate demand

    def analyze_network_impact(self):
        """Analyze network conditions and return insights as a dictionary."""
        network_issues = {}

        for server_id, network_data in self.network_conditions.items():
            issues = []
            latency = network_data.get("latency", 0)
            packet_loss = network_data.get("packet_loss", 0)
            outages = network_data.get("network_outages", 0)

            if latency > 200:
                issues.append(f"⚠️ High latency ({latency}ms) → Consider delaying purchases.")
            if packet_loss > 5:
                issues.append(f"⚠️ High packet loss ({packet_loss}%) → Favor selling unreliable servers.")
            if outages >= 3:
                issues.append(f"⚠️ Multiple outages ({outages} in 24h) → Scale down.")

            if issues:
                network_issues[server_id] = issues  # Store issues per server

        return network_issues if network_issues else {"summary": "✅ Network conditions are stable."}

    def analyze_environmental_impact(self):
        """Analyze environmental conditions and return insights as a dictionary."""
        environmental_issues = {}

        for server_id, env_data in self.environment_conditions.items():
            issues = []
            temperature = env_data.get("temperature", 50)  # Default 50°C if missing
            cooling_efficiency = env_data.get("cooling_efficiency", 100)  # Default 100% if missing
            power_stability = env_data.get("power_stability", "stable")  # Default stable

            if temperature > 75:
                issues.append(f"🔥 High temperature ({temperature}°C) → Risk of overheating!")
            if cooling_efficiency < 50:
                issues.append(f"❄️ Low cooling efficiency ({cooling_efficiency}%) → Needs better airflow.")
            if power_stability in ["unstable", "critical, failed"]:
                issues.append(f"⚡ Power instability ({power_stability}) → Risk of sudden shutdown.")

            if issues:
                environmental_issues[server_id] = issues  # Store issues per server

        return environmental_issues if environmental_issues else {"summary": "✅ Environmental conditions are stable."}