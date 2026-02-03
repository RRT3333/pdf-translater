"""API 사용 현황 추적 및 비용 계산"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class UsageTracker:
    """API 사용 현황 추적기"""
    
    def __init__(self, usage_file: str = "usage_history.json"):
        """
        사용 현황 추적기 초기화
        
        Args:
            usage_file: 사용 현황을 저장할 JSON 파일 경로
        """
        self.usage_file = usage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """저장된 사용 현황 데이터 로드"""
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
        """사용 현황 데이터를 파일에 저장"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 사용 현황 저장 실패: {str(e)}")
    
    def calculate_cost(self, file_size_bytes: int) -> float:
        """
        파일 크기 기반 비용 계산
        
        Document Translation 비용:
        - 페이지당 $0.075 (최초 500페이지/월)
        - 페이지당 $0.045 (500페이지 초과분)
        
        대략적 추정: 1MB = 약 10페이지
        
        Args:
            file_size_bytes: 파일 크기 (바이트)
            
        Returns:
            예상 비용 (USD)
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
        번역 기록 추가
        
        Args:
            input_file: 입력 파일명
            output_file: 출력 파일명
            source_lang: 출발어 코드
            target_lang: 도착어 코드
            file_size_bytes: 파일 크기 (바이트)
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
        """전체 사용 현황 요약"""
        return {
            "total_files": self.data["total_files"],
            "total_cost_usd": self.data["total_cost_usd"],
            "total_size_mb": self.data["total_size_mb"],
            "translation_count": len(self.data["translations"])
        }
    
    def get_recent_translations(self, limit: int = 10) -> List[Dict]:
        """최근 번역 기록 조회"""
        translations = self.data["translations"]
        return translations[-limit:] if len(translations) > limit else translations
    
    def get_all_translations(self) -> List[Dict]:
        """모든 번역 기록 조회"""
        return self.data["translations"]
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """월별 사용 현황 요약"""
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
        """사용 기록 초기화"""
        self.data = {
            "total_files": 0,
            "total_cost_usd": 0.0,
            "total_size_mb": 0.0,
            "translations": []
        }
        self._save_data()
