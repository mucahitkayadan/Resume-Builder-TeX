import os
from utils.database_manager import DatabaseManager

def migrate_tex_headers_to_db():
    db_manager = DatabaseManager()
    tex_headers_dir = "tex_headers"

    for filename in os.listdir(tex_headers_dir):
        if filename.endswith(".tex"):
            file_path = os.path.join(tex_headers_dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            name = os.path.splitext(filename)[0]
            db_manager.insert_tex_header(name, content)
            print(f"Migrated {filename} to database")

if __name__ == "__main__":
    migrate_tex_headers_to_db()
