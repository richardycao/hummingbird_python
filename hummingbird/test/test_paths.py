from pathlib import Path

path = Path('./a/b/test_paths.py')
print(path.name)
print(path.parent.name)
print(path)
#print(list(path.glob('*.*')))