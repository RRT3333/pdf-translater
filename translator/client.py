"""Google Cloud Translation API 클라이언트"""

import os
from google.cloud import translate_v3 as translate
from typing import Dict


class TranslationClient:
    """Google Cloud Translation API v3 클라이언트 래퍼 (Document Translation)"""
    
    def __init__(self, project_id: str = None):
        """
        클라이언트 초기화
        
        Args:
            project_id: Google Cloud 프로젝트 ID
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.")
        
        self.client = translate.TranslationServiceClient()
        self.location = "us-central1"  # 또는 "global"
        self.parent = f"projects/{self.project_id}/locations/{self.location}"
    
    def translate_document(
        self,
        file_path: str,
        target_language: str = "ko",
        source_language: str = "ja",
        mime_type: str = "application/pdf"
    ) -> Dict:
        """
        문서 파일 번역 (PDF, DOCX 등)
        
        Args:
            file_path: 번역할 파일 경로
            target_language: 도착어 코드
            source_language: 출발어 코드 (옵션, 자동 감지 가능)
            mime_type: 파일 MIME 타입
            
        Returns:
            번역된 문서 정보 딕셔너리 (document_content, mime_type)
        """
        try:
            # 파일 읽기
            with open(file_path, "rb") as f:
                document_content = f.read()
            
            # 문서 입력 설정
            document_input_config = {
                "content": document_content,
                "mime_type": mime_type,
            }
            
            # 번역 요청
            request = {
                "parent": self.parent,
                "target_language_code": target_language,
                "document_input_config": document_input_config,
            }
            
            # source_language가 지정된 경우에만 추가 (자동 감지도 가능)
            if source_language:
                request["source_language_code"] = source_language
            
            # API 호출
            response = self.client.translate_document(request=request)
            
            return {
                "document_content": response.document_translation.byte_stream_outputs[0],
                "mime_type": response.document_translation.mime_type,
                "detected_language": getattr(response, "detected_language_code", source_language)
            }
            
        except Exception as e:
            raise Exception(f"문서 번역 중 오류 발생: {str(e)}")
