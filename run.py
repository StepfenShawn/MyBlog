import os
current_address = os.path.dirname("archives/")
file_list = []
for parent, dirnames, filenames in os.walk(current_address):
  for filename in filenames:
    file_list.append([parent + '\\' + filename, filename])
    
print(file_list)