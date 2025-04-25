print("Running modify_readme.py...")

with open("README.md", "a") as f:
    f.write("\n\n> Auto-generated note: Last updated by script.\n")

print("README.md successfully updated.")