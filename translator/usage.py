"""API usage tracking and cost calculation"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class UsageTracker:
    """API usage tracker"""
    
    def __init__(self, usage_file: str = "usage_history.json"):
        """
        Initialize usage tracker
        
        Args:
            usage_file: JSON file path to save usage history
        """
        self.usage_file = usage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load saved usage history data"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "total_files": 0,
            "total_cost_usd": 0.0,
            "total_size_mb": 0.0,
            "translations": []
        }
    
    def _save_data(self):
        """Save usage history data to file"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save usage history: {str(e)}")
    
    def calculate_cost(self, file_size_bytes: int) -> float:
        """
        Calculate cost based on file size
        
        Document Translation cost:
        - $0.075 per page (first 500 pages/month)
        - $0.045 per page (over 500 pages)
        
        Rough estimate: 1MB = approximately 10 pages
        
        Args:
            file_size_bytes: File size (bytes)
            
        Returns:
            Estimated cost (USD)
        """
        file_size_mb = file_size_bytes / (1024 * 1024)
        estimated_pages = max(1, int(file_size_mb * 10))  # 1MB ≈ 10페이지
        
        # 단순화: 평균 $0.06/페이지로 계산
        cost = estimated_pages * 0.06
        return round(cost, 2)
    
    def add_translation(
        self,
        input_file: str,
        output_file: str,
        source_lang: str,
        target_lang: str,
        file_size_bytes: int
    ):
        """
        Add translation record
        
        Args:
            input_file: Input file name
            output_file: Output file name
            source_lang: Source language code
            target_lang: Target language code
            file_size_bytes: File size (bytes)
        """
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
        cost = self.calculate_cost(file_size_bytes)
        
        translation_record = {
            "timestamp": datetime.now().isoformat(),
            "input_file": os.path.basename(input_file),
            "output_file": os.path.basename(output_file),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "file_size_mb": file_size_mb,
            "estimated_cost_usd": cost
        }
        
        self.data["translations"].append(translation_record)
        self.data["total_files"] += 1
        self.data["total_cost_usd"] = round(self.data["total_cost_usd"] + cost, 2)
        self.data["total_size_mb"] = round(self.data["total_size_mb"] + file_size_mb, 2)
        
        self._save_data()
    
    def get_summary(self) -> Dict:
        """Overall usage summary"""
        return {
            "total_files": self.data["total_files"],
            "total_cost_usd": self.data["total_cost_usd"],
            "total_size_mb": self.data["total_size_mb"],
            "translation_count": len(self.data["translations"])
        }
    
    def get_recent_translations(self, limit: int = 10) -> List[Dict]:
        """View recent translation records"""
        translations = self.data["translations"]
        return translations[-limit:] if len(translations) > limit else translations
    
    def get_all_translations(self) -> List[Dict]:
        """View all translation records"""
        return self.data["translations"]
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Monthly usage summary"""
        monthly_data = {
            "year": year,
            "month": month,
            "files": 0,
            "cost_usd": 0.0,
            "size_mb": 0.0
        }
        
        for record in self.data["translations"]:
            timestamp = datetime.fromisoformat(record["timestamp"])
            if timestamp.year == year and timestamp.month == month:
                monthly_data["files"] += 1
                monthly_data["cost_usd"] += record["estimated_cost_usd"]
                monthly_data["size_mb"] += record["file_size_mb"]
        
        monthly_data["cost_usd"] = round(monthly_data["cost_usd"], 2)
        monthly_data["size_mb"] = round(monthly_data["size_mb"], 2)
        
        return monthly_data
    
    def clear_history(self):
        """Clear usage history"""
        self.data = {
            "total_files": 0,
            "total_cost_usd": 0.0,
            "total_size_mb": 0.0,
            "translations": []
        }
        self._save_data()
