import random

def optimize_fleet(env):
    optimized_actions = {}
    cooldown_tracker = {}
    cooldown_duration = 3  # Prevent immediate rebuy after failure for 3 cycles

    def get_sell_threshold(server, env):
        base = 0.05 + ((1 - server["reliability"]) * 0.30)
        env_conditions = env.get_environment_factor(server["server_id"])
        power_factor = 0.10 if env_conditions["power_stability"] in ["unstable", "critical, failed"] else 0
        cooling_factor = 0.05 if env_conditions["cooling_efficiency"] < 40 else 0
        temp_factor = min((env_conditions["temperature"] - 40) / 250, 0.10)
        return min(base + power_factor + cooling_factor + temp_factor, 0.90)

    def get_buy_threshold(server, env):
        base = 0.25 - (server["reliability"] * 0.20)
        failure_penalty = 0.10 if env.get_failure_rate(server["server_id"]) > 0.20 else 0
        demand_factor = 0.10 if env.get_demand_factor(server["server_id"]) > 150 else -0.05
        return max(base - failure_penalty + demand_factor, 0.05)

    def get_random_factor(server_id, env):
        net_conditions = env.get_network_factor(server_id)
        env_conditions = env.get_environment_factor(server_id)
        latency_weight = min(net_conditions["latency"] / 2000, 0.20)
        temp_weight = min(env_conditions["temperature"] / 150, 0.20)

        # Introduce sudden spikes
        if random.randint(1, 100) % random.randint(1, 50) == 0:
            latency_weight += random.uniform(0.2, 0.5)  # Simulating DDoS
            temp_weight += random.uniform(0.5, 1.0)  # Simulating HVAC failure

        return 0.25 + latency_weight + temp_weight

    for server_id, server in env.servers.items():
        failure_rate = env.get_failure_rate(server_id)
        network_latency = env.get_network_factor(server_id)["latency"]
        temperature = env.get_environment_factor(server_id)["temperature"]
        cost = server["cost"]

        if server_id in cooldown_tracker and cooldown_tracker[server_id] > 0:
            cooldown_tracker[server_id] -= 1
            optimized_actions[server_id] = "hold"
            continue

        sell_threshold = get_sell_threshold(server, env)
        buy_threshold = get_buy_threshold(server, env)
        random_factor = get_random_factor(server_id, env)

        if (failure_rate > sell_threshold and cost > 15) or (network_latency > 400 and temperature > 55):
            action = "sell"
            cooldown_tracker[server_id] = cooldown_duration
        elif (server["reliability"] > buy_threshold and cost < 30 and network_latency < 250 and temperature < 50) or random.random() < random_factor:
            action = "buy"
        else:
            action = random.choices(["hold", "buy", "sell"], weights=[0.3, 0.4, 0.3])[0]

        optimized_actions[server_id] = action

        print(f"Server {server_id}: Failure Rate = {failure_rate:.2f}, Cost = {cost}, "
              f"Latency = {network_latency}ms, Temperature = {temperature}°C, Action = {optimized_actions[server_id]}")

    print("\n🔍 Final Optimized Actions:", optimized_actions)

    return optimized_actions
