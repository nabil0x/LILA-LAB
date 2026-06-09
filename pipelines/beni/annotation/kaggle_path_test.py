import os
print("Listing /kaggle/input/ recursively:")
for root, dirs, files in os.walk("/kaggle/input/"):
    level = root.replace("/kaggle/input/", "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for f in files:
        print(f"{subindent}{f}")
print("DONE")
