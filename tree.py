import os
import sys
import json
from git import Repo
import shutil
import stat

def clone_repo(repo_url, clone_dir='temp_repo'):
    """
    Clone the GitHub repo to a temporary directory
    """
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, onerror=handle_remove_readonly)  # Clean up previous clone
    print(f"Cloning repository from {repo_url}...")
    try:
        Repo.clone_from(repo_url, clone_dir)
    except Exception as e:
        print(f"Failed to clone repository: {e}")
        sys.exit(1)

def generate_tree(directory, prefix="", as_dict=False):
    """
    Recursively generate a tree structure for directories and files
    Returns a nested dictionary if as_dict is True
    """
    structure = {}
    files = sorted([f for f in os.listdir(directory) if f != ".git"])  # Ignore .git directory
    for i, file in enumerate(files):
        path = os.path.join(directory, file)
        connector = "├──" if i < len(files) - 1 else "└──"
        
        if as_dict:
            if os.path.isdir(path):
                structure[file] = generate_tree(path, as_dict=True)  # Recursively build the structure
            else:
                structure[file] = None  # Leaf node
        else:
            print(f"{prefix}{connector} {file}")

        if os.path.isdir(path) and not as_dict:
            # Recursively print the tree for sub-directories
            new_prefix = prefix + ("│   " if i < len(files) - 1 else "    ")
            generate_tree(path, new_prefix)

    return structure

def write_json_file(repo_name, structure):
    """
    Write the directory structure to a JSON file
    """
    json_filename = f"{repo_name}.json"
    with open(json_filename, 'w') as json_file:
        json.dump(structure, json_file, indent=2)
    print(f"Directory structure written to {json_filename}")

def handle_remove_readonly(func, path, exc_info):
    """
    Handle read-only file deletion on Windows by changing permissions
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main(repo_url):
    clone_dir = "temp_repo"  # Temporary directory to clone the repo

    # Step 1: Clone the repo
    clone_repo(repo_url, clone_dir)

    # Step 2: Generate the directory tree structure as a dictionary
    tree_structure = generate_tree(clone_dir, as_dict=True)

    # Print the directory tree structure in the console
    generate_tree(clone_dir)

    # Extract the repo name from the URL for the JSON filename
    repo_name = os.path.basename(repo_url).replace('.git', '')  # Remove .git if present
    
    # Step 3: Write the directory structure to a JSON file
    write_json_file(repo_name, tree_structure)

    # Step 4: Clean up the cloned repository
    shutil.rmtree(clone_dir, onerror=handle_remove_readonly)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tree.py <github_repo_url>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    main(repo_url)
