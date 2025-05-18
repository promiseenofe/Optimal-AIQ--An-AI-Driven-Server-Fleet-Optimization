import json
import os
from datetime import datetime
from environment import Environment
from optimization import optimize_fleet
from ai_failure_detection import AIFailureDetection

# Constants
OUTPUT_DIR = "output"
HISTORY_FILE = os.path.join(OUTPUT_DIR, "historical_results.json")

class FatigueTracker:
    def __init__(self, history_file):
        self.history_file = history_file
        self.cooldown_period = 3  # Number of runs to wait before allowing a buy action
        self.recent_failures = self.load_recent_failures()

    def load_recent_failures(self):
        if not os.path.exists(self.history_file):
            return {}
        with open(self.history_file, "r") as f:
            history = json.load(f)
        failures = {}
        for entry in history[-self.cooldown_period:]:
            for server, action in entry.get("optimized_server_actions", {}).items():
                if action == "sell":
                    failures[server] = failures.get(server, 0) + 1
        return failures

    def apply_cooldown(self, actions):
        adjusted_actions = {}
        for server, action in actions.items():
            if action == "buy" and self.recent_failures.get(server, 0) > 0:
                adjusted_actions[server] = "hold"
            else:
                adjusted_actions[server] = action
        return adjusted_actions

def save_results(results):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(results)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

    print(f"\nResults appended to {HISTORY_FILE}")

def main():
    env = Environment(
        demand_path="data/dynamic_demand.json",
        network_path="data/dynamic_network_logs.json",
        environment_path="data/dynamic_environment_logs.json",
        failure_path="data/dynamic_failure_logs.json"
    )

    optimized_solution = optimize_fleet(env)

    fatigue_tracker = FatigueTracker(HISTORY_FILE)
    adjusted_solution = fatigue_tracker.apply_cooldown(optimized_solution)

    print("Optimized Server Actions:", adjusted_solution)
    if not adjusted_solution:
        print("No buy/sell hold decisions were made! Check optimization logic.")
    else:
        for server, action in adjusted_solution.items():
            print(f"    - {server}: {action}")

    ai_detector = AIFailureDetection(
        "data/dynamic_failure_logs.json",
        "data/dynamic_network_logs.json",
        "data/dynamic_environment_logs.json"
    )
    ai_analysis = ai_detector.analyze_failures()
    print("\nAI Failure Analysis:\n", ai_analysis)

    network_impact_analysis = env.analyze_network_impact()
    network_impact = {"summary": network_impact_analysis} if isinstance(network_impact_analysis, str) else network_impact_analysis

    environmental_impact_analysis = env.analyze_environmental_impact()
    environmental_impact = {"summary": environmental_impact_analysis} if isinstance(environmental_impact_analysis, str) else environmental_impact_analysis

    print("\nNetwork Impact Analysis:\n", network_impact)
    print("\nEnvironmental Impact Analysis:\n", environmental_impact)

    save_results({
        "optimized_server_actions": adjusted_solution,
        "ai_failure_analysis": ai_analysis,
        "network_impact": network_impact,
        "environmental_impact": environmental_impact
    })
    # Save server actions with timestamp to a growing historical file
    server_actions_file = os.path.join(OUTPUT_DIR, "server_actions.json")
    timestamped_actions = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "buy": 0, "hold": 0, "sell": 0
    }
    for action in adjusted_solution.values():
        if action in timestamped_actions:
            timestamped_actions[action] += 1

    # Append to existing list or create new one
    if os.path.exists(server_actions_file):
        with open(server_actions_file, "r") as f:
            action_history = json.load(f)
            if not isinstance(action_history, list):
                action_history = [action_history]
    else:
        action_history = []

    action_history.append(timestamped_actions)

    with open(server_actions_file, "w") as f:
        json.dump(action_history, f, indent=4)

    print(f"📊 Server actions history updated at {server_actions_file}")

if __name__ == "__main__":
    main()
