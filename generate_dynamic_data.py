import json
import random
from datetime import datetime

# Constants
NUM_SERVERS = 10
NUM_TIME_STEPS = 10
SERVERS = [f"s{i+1}" for i in range(NUM_SERVERS)]

# Helper function to generate random values within a range
def random_value(min_val, max_val, decimal_places=2):
    return round(random.uniform(min_val, max_val), decimal_places)

# Generate dynamic demand data
def generate_demand():
    demand = {"server_demand": {}}
    for time_step in range(1, NUM_TIME_STEPS + 1):
        demand["server_demand"][str(time_step)] = {
            server: random_value(10, 300) for server in SERVERS
        }
    return demand

# Generate dynamic network logs with realistic fluctuations and occasional spikes
def generate_network_logs():
    network_logs = {"time_steps": {}}
    for time_step in range(NUM_TIME_STEPS):
        spike = (random.randint(1, 100) % 5 == 0)  # 20% chance of sudden spike
        network_logs["time_steps"][str(time_step)] = {
            "packet_loss": random_value(0.1, 30.0 if not spike else 60.0),
            "latency": random_value(50, 1500 if not spike else 3000),
            "network_outages": random.randint(0, 15 if not spike else 30),
            "bandwidth_usage": random_value(50, 100),
        }
    return network_logs

# Generate dynamic environmental logs with fluctuations and sudden HVAC malfunction
def generate_environment_logs():
    environment_logs = {"time_steps": {}}
    base_temp = random_value(40, 60)  # Baseline temperature

    for time_step in range(NUM_TIME_STEPS):
        temp_variation = random_value(-5, 5)
        hvac_malfunction = (random.randint(1, 100) % 7 == 0)  # 15% chance of malfunction
        power_state = random.choices(["stable", "unstable", "critical, failed"], weights=[0.7, 0.2, 0.1])[0]

        environment_logs["time_steps"][str(time_step)] = {
            "temperature": round(base_temp + temp_variation + (15 if hvac_malfunction else 0), 2),
            "humidity": random_value(30, 100),
            "power_stability": power_state,
            "cooling_efficiency": random_value(10, 100),
        }
    return environment_logs

# Generate dynamic failure logs with cooldown period handling
def generate_failure_logs():
    failure_logs = {}
    cooldown_tracker = {server: 0 for server in SERVERS}  # Cooldown state for each server

    for time_step in range(1, NUM_TIME_STEPS + 1):
        failure_logs[str(time_step)] = {}
        for server in SERVERS:
            if cooldown_tracker[server] > 0:
                failure_logs[str(time_step)][server] = False
                cooldown_tracker[server] -= 1  # Reduce cooldown period
            else:
                failure_occurred = random.choices([True, False], weights=[0.2, 0.8])[0]
                failure_logs[str(time_step)][server] = failure_occurred
                if failure_occurred:
                    cooldown_tracker[server] = 2  # Apply 2-step cooldown
    return failure_logs

# Generate dynamic server configurations
def generate_servers():
    servers = {}
    for server in SERVERS:
        servers[server] = {
            "server_id": server,
            "reliability": round(random.uniform(0.7, 0.99), 2),
            "cost": round(random.uniform(10, 50), 2),
            "latency": round(random.uniform(50, 500), 2),
        }
    return {"servers": servers}

# Save generated data to JSON files
def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Main function to generate and save all data
def main():
    # Generate data
    demand_data = generate_demand()
    network_data = generate_network_logs()
    environment_data = generate_environment_logs()
    failure_data = generate_failure_logs()
    server_data = generate_servers()

    # Merge server data with demand
    demand_data.update(server_data)

    # Save data to JSON files
    save_to_json(demand_data, "data/dynamic_demand.json")
    save_to_json(network_data, "data/dynamic_network_logs.json")
    save_to_json(environment_data, "data/dynamic_environment_logs.json")
    save_to_json(failure_data, "data/dynamic_failure_logs.json")

    print("\u2705 Dynamic data generated and saved successfully!")

if __name__ == "__main__":
    main()