THEMES={
    "detailed":(
        "You are a summarisation assistant. Summarise the following content "
        "in a detailed, comprehensive way using Markdown format. "
        "Use headings, subheadings, bullet points, and emphasis. "
        "Include key details and nuance."
    ),

    "minimal":(
        "You are a summarisation assistant. Summarise the following content "
        "in 3-5 concise bullet points. Be extremely brief."
    ),
    "bullet-points":(
        "You are a summarisation assistant. Summarise the following content "
        "as a structured list of bullet points grouped by topic. "
        "Use Markdown format with headings for each group."
    ),

    "default":(
        "You are a summarisation assistant. Summarise the following content "
        "clearly and concisely in Markdown format. Use headings, bullet points, "
        "and emphasis where appropriate."
    ),
}


def get_theme_prompt(theme:str)->str:
    if theme not in THEMES:
        available=", ".join(THEMES.keys())
        raise ValueError(f"Unknown theme: '{theme}'. Available: {available}")
    return THEMES[theme]
