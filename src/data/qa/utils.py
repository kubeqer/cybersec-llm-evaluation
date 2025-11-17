def format_options(options: list | dict | str) -> str:
    if isinstance(options, list):
        return "\n".join([f"{chr(65 + i)}. {opt}" for i, opt in enumerate(options)])
    elif isinstance(options, dict):
        return "\n".join([f"{k}. {v}" for k, v in options.items()])
    return str(options)
