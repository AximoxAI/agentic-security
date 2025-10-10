import json
import os
import subprocess
import git

with open("custom_instance.json") as f:
    instance = json.load(f)

repo_name = instance["repo"]
base_commit = instance["base_commit"]
repo_path = repo_name.replace("/", "__")

# Clone repo if not exists
if not os.path.exists(repo_path):
    subprocess.run(['git', 'clone', f'https://github.com/{repo_name}.git', repo_path])

# Checkout base commit
repo = git.Repo(repo_path)
repo.git.checkout(base_commit)

# Optionally install dependencies
if os.path.exists(os.path.join(repo_path, "requirements.txt")):
    subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path)
elif os.path.exists(os.path.join(repo_path, "setup.py")):
    subprocess.run(["pip", "install", "-e", "."], cwd=repo_path)
elif os.path.exists(os.path.join(repo_path, "pyproject.toml")):
    subprocess.run(["pip", "install", "."], cwd=repo_path)

# Write and apply patch
patch_file = os.path.join(repo_path, "solution.patch")
with open(patch_file, "w") as f:
    f.write(instance["patch"])

try:
    subprocess.run(["git", "apply", patch_file], cwd=repo_path, check=True)
    result = subprocess.run(["pytest", "-q"], cwd=repo_path, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Solution appears to work!")
    else:
        print("❌ Tests failed:")
        print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"❌ Failed to apply patch: {e}")