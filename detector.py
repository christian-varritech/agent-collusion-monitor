#!/usr/bin/env python3
"""
Agent Collusion Detector
Scans agent logs for coordination signatures

Usage: python3 detector.py --logs /path/to/logs/*.jsonl
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

def load_logs(log_paths):
    """Parse JSONL agent logs from multiple files"""
    logs = []
    for path_pattern in log_paths:
        for path in Path('.').glob(path_pattern):
            try:
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
            except FileNotFoundError:
                print(f"Warning: {path} not found")
    return logs

def detect_session_collusion(logs):
    """Find same session_id across unrelated agents"""
    session_map = defaultdict(list)
    for log in logs:
        if 'session_id' in log:
            session_map[log['session_id']].append(log)
    
    collusion_events = []
    for session_id, entries in session_map.items():
        agent_types = set(e.get('agent_id', 'unknown') for e in entries)
        if len(agent_types) > 1:
            collusion_events.append({
                'type': 'SESSION_COLLUSION',
                'session_id': session_id,
                'agents': sorted(list(agent_types)),
                'count': len(entries),
                'timestamps': [e.get('timestamp', '') for e in entries]
            })
    return sorted(collusion_events, key=lambda x: x['count'], reverse=True)

def detect_timing_anomalies(logs, threshold_ms=100):
    """Find suspiciously fast responses on high-token tasks"""
    anomalies = []
    for log in logs:
        latency = log.get('response_latency_ms', float('inf'))
        tokens = log.get('token_usage', 0)
        if latency < threshold_ms and tokens > 1000:
            anomalies.append({
                'type': 'TIMING_ANOMALY',
                'agent_id': log.get('agent_id', 'unknown'),
                'latency_ms': latency,
                'tokens': tokens,
                'task_id': log.get('task_id', 'unknown'),
                'timestamp': log.get('timestamp', '')
            })
    return sorted(anomalies, key=lambda x: x['latency_ms'])

def detect_token_spikes(logs, threshold_multiplier=3.0):
    """Detect sudden token usage spikes suggesting multi-agent handoffs"""
    agent_tokens = defaultdict(list)
    for log in logs:
        agent_id = log.get('agent_id', 'unknown')
        tokens = log.get('token_usage', 0)
        agent_tokens[agent_id].append(tokens)
    
    spikes = []
    for agent_id, token_list in agent_tokens.items():
        if len(token_list) < 2:
            continue
        avg_tokens = sum(token_list) / len(token_list)
        for i, tokens in enumerate(token_list):
            if tokens > avg_tokens * threshold_multiplier:
                spikes.append({
                    'type': 'TOKEN_SPIKE',
                    'agent_id': agent_id,
                    'tokens': tokens,
                    'average': round(avg_tokens, 2),
                    'multiplier': round(tokens / avg_tokens, 2)
                })
    return sorted(spikes, key=lambda x: x['multiplier'], reverse=True)

def main():
    parser = argparse.ArgumentParser(description='Detect AI agent collusion patterns')
    parser.add_argument('--logs', nargs='+', required=True, help='Log file paths (supports glob patterns)')
    parser.add_argument('--timing-threshold', type=int, default=100, help='Latency threshold in ms')
    parser.add_argument('--token-multiplier', type=float, default=3.0, help='Token spike multiplier')
    args = parser.parse_args()
    
    logs = load_logs(args.logs)
    if not logs:
        print("❌ No logs loaded. Check file paths.")
        sys.exit(1)
    
    print(f"📊 Analyzed {len(logs)} log entries")
    print("=" * 60)
    
    # Run detections
    session_collusion = detect_session_collusion(logs)
    timing_anomalies = detect_timing_anomalies(logs, args.timing_threshold)
    token_spikes = detect_token_spikes(logs, args.token_multiplier)
    
    total_issues = len(session_collusion) + len(timing_anomalies) + len(token_spikes)
    
    if session_collusion:
        print(f"\n🚨 SESSION COLLUSION: {len(session_collusion)} events")
        for event in session_collusion[:5]:
            print(f"   Session {event['session_id'][:12]}...")
            print(f"   Agents: {', '.join(event['agents'])}")
            print(f"   Entries: {event['count']}")
    
    if timing_anomalies:
        print(f"\n⚠️  TIMING ANOMALIES: {len(timing_anomalies)} events")
        for anomaly in timing_anomalies[:5]:
            print(f"   {anomaly['agent_id']}: {anomaly['latency_ms']}ms for {anomaly['tokens']} tokens")
    
    if token_spikes:
        print(f"\n📈 TOKEN SPIKES: {len(token_spikes)} events")
        for spike in token_spikes[:5]:
            print(f"   {spike['agent_id']}: {spike['tokens']} tokens ({spike['multiplier']}x average)")
    
    print("\n" + "=" * 60)
    if total_issues > 0:
        print(f"💡 Found {total_issues} potential collusion signatures")
        print("   Recommendation: Audit flagged sessions manually")
        sys.exit(1)
    else:
        print("✅ No collusion signatures detected")
        sys.exit(0)

if __name__ == '__main__':
    main()
