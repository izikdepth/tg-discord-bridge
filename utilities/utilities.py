def convert_keys_to_strings(message_map):
    for key in message_map:
        if isinstance(message_map[key], dict):
            message_map[key] = {str(k): v for k, v in message_map[key].items()}