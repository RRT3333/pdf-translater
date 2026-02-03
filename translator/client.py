"""Google Cloud Translation API Client"""

import os
from google.cloud import translate_v3 as translate
from typing import Dict


class TranslationClient:
    """Google Cloud Translation API v3 Client Wrapper (Document Translation)"""
    
    def __init__(self, project_id: str = None):
        """
        Initialize client
        
        Args:
            project_id: Google Cloud project ID
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")
        
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
        Translate document file (PDF, DOCX, etc.)
        
        Args:
            file_path: Path to file to translate
            target_language: Target language code
            source_language: Source language code (optional, auto-detection possible)
            mime_type: File MIME type
            
        Returns:
            Dictionary with translated document info (document_content, mime_type)
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
            raise Exception(f"Error during document translation: {str(e)}")
