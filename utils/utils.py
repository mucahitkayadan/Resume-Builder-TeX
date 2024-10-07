import os
import shutil
import subprocess
from typing import List, Optional

class Utils:
    @staticmethod
    def copy_tex_headers(source_dir: str, dest_dir: str) -> None:
        """
        Copy all .tex files from the source directory to the destination directory.

        Args:
            source_dir (str): Path to the source directory containing .tex files.
            dest_dir (str): Path to the destination directory where files will be copied.
        """
        for file_name in os.listdir(source_dir):
            if file_name.endswith('.tex'):
                source_file = os.path.join(source_dir, file_name)
                dest_file = os.path.join(dest_dir, file_name)
                shutil.copy2(source_file, dest_file)
                print(f"Copied {file_name} to {dest_dir}")

    @staticmethod
    def compile_tex_to_pdf(tex_file_path: str) -> None:
        """
        Compile a .tex file to PDF using pdflatex.

        Args:
            tex_file_path (str): Path to the .tex file to be compiled.
        """
        # Get the directory and filename
        file_dir = os.path.dirname(tex_file_path)
        file_name = os.path.basename(tex_file_path)
        print(f"Compiling {file_name}")

        # Change the current working directory to the file's directory
        original_dir = os.getcwd()
        os.chdir(file_dir)

        # Run pdflatex
        try:
            subprocess.run(["pdflatex", file_name], check=True)
            print(f"Successfully compiled {file_name} to PDF")
        except subprocess.CalledProcessError:
            print(f"Error compiling {file_name} to PDF")
        finally:
            # Change back to the original directory
            os.chdir(original_dir)

    @staticmethod
    def copy_job_description(source_file: str, dest_dir: str) -> None:
        """
        Copy the job description file to the destination directory.

        Args:
            source_file (str): Path to the source job description file.
            dest_dir (str): Path to the destination directory.
        """
        dest_file = os.path.join(dest_dir, "job_description.txt")
        shutil.copy2(source_file, dest_file)
        print(f"Copied job description to {dest_file}")

# Utils.compile_tex_to_pdf("../created_resumes/darwin_recruitment_computer_vision_engineer/muja_kayadan_resume.tex")