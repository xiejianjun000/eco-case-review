"""
PDF/OCR 文档解析模块 - 解析案卷文件
"""
from typing import Dict, Any, Optional
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import base64
from loguru import logger

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class DocumentParser:
    """文档解析器 - 支持 PDF、图片、文本文件解析"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.json', '.jpg', '.jpeg', '.png', '.tiff']
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析文件并提取内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析结果字典
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return self._parse_pdf(file_path)
        elif suffix == '.txt':
            return self._parse_txt(file_path)
        elif suffix == '.json':
            return self._parse_json(file_path)
        elif suffix in ['.jpg', '.jpeg', '.png', '.tiff']:
            return self._parse_image(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
    
    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """解析 PDF 文件"""
        try:
            doc = fitz.open(file_path)
            pages = []
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 提取文本
                text = page.get_text()
                full_text += text
                
                # 提取图片
                images = []
                for img in page.get_images(full=True):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append({
                        'index': len(images),
                        'width': base_image['width'],
                        'height': base_image['height'],
                        'format': base_image['ext']
                    })
                
                pages.append({
                    'page_number': page_num + 1,
                    'text': text,
                    'text_length': len(text),
                    'images': images,
                    'image_count': len(images)
                })
            
            # 检查是否需要 OCR（如果文本很少但有图片）
            need_ocr = len(full_text.strip()) < 100 and any(p['image_count'] > 0 for p in pages)
            
            if need_ocr and PDF2IMAGE_AVAILABLE:
                ocr_text = self._perform_ocr(file_path)
                full_text = full_text + "\n\n[OCR识别内容]\n" + ocr_text
            
            return {
                'success': True,
                'file_type': 'pdf',
                'page_count': len(doc),
                'total_text_length': len(full_text),
                'full_text': full_text,
                'pages': pages,
                'has_images': any(p['image_count'] > 0 for p in pages),
                'ocr_performed': need_ocr
            }
            
        except Exception as e:
            logger.error(f"解析 PDF 失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_type': 'pdf',
                'page_count': 0,
                'full_text': '',
                'pages': []
            }
    
    def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        """解析文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                'success': True,
                'file_type': 'txt',
                'line_count': len(lines),
                'text_length': len(content),
                'full_text': content,
                'lines': lines[:100]  # 返回前100行预览
            }
        except Exception as e:
            logger.error(f"解析 TXT 失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """解析 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'success': True,
                'file_type': 'json',
                'data': data,
                'keys': list(data.keys())
            }
        except Exception as e:
            logger.error(f"解析 JSON 失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        """解析图片文件（使用 OCR）"""
        try:
            text = self._ocr_image(file_path)
            
            return {
                'success': True,
                'file_type': 'image',
                'ocr_text': text,
                'text_length': len(text)
            }
        except Exception as e:
            logger.error(f"解析图片失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _perform_ocr(self, pdf_path: str) -> str:
        """对 PDF 文件执行 OCR"""
        try:
            images = convert_from_path(pdf_path)
            ocr_text = ""
            
            for img in images:
                text = pytesseract.image_to_string(img, lang='chi_sim')
                ocr_text += text + "\n"
            
            return ocr_text
        except Exception as e:
            logger.warning(f"OCR 失败: {e}")
            return ""
    
    def _ocr_image(self, image_path: str) -> str:
        """对图片执行 OCR"""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='chi_sim')
            return text
        except Exception as e:
            logger.warning(f"图片 OCR 失败: {e}")
            return ""
    
    def extract_key_info(self, content: str) -> Dict[str, Any]:
        """
        从文本内容中提取关键信息
        
        Args:
            content: 案卷文本内容
            
        Returns:
            提取的关键信息
        """
        import re
        
        info = {
            'case_number': '',
            'case_name': '',
            'respondent': '',
            'organizing_unit': '',
            'violation': '',
            'penalty_amount': '',
            'filing_date': '',
            'decision_date': ''
        }
        
        # 提取案号
        match = re.search(r'案号[：:]?\s*([^\n]+)', content)
        if match:
            info['case_number'] = match.group(1).strip()
        
        # 提取案件名称
        match = re.search(r'案件名称[：:]?\s*([^\n]+)', content)
        if match:
            info['case_name'] = match.group(1).strip()
        
        # 提取当事人
        match = re.search(r'当事人[：:]?\s*([^\n]+)', content)
        if match:
            info['respondent'] = match.group(1).strip()
        
        # 提取承办单位
        match = re.search(r'承办单位[：:]?\s*([^\n]+)', content)
        if match:
            info['organizing_unit'] = match.group(1).strip()
        
        # 提取违法行为
        match = re.search(r'违法行为[：:]?\s*([^\n]+)', content)
        if match:
            info['violation'] = match.group(1).strip()
        
        # 提取罚款金额
        match = re.search(r'罚款\s*([\d.]+)\s*万元?', content)
        if match:
            info['penalty_amount'] = match.group(1)
        
        # 提取日期
        match = re.search(r'立案日期[：:]?\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            info['filing_date'] = match.group(1)
        
        match = re.search(r'决定日期[：:]?\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            info['decision_date'] = match.group(1)
        
        return info


# 全局实例
document_parser = DocumentParser()
