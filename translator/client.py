"""Google Cloud Translation API 클라이언트"""

import os
from google.cloud import translate_v2 as translate
from typing import List, Dict


class TranslationClient:
    """Google Cloud Translation API 클라이언트 래퍼"""
    
    def __init__(self, project_id: str = None):
        """
        클라이언트 초기화
        
        Args:
            project_id: Google Cloud 프로젝트 ID
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.client = translate.Client()
    
    def translate_text(
        self, 
        text: str, 
        target_language: str = "ko", 
        source_language: str = "ja"
    ) -> str:
        """
        텍스트 번역
        
        Args:
            text: 번역할 텍스트
            target_language: 도착어 코드
            source_language: 출발어 코드
            
        Returns:
            번역된 텍스트
        """
        if not text or not text.strip():
            return text
        
        try:
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            return result["translatedText"]
        except Exception as e:
            raise Exception(f"번역 중 오류 발생: {str(e)}")
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str = "ko",
        source_language: str = "ja"
    ) -> List[str]:
        """
        여러 텍스트를 일괄 번역
        
        Args:
            texts: 번역할 텍스트 리스트
            target_language: 도착어 코드
            source_language: 출발어 코드
            
        Returns:
            번역된 텍스트 리스트
        """
        if not texts:
            return []
        
        try:
            results = self.client.translate(
                texts,
                target_language=target_language,
                source_language=source_language
            )
            
            if isinstance(results, list):
                return [r["translatedText"] for r in results]
            else:
                return [results["translatedText"]]
        except Exception as e:
            raise Exception(f"일괄 번역 중 오류 발생: {str(e)}")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        지원하는 언어 목록 조회
        
        Returns:
            언어 코드와 이름 딕셔너리 리스트
        """
        results = self.client.get_languages()
        return [{"code": lang["language"], "name": lang.get("name", "")} for lang in results]
