import os
import subprocess
from pathlib import Path

def convert_to_pdf(input_file, output_file):
    try:
        subprocess.run([
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            os.path.dirname(output_file),
            input_file
        ], check=True, capture_output=True, text=True)
        print(f"Converted: {input_file} -> {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def rename_file(input_file):
    file_name, file_ext = os.path.splitext(input_file)
    new_name = f"{file_name}_CONVERTED{file_ext}"
    try:
        os.rename(input_file, new_name)
        print(f"Renamed: {input_file} -> {new_name}")
    except Exception as e:
        print(f"Error renaming {input_file}: {e}")

def process_directory(directory):
    total_files = 0
    converted_files = 0
    
    for root, _, files in os.walk(directory):
        print(f"\nProcessing folder: {root}")
        for file in files:
            if file.lower().endswith(('.doc', '.docx')) and "CONVERTED" not in file:
                total_files += 1
                input_path = os.path.join(root, file)
                output_path = os.path.splitext(input_path)[0] + '.pdf'
                
                if convert_to_pdf(input_path, output_path):
                    rename_file(input_path)
                    converted_files += 1
    
    print(f"\nConversion complete.")
    print(f"Total Word files found: {total_files}")
    print(f"Successfully converted files: {converted_files}")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Starting to process directory: {script_directory}")
    process_directory(script_directory)