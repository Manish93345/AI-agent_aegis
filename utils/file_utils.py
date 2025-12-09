"""
File and directory utilities for AEGIS
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from utils.constants import *

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def load_json(file_path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.FAIL}✗ Config file not found: {file_path}{Colors.ENDC}")
            return {}
        except json.JSONDecodeError as e:
            print(f"{Colors.FAIL}✗ Error parsing {file_path}: {e}{Colors.ENDC}")
            return {}
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Path) -> bool:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"{Colors.GREEN}✓ Saved: {file_path}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error saving {file_path}: {e}{Colors.ENDC}")
            return False
    
    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def backup_file(file_path: Path) -> bool:
        """Create backup of a file"""
        if not file_path.exists():
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = BACKUPS_DIR / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            print(f"{Colors.GREEN}✓ Backup created: {backup_path}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗ Backup failed: {e}{Colors.ENDC}")
            return False
    
    @staticmethod
    def list_files(directory: Path, extension: str = None) -> List[Path]:
        """List files in directory with optional extension filter"""
        if not directory.exists():
            return []
        
        if extension:
            return list(directory.glob(f"*.{extension}"))
        else:
            return list(directory.glob("*"))
    
    @staticmethod
    def ensure_file(file_path: Path, default_content: str = "") -> bool:
        """Ensure a file exists, create with default content if not"""
        if not file_path.exists():
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                print(f"{Colors.GREEN}✓ Created: {file_path}{Colors.ENDC}")
                return True
            except Exception as e:
                print(f"{Colors.FAIL}✗ Failed to create {file_path}: {e}{Colors.ENDC}")
                return False
        return True