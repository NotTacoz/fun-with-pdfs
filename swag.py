import os
import subprocess

# Get the directory of the current script (where awesome.py is located)
directory = os.path.dirname(os.path.abspath(__file__))

# Define the options you want to use with awesome.py
options = "--paper=a4paper --short-edge --no-crop"

# Recursively search for all files in the directory
for root, dirs, files in os.walk(directory):
    for file in files:
        # Skip files that contain '-book' in their filename
        if '-book' in file:
            continue
        
        file_path = os.path.join(root, file)
        # Run awesome.py on each file that doesn't contain '-book'
        command = f"python3 awesome.py {options} \"{file_path}\""
        subprocess.run(command, shell=True)


# import os
# import subprocess
# import pypandoc

# # Function to convert Word documents to PDF
# def convert_to_pdf(file_path):
#     output_file = file_path.rsplit('.', 1)[0] + ".pdf"
#     try:
#         pypandoc.convert_file(file_path, 'pdf', outputfile=output_file)
#         print(f"Converted {file_path} to {output_file}")
#     except Exception as e:
#         print(f"Failed to convert {file_path} to PDF: {e}")

# # Get the directory of the current script (where awesome.py is located)
# directory = os.path.dirname(os.path.abspath(__file__))

# # Define the options you want to use with awesome.py
# options = "--paper=a4paper --short-edge --no-crop"

# # Recursively search for all files in the directory
# for root, dirs, files in os.walk(directory):
#     for file in files:
#         # Full path to the file
#         file_path = os.path.join(root, file)
        
#         # Convert Word documents to PDF if they are .doc or .docx
#         if file.lower().endswith(('.doc', '.docx')):
#             convert_to_pdf(file_path)

# # Re-run the file search to include the newly created PDFs
# for root, dirs, files in os.walk(directory):
#     for file in files:
#         # Skip files that contain '-book' in their filename
#         if '-book' in file:
#             continue

#         # Run awesome.py on each file that doesn't contain '-book'
#         file_path = os.path.join(root, file)
#         command = f"python3 awesome.py {options} \"{file_path}\""
#         subprocess.run(command, shell=True)
