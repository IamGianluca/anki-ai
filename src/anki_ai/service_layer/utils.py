import difflib

from termcolor import colored


def github_style_diff(text1: str, text2: str) -> None:
    """Print a GitHub-style colored diff between two strings."""

    def color_text(text, bg_color):
        return colored(text, "black", bg_color, attrs=["bold"])

    sm = difflib.SequenceMatcher(None, text1, text2)
    line1 = []
    line2 = []

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            line1.append(color_text(text1[i1:i2], "on_red"))
            line2.append(color_text(text2[j1:j2], "on_green"))
        elif op == "delete":
            line1.append(color_text(text1[i1:i2], "on_light_red"))
        elif op == "insert":
            line2.append(color_text(text2[j1:j2], "on_light_green"))
        elif op == "replace":
            line1.append(color_text(text1[i1:i2], "on_light_red"))
            line2.append(color_text(text2[j1:j2], "on_light_green"))

    print(f"- {''.join(line1)}\n+ {''.join(line2)}")
