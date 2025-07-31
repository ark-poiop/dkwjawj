#!/usr/bin/env python3
"""
로컬 Carousel 이미지 생성 스크립트
슬라이드 JSON을 PNG 이미지로 변환 (1080×1350)
"""

from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 이미지 설정
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350
BACKGROUND_COLOR = (18, 18, 18)  # 다크 그레이
TEXT_COLOR = (255, 255, 255)     # 화이트
ACCENT_COLOR = (0, 150, 255)     # 블루
HOT_COLOR = (255, 69, 0)         # 오렌지

def load_font(size, bold=False):
    """폰트 로드 (한글 지원)"""
    font_paths = []
    
    # macOS 폰트 경로들
    if os.name == 'posix':  # macOS/Linux
        font_paths.extend([
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS 한글 폰트
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ])
    else:  # Windows
        font_paths.extend([
            "C:/Windows/Fonts/malgunbd.ttf",
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ])
    
    # 폰트 파일 찾기
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                if bold and "Bold" in font_path or "bd" in font_path:
                    return ImageFont.truetype(font_path, size)
                elif not bold and ("Regular" in font_path or "bd" not in font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"⚠️ 폰트 로드 실패: {font_path} - {e}")
                continue
    
    # 폰트를 찾지 못한 경우 기본 폰트 사용
    logger.warning("⚠️ 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다")
    return ImageFont.load_default()

def create_slide(slide_data, slide_number):
    """개별 슬라이드 생성"""
    # 새 이미지 생성
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    title_font = load_font(48, bold=True)
    bullet_font = load_font(32)
    hot_font = load_font(28, bold=True)
    page_font = load_font(24)
    
    # 제목 (상단)
    title = slide_data.get('heading', '')
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (IMAGE_WIDTH - title_width) // 2
    title_y = 80
    
    draw.text((title_x, title_y), title, font=title_font, fill=TEXT_COLOR)
    
    # 구분선
    line_y = title_y + 80
    draw.line([(50, line_y), (IMAGE_WIDTH - 50, line_y)], fill=ACCENT_COLOR, width=3)
    
    # Bullet 1
    bullet1 = slide_data.get('bullet1', '')
    bullet1_y = line_y + 100
    draw.text((60, bullet1_y), "•", font=bullet_font, fill=ACCENT_COLOR)
    draw.text((90, bullet1_y), bullet1, font=bullet_font, fill=TEXT_COLOR)
    
    # Bullet 2
    bullet2 = slide_data.get('bullet2', '')
    bullet2_y = bullet1_y + 80
    draw.text((60, bullet2_y), "•", font=bullet_font, fill=ACCENT_COLOR)
    draw.text((90, bullet2_y), bullet2, font=bullet_font, fill=TEXT_COLOR)
    
    # Hot 섹션 (하단)
    hot_text = slide_data.get('hot', '')
    if hot_text:
        # Hot 배경 박스
        hot_bbox = draw.textbbox((0, 0), hot_text, font=hot_font)
        hot_width = hot_bbox[2] - hot_bbox[0] + 40
        hot_height = hot_bbox[3] - hot_bbox[1] + 20
        
        hot_x = (IMAGE_WIDTH - hot_width) // 2
        hot_y = IMAGE_HEIGHT - 200
        
        # 배경 박스 그리기
        draw.rectangle([hot_x, hot_y, hot_x + hot_width, hot_y + hot_height], 
                      fill=HOT_COLOR, outline=HOT_COLOR, width=2)
        
        # Hot 텍스트
        hot_text_x = hot_x + 20
        hot_text_y = hot_y + 10
        draw.text((hot_text_x, hot_text_y), hot_text, font=hot_font, fill=TEXT_COLOR)
    
    # 페이지 번호 (우하단)
    page_text = f"{slide_number}/6"
    page_bbox = draw.textbbox((0, 0), page_text, font=page_font)
    page_width = page_bbox[2] - page_bbox[0]
    page_x = IMAGE_WIDTH - page_width - 30
    page_y = IMAGE_HEIGHT - 50
    
    draw.text((page_x, page_y), page_text, font=page_font, fill=ACCENT_COLOR)
    
    return img

def create_carousel(slides_data, date_str):
    """전체 Carousel 생성"""
    slides = slides_data.get('slides', [])
    
    if len(slides) != 6:
        logger.error(f"❌ 슬라이드 개수가 6개가 아닙니다: {len(slides)}개")
        return None
    
    # 미리보기 디렉토리 생성
    preview_dir = f'data/{date_str}/preview'
    os.makedirs(preview_dir, exist_ok=True)
    
    slide_images = []
    
    for i, slide_data in enumerate(slides, 1):
        logger.info(f"🎨 슬라이드 {i} 생성 중...")
        
        # 슬라이드 이미지 생성
        slide_img = create_slide(slide_data, i)
        
        # 파일명 생성
        filename = f'slide_{i:02d}.png'
        filepath = os.path.join(preview_dir, filename)
        
        # 이미지 저장
        slide_img.save(filepath, 'PNG', optimize=True)
        slide_images.append(filepath)
        
        logger.info(f"💾 슬라이드 {i} 저장: {filepath}")
    
    return slide_images

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) != 2:
        logger.error("❌ 사용법: python local_carousel.py [slides_json_file]")
        return None
    
    slides_file = sys.argv[1]
    
    if not os.path.exists(slides_file):
        logger.error(f"❌ 슬라이드 파일 없음: {slides_file}")
        return None
    
    # 슬라이드 데이터 로드
    with open(slides_file, 'r', encoding='utf-8') as f:
        slides_data = json.load(f)
    
    # 날짜 추출
    date_str = slides_file.split('/')[-2] if '/' in slides_file else datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"🎨 Carousel 이미지 생성 시작: {date_str}")
    
    # Carousel 생성
    slide_images = create_carousel(slides_data, date_str)
    
    if slide_images:
        logger.info(f"✅ Carousel 생성 완료: {len(slide_images)}개 슬라이드")
        return slide_images
    else:
        logger.error("❌ Carousel 생성 실패")
        return None

if __name__ == "__main__":
    main() 