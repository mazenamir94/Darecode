def get_spider_frame(state: str, color: str = "#CC0000") -> str:
    # ANSI coloring
    RED = "\033[38;2;204;0;0m" # CC0000
    BLUE = "\033[38;2;0;51;102m" # 003366
    
    C = RED if color == "#CC0000" else BLUE
    R = "\033[0m"
    Y = "\033[33m"
    G = "\033[32m"
    
    if state == "IDLE":
        return f"""
{C} ╲ ▄███▄ ╱{R}
{C}  █▀ ▀█{R}
{C} ╱ ▀███▀ ╲{R}
"""
    elif state == "THINKING":
        return f"""
{C} ╲ ▄███▄ ╱{R}
{C}  █° °█{R} {Y}...{R}
{C} ╱ ▀███▀ ╲{R}
"""
    elif state == "SUCCESS":
        return f"""
{C}   ▄███▄ {G}✓{R}
{C} ╲█^ ^█╱{R}
{C}  ▀███▀{R}
"""
    elif state == "ERROR":
        return f"""
{C}   ▄███▄ {Y}⚠{R}
{C} ╲█X X█╱{R}
{C}  ▀███▀{R}
"""
    return ""

def print_spider(state: str, color: str = "#CC0000"):
    print(get_spider_frame(state, color))
