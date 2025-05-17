import json
import os
import re
from collections import Counter

HISTORY_FILE = "output/historical_results.json"
ALL_SERVERS = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"}

def extract_servers_from_text(text, patterns):
    """Extracts server identifiers from AI-generated failure analysis."""
    found_servers = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            found_servers.update(re.findall(r"s\d+", match))  # Extract "s1", "s2", etc.
    return found_servers

def analyze_failure_trends():
    """Analyzes historical failure trends from AI-generated failure logs."""
    if not os.path.exists(HISTORY_FILE):
        print("\n⚠️ No historical results found. Run main.py first to generate data.")
        return

    with open(HISTORY_FILE, "r") as f:
        try:
            history = json.load(f)
            if not history:
                print("\n📂 Historical file is empty. No failure data to analyze.")
                return
        except json.JSONDecodeError:
            print("\n❌ Error: Unable to parse historical results file. Check JSON format.")
            return

    # Track failure counts, actions, and trends
    failure_counts = Counter()
    action_counts = Counter()
    network_issues = []
    environmental_issues = []

    for entry in history:
        # Track server actions (buy/sell/hold)
        actions = entry.get("optimized_server_actions", {})
        for server, action in actions.items():
            action_counts[(server, action)] += 1

        # Track failures from AI analysis
        ai_analysis = entry.get("ai_failure_analysis", "")
        operational_patterns = [
            r'servers? ([s\d,\s]+) are operating fine',
            r'servers? ([s\d,\s]+) are up and running',
            r'servers? ([s\d,\s]+) are functional',
            r'servers? ([s\d,\s]+) are online'
        ]
        failure_patterns = [
            r'the failed servers are: ([s\d,\s]+)',
            r'servers? ([s\d,\s]+) (?:have|has) failed',
            r'servers? ([s\d,\s]+) are down',
            r'servers? ([s\d,\s]+) experienced issues',
            r'servers? ([s\d,\s]+) are not operational',
            r'servers? ([s\d,\s]+) (?:encountered|had) failures?',
            r'servers? ([s\d,\s]+) (?:became|were) non-functional'
        ]

        operational_servers = extract_servers_from_text(ai_analysis, operational_patterns)
        failed_servers = extract_servers_from_text(ai_analysis, failure_patterns)

        # Infer failures if operational servers are listed but failures are not
        if operational_servers and not failed_servers:
            failed_servers = ALL_SERVERS - operational_servers

        # Count failure occurrences
        for server in failed_servers:
            failure_counts[server] += 1

    # Track network and environmental issues
    network_impact = entry.get("network_impact", "")
    environmental_impact = entry.get("environmental_impact", {})

    # ✅ Fix: Ensure environmental_impact is a dictionary
    if isinstance(environmental_impact, str):  
        try:
            environmental_impact = json.loads(environmental_impact)  # Convert from string to dictionary
        except json.JSONDecodeError:
            environmental_impact = {}  # Fallback if conversion fails
            
    if isinstance(network_impact, str):
        try:
            network_impact = json.loads(network_impact)  # Convert from string to dictionary
        except json.JSONDecodeError:
            network_impact = {}  # Fallback if conversion fails

    for server, impact in environmental_impact.items():
        if isinstance(impact, dict) and impact.get("Temperature", "").lower() == "high":
            environmental_issues.append((server, entry.get("timestamp")))

    # Display Results
    print("\n" + "=" * 40)
    print("      🔍 HISTORICAL TREND ANALYSIS")
    print("=" * 40)

    # Server Actions
    print("\n📊 Server Actions (Buy/Sell/Hold):")
    for (server, action), count in action_counts.items():
        print(f"   - {server}: {action} {count} time{'s' if count > 1 else ''}")

    # Failure Trends
    print("\n🔴 Failure Occurrences per Server:")
    for server, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
        print(f"   - {server}: failed {count} time{'s' if count > 1 else ''}")

    # Network Issues
    if network_issues:
        print("\n🌐 Network Issues Detected:")
        for timestamp in network_issues:
            print(f"   - {timestamp}")
    else:
        print("\n🌐 No significant network issues detected.")

    # Environmental Issues
    if environmental_issues:
        print("\n🌡️ Environmental Issues Detected:")
        for server, timestamp in environmental_issues:
            print(f"   - Server {server} had high temperature on {timestamp}")
    else:
        print("\n🌡️ No significant environmental issues detected.")

    print("\n📌 End of Historical Trend Analysis")
    print("=" * 40 + "\n")

if __name__ == "__main__":
    analyze_failure_trends()