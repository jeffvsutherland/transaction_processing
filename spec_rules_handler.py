def load_spec_rules():
    with open('spec_rules.txt', 'r') as file:
        content = file.read()

    rules = {}
    current_section = None
    for line in content.split('\n'):
        line = line.strip()
        if line.endswith(':'):
            current_section = line[:-1]
            rules[current_section] = []
        elif line and current_section:
            rules[current_section].append(line)

    return rules

def get_spec_rule(rules, section, index=None):
    if section not in rules:
        return f"Section '{section}' not found in spec rules."
    if index is not None:
        try:
            return rules[section][index]
        except IndexError:
            return f"Rule {index} not found in section '{section}'."
    return '\n'.join(rules[section])

# Example usage:
spec_rules = load_spec_rules()
print(get_spec_rule(spec_rules, "DEFINITION OF DONE FOR PROMPT"))
print(get_spec_rule(spec_rules, "Final report contents", 0))