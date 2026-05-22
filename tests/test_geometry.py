from vitrans.models import Rect
from vitrans.geometry import content_capture_rect, translate_capture_bbox_to_overlay


def test_translate_capture_bbox_to_overlay_offsets_by_content_origin():
    bbox = Rect(x=10, y=20, width=100, height=30)
    result = translate_capture_bbox_to_overlay(bbox, content_origin_x=5, content_origin_y=40)
    assert result == Rect(x=15, y=60, width=100, height=30)


def test_content_capture_rect_excludes_top_bar():
    overlay = Rect(x=100, y=200, width=500, height=300)
    result = content_capture_rect(overlay, top_bar_height=36)
    assert result == Rect(x=100, y=236, width=500, height=264)


def test_content_capture_rect_never_returns_negative_height():
    overlay = Rect(x=100, y=200, width=500, height=20)
    result = content_capture_rect(overlay, top_bar_height=36)
    assert result == Rect(x=100, y=236, width=500, height=1)
