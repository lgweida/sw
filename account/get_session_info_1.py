import json
import re
from typing import Dict, List, Optional, Tuple, Any
import convert_time

def load_properties(filepath: str) -> Dict[str, str]:
    """
    Load a Java-style properties file into a dictionary.
    Lines starting with '#' or '!' are ignored, as are blank lines.
    Key-value pairs are separated by '=' or ':'.
    Leading/trailing whitespace is stripped.
    """
    props = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in ('#', '!'):
                continue
            # Look for first '=' or ':'
            sep = line.find('=')
            if sep == -1:
                sep = line.find(':')
            if sep == -1:
                continue  # malformed line, skip
            key = line[:sep].strip()
            value = line[sep+1:].strip()
            props[key] = value
    return props

def substitute_placeholders(value: Any, props: Dict[str, str]) -> Any:
    """
    If value is a string of the form ${key}, replace it with props[key].
    Otherwise return value unchanged.
    """
    if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
        key = value[2:-1]  # remove ${ and }
        return props.get(key, value)  # if key not found, keep original
    return value

def get_adapter_sessions(
    adapter_routing_path: str,
    grouped_sessions_path: str,
    properties_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    For each adapter in adapter_routing.json, retrieve the matching session
    from grouped_sessions.json and extract its start/end timer information
    and session-level identifiers. If a properties file is provided, any
    placeholders (${...}) in the extracted fields are replaced with the
    corresponding property values.

    Args:
        adapter_routing_path: Path to adapter_routing.json.
        grouped_sessions_path: Path to grouped_sessions.json.
        properties_path: Optional path to the .properties file.

    Returns:
        A list of dictionaries, each containing:
            - network: from adapter entry
            - adapter: adapter name
            - broker_code: broker code
            - session_name: name of the session (if found)
            - session_sendercompid: SenderCompID from the session (or None)
            - session_targetcompid: TargetCompID from the session (or None)
            - start_time: cron expression for session start (or None)
            - start_timezone: timezone for start (or None)
            - end_time: cron expression for session stop (or None)
            - end_timezone: timezone for stop (or None)
            - note: optional note if session not found or wildcard
    """
    # Load JSON files
    with open(adapter_routing_path, 'r') as f:
        adapters = json.load(f)

    with open(grouped_sessions_path, 'r') as f:
        grouped = json.load(f)

    # Load properties if provided
    props = {}
    if properties_path:
        props = load_properties(properties_path)

    # Build a mapping from session name to the full session dictionary
    session_map: Dict[str, Dict] = {}
    for category, sessions in grouped.items():
        for sess in sessions:
            sess_name = sess["session"]["name"]
            session_map[sess_name] = sess

    def extract_timers(session: Dict) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Extract start and end cron triggers and timezones from a session's timer blocks.
        Returns (start_time, start_tz, end_time, end_tz).
        """
        start_time = start_tz = None
        end_time = end_tz = None

        for key, value in session.items():
            if key.startswith("timers/") and isinstance(value, dict):
                trigger = value.get("trigger")
                tz = value.get("timezone")
                action = value.get("action", "")
                if trigger and tz:
                    if "doStart" in action:
                        start_time, start_tz = trigger, tz
                    if "doStop" in action:
                        end_time, end_tz = trigger, tz
        return start_time, start_tz, end_time, end_tz

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
                "session_sendercompid": None,
                "session_targetcompid": None,
                "start_time": None,
                "start_timezone": None,
                "end_time": None,
                "end_timezone": None,
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
                "session_sendercompid": None,
                "session_targetcompid": None,
                "start_time": None,
                "start_timezone": None,
                "end_time": None,
                "end_timezone": None,
                "note": "Session not found"
            })
            continue

        # Extract session-level fields
        session_dict = session.get("session", {})
        sendercompid = session_dict.get("sendercompid")
        targetcompid = session_dict.get("targetcompid")

        start_time, start_tz, end_time, end_tz = extract_timers(session)

        # Substitute placeholders if properties were loaded
        if props:
            sendercompid = substitute_placeholders(sendercompid, props)
            targetcompid = substitute_placeholders(targetcompid, props)
            # Note: timers are not placeholders, but we still apply substitution just in case
            start_time = substitute_placeholders(start_time, props)
            start_tz = substitute_placeholders(start_tz, props)
            end_time = substitute_placeholders(end_time, props)
            end_tz = substitute_placeholders(end_tz, props)

        results.append({
            "network": network,
            "adapter": adapter_name,
            "broker_code": broker_code,
            "session_name": adapter_name,
            "session_sendercompid": sendercompid,
            "session_targetcompid": targetcompid,
            "start_time": convert_time.parse_cron_expression(start_time) if start_time else None,
            "start_timezone": start_tz,
            "end_time": convert_time.parse_cron_expression(end_time) if end_time else None,
            "end_timezone": end_tz
        })

    return results

if __name__ == "__main__":
    adapter_info = get_adapter_sessions(
        "adapter_routing.json",
        "grouped_sessions.json",
        "prd-mizuho-gold_ulbridge.properties"
    )
    for info in adapter_info:
        print(info)

    # Export to a JSON file
    output_file = "adapter_sessions_output.json"
    with open(output_file, "w") as f:
        json.dump(adapter_info, f, indent=2)
    
    print(f"Exported {len(adapter_info)} adapter entries to {output_file}")