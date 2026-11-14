"""
Packages all submission deliverables into a single clean ZIP archive for UMS submission.
"""

import os
import zipfile

def package_submission(output_zip="Rockfall_Early_Warning_System_UMS_Submission.zip"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, output_zip)

    source_files = [
        "app.py",
        "model.py",
        "prediction.py",
        "alert_system.py",
        "emergency_response.py",
        "database.py",
        "rockfall.db",
        "requirements.txt",
        "run_app.bat",
        "test_system.py",
        "README.md"
    ]

    source_dirs = [
        "templates",
        "static",
        "data",
        "models",
        "uploads"
    ]

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add Root Submission Deliverables
        if os.path.exists(os.path.join(base_dir, "PROJECT_REPORT.docx")):
            zipf.write(os.path.join(base_dir, "PROJECT_REPORT.docx"), "Project_Report.docx")
        
        if os.path.exists(os.path.join(base_dir, "ROCKFALL_EARLY_WARNING_PRESENTATION.pptx")):
            zipf.write(os.path.join(base_dir, "ROCKFALL_EARLY_WARNING_PRESENTATION.pptx"), "Presentation_Slides.pptx")

        if os.path.exists(os.path.join(base_dir, "SUBMISSION_LINKS_AND_DETAILS.txt")):
            zipf.write(os.path.join(base_dir, "SUBMISSION_LINKS_AND_DETAILS.txt"), "SUBMISSION_LINKS_AND_DETAILS.txt")

        # 2. Add Source Code folder
        for file in source_files:
            file_path = os.path.join(base_dir, file)
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.join("Source_Code", file))

        for directory in source_dirs:
            dir_path = os.path.join(base_dir, directory)
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if "__pycache__" in root or file.endswith(".pyc"):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, base_dir)
                        zipf.write(full_path, os.path.join("Source_Code", rel_path))

    file_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[UMS Package] Created '{output_zip}' successfully ({file_size_mb:.2f} MB).")
    return zip_path

if __name__ == '__main__':
    package_submission()
