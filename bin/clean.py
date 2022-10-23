import os

dir_name = os.getcwd()
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".gzip"):
        os.remove(os.path.join(dir_name, item))