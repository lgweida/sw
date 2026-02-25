import json
from typing import Dict, List, Optional, Tuple, Any

def get_adapter_sessions(
    adapter_routing_path: str,
    grouped_sessions_path: str
) -> List[Dict[str, Any]]:
    """
    For each adapter in adapter_routing.json, retrieve the matching session
    from grouped_sessions.json and extract its start/stop timer information.

    Args:
        adapter_routing_path: Path to adapter_routing.json.
        grouped_sessions_path: Path to grouped_sessions.json.

    Returns:
        A list of dictionaries, each containing:
            - network: from adapter entry
            - adapter: adapter name
            - broker_code: broker code
            - session_name: name of the session (if found)
            - start_trigger: cron expression for session start (or None)
            - start_timezone: timezone for start (or None)
            - stop_trigger: cron expression for session stop (or None)
            - stop_timezone: timezone for stop (or None)
            - note: optional note if session not found
    """
    # Load JSON files
    with open(adapter_routing_path, 'r') as f:
        adapters = json.load(f)

    with open(grouped_sessions_path, 'r') as f:
        grouped = json.load(f)

    # Build a mapping from session name to the full session dictionary
    session_map: Dict[str, Dict] = {}
    for category, sessions in grouped.items():
        for sess in sessions:
            sess_name = sess["session"]["name"]
            session_map[sess_name] = sess

    def extract_timers(session: Dict) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Extract start and stop cron triggers and timezones from a session's timer blocks.
        Returns (start_trigger, start_tz, stop_trigger, stop_tz).
        """
        start_trigger = start_tz = None
        stop_trigger = stop_tz = None

        print(session['routing']['destination'], session['session']['name'])

        for key, value in session.items():
            if key.startswith("timers/") and isinstance(value, dict):
                trigger = value.get("trigger")
                tz = value.get("timezone")
                action = value.get("action", "")
                if trigger and tz:
                    if "doStart" in action:
                        start_trigger, start_tz = trigger, tz
                    if "doStop" in action:
                        stop_trigger, stop_tz = trigger, tz
        return start_trigger, start_tz, stop_trigger, stop_tz

    results = []
    for entry in adapters:
        network = entry.get("network")
        adapter_name = entry.get("adapter")
        broker_code = entry.get("broker_code")

        # If adapter is "*", there is no exact match; we record it as not found.
        if adapter_name == "*":
            results.append({
                "network": network,
                "adapter": adapter_name,
                "broker_code": broker_code,
                "session_name": None,
                "start_trigger": None,
                "start_timezone": None,
                "stop_trigger": None,
                "stop_timezone": None,
                "routing_destination": None,
                "note": "Wildcard adapter – no specific session"
            })
            continue

        session = session_map.get(adapter_name)
        if not session:
            results.append({
                "network": network,
                "adapter": adapter_name,
                "broker_code": broker_code,
                "session_name": None,
                "start_trigger": None,
                "start_timezone": None,
                "stop_trigger": None,
                "stop_timezone": None,
                "routing_destination": None,
                "note": "Session not found"
            })
            continue

        start_trig, start_tz, stop_trig, stop_tz = extract_timers(session)
        dest = session.get("routing", {}).get("destination")
        results.append({
            "network": network,
            "adapter": adapter_name,
            "broker_code": broker_code,
            "session_name": adapter_name,
            "start_trigger": start_trig,
            "start_timezone": start_tz,
            "stop_trigger": stop_trig,
            "stop_timezone": stop_tz,
            "routing_destination": dest
        })

    return results

if __name__ == "__main__":
    adapter_info = get_adapter_sessions("adapter_routing.json", "grouped_sessions.json")
    for info in adapter_info:
        print(info)