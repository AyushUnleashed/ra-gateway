import os
import re
import pathspec

# Define regex patterns
class_pattern = re.compile(r'^class (\w+)')
function_pattern = re.compile(r'^async def (\w+)|^def (\w+)')
endpoint_pattern = re.compile(r'@(.*\.\w+)\("(.*?)"\)')


# Read .gitignore specs
def read_gitignore_specs(startpath):
    ignore_specs = []
    gitignore_path = os.path.join(startpath, '.gitignore')
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            ignore_specs = f.readlines()
    return pathspec.PathSpec.from_lines('gitwildmatch', ignore_specs)


def analyze_python_files(startpath, output_file):
    spec = read_gitignore_specs(startpath)
    with open(output_file, 'w') as md_file:
        for root, dirs, files in os.walk(startpath, topdown=True):
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(root, d)) and d != '.git']
            python_files = [f for f in files if f.endswith('.py') and not spec.match_file(os.path.join(root, f))]
            if not python_files:
                continue

            # Writing directory structure
            rel_dir = os.path.relpath(root, startpath)
            if rel_dir != ".":
                md_file.write(f"\n### {'/'.join(['`' + part + '`' for part in rel_dir.split('/')])}\n")

            for file in python_files:
                analyze_and_write_file_structure(md_file, os.path.join(root, file))


def analyze_and_write_file_structure(md_file, filepath):
    relative_path = os.path.relpath(filepath, '.')
    md_file.write(f"\n- **{relative_path}**\n")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.readlines()

    last_endpoint = None
    for line in content:
        class_match = class_pattern.match(line.strip())
        function_match = function_pattern.match(line.strip())
        endpoint_match = endpoint_pattern.match(line.strip())

        if class_match:
            md_file.write(f"  - Class: `{class_match.group(1)}`\n")
            last_endpoint = None

        elif endpoint_match:
            router_name, path = endpoint_match.groups()
            last_endpoint = (router_name, path)  # Store as a tuple for later use
            # Do not write yet, wait for the function


        elif function_match:
            function_name = function_match.group(1) or function_match.group(2)
            if last_endpoint:
                router_name, path = last_endpoint  # Unpack the tuple
                md_file.write(f"    - Endpoint: `{router_name}`\n")
                md_file.write(f"      - Path: `{path}`\n")  # Path as a child of the endpoint
                md_file.write(f"      - Function: `{function_name}`\n")  # Function as a child of the endpoint
                last_endpoint = None  # Reset after associating function with endpoint
            else:
                md_file.write(f"    - Function: `{function_name}`\n")


if __name__ == "__main__":
    analyze_python_files('.', 'codebase_structure.md')