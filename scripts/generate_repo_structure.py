import os
import json
import hashlib

def file_hash(path):
    """Generate SHA256 hash for a file"""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"error: {str(e)}"

def get_file_info(filepath):
    """Get detailed file information"""
    try:
        stat = os.stat(filepath)
        return {
            "path": filepath,
            "size_bytes": stat.st_size,
            "sha256": file_hash(filepath),
            "modified": stat.st_mtime
        }
    except Exception as e:
        return {
            "path": filepath,
            "error": str(e)
        }

def scan_repository():
    """Scan repository and generate structure data"""
    repo_data = {
        "scan_date": "2025-01-22",
        "repository": "MOTEB1989/Top-TieR-Global-HUB-AI",
        "files": [],
        "summary": {
            "total_files": 0,
            "total_size_bytes": 0,
            "file_types": {}
        }
    }
    
    exclude_dirs = {".git", "__pycache__", "node_modules", "dist", "target", ".venv", "venv"}
    exclude_files = {".DS_Store", "Thumbs.db", "desktop.ini"}
    
    for root, dirs, files in os.walk(".", topdown=True):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file in exclude_files:
                continue
                
            full_path = os.path.join(root, file)
            file_info = get_file_info(full_path)
            
            # Track file extension
            ext = os.path.splitext(file)[1] or "no_extension"
            repo_data["summary"]["file_types"][ext] = repo_data["summary"]["file_types"].get(ext, 0) + 1
            
            # Add to files list
            repo_data["files"].append(file_info)
            
            # Update summary
            if "error" not in file_info:
                repo_data["summary"]["total_files"] += 1
                repo_data["summary"]["total_size_bytes"] += file_info["size_bytes"]
    
    return repo_data

def main():
    print("🔍 Scanning repository structure...")
    repo_data = scan_repository()
    
    output_file = "repo_structure.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(repo_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scan complete!")
    print(f"📊 Statistics:")
    print(f"   - Total files: {repo_data['summary']['total_files']}")
    print(f"   - Total size: {repo_data['summary']['total_size_bytes']:,} bytes")
    print(f"   - File types: {len(repo_data['summary']['file_types'])}")
    print(f"📄 Output saved to: {output_file}")

if __name__ == "__main__":
    main()