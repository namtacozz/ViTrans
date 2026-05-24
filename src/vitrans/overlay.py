from collections.abc import Callable

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QVBoxLayout, QWidget

from vitrans.config import AppConfig
from vitrans.models import Rect, TranslatedBox
from vitrans.resources import resource_path

TOP_BAR_HEIGHT = 0
RESIZE_MARGIN = 8

OVERLAY_COLORS: dict[str, tuple[QColor, QColor]] = {
    "blue": (QColor(40, 120, 220, 45), QColor(80, 180, 255, 180)),
    "green": (QColor(40, 180, 80, 45), QColor(80, 255, 140, 180)),
    "red": (QColor(220, 60, 60, 45), QColor(255, 120, 120, 180)),
    "purple": (QColor(140, 60, 220, 45), QColor(180, 120, 255, 180)),
    "orange": (QColor(220, 140, 40, 45), QColor(255, 180, 80, 180)),
    "white": (QColor(200, 200, 200, 45), QColor(230, 230, 230, 180)),
}

SOURCE_LANGUAGES = [
    ("Tự phát hiện", "auto"),
    ("English", "en"),
    ("Tiếng Việt", "vi"),
    ("日本語", "ja"),
    ("한국어", "ko"),
    ("中文", "zh-CN"),
    ("Français", "fr"),
    ("Deutsch", "de"),
]

TARGET_LANGUAGES = [
    ("Tiếng Việt", "vi"),
    ("English", "en"),
    ("日本語", "ja"),
    ("한국어", "ko"),
    ("中文", "zh-CN"),
    ("Français", "fr"),
    ("Deutsch", "de"),
]


class OverlayWindow(QWidget):
    def __init__(self, config: AppConfig, on_translate: Callable[[], None], on_hide: Callable[[], None]):
        super().__init__()
        self._on_translate = on_translate
        self._on_hide = on_hide
        self._drag_position: QPoint | None = None
        self._resize_edges: set[str] = set()
        self._resize_start_pos: QPoint | None = None
        self._resize_start_geometry: QRect | None = None
        self._translated_boxes: list[TranslatedBox] = []
        self._status = ""
        self._overlay_color = config.overlay_color
        self._source_language = config.source_language
        self._target_language = config.target_language
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(QSize(32, 24))
        self.setGeometry(config.x, config.y, config.width, config.height)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)

        self.translate_button = QPushButton(self)
        self.translate_button.setIcon(QIcon(str(resource_path("assets/logo.ico"))))
        self.translate_button.setFixedSize(32, 32)
        self.translate_button.setIconSize(QSize(22, 22))
        self.translate_button.setStyleSheet(
            "QPushButton { background: rgba(20, 20, 20, 150); border: 1px solid rgba(255, 255, 255, 140); border-radius: 16px; }"
            "QPushButton:hover { background: rgba(40, 40, 40, 190); }"
        )
        self.translate_button.clicked.connect(self._start_translate)
        row.addWidget(self.translate_button)

        row.addStretch(1)
        root.addLayout(row)
        root.addStretch(1)

    def _start_translate(self) -> None:
        self.translate_button.hide()
        self._on_translate()

    def current_config(self) -> AppConfig:
        geometry = self.geometry()
        return AppConfig(
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            target_language=self._target_language,
            source_language=self._source_language,
            overlay_color=self._overlay_color,
        )

    def source_language(self) -> str:
        return self._source_language

    def target_language(self) -> str:
        return self._target_language

    def overlay_rect(self) -> Rect:
        geometry = self.geometry()
        return Rect(x=geometry.x(), y=geometry.y(), width=geometry.width(), height=geometry.height())

    def update_overlay_color(self, color_name: str) -> None:
        self._overlay_color = color_name
        self.update()

    def set_translated_boxes(self, boxes: list[TranslatedBox]) -> None:
        self._status = ""
        self._translated_boxes = boxes
        self.translate_button.hide()
        self.update()

    def set_status(self, message: str) -> None:
        self._status = message
        self._translated_boxes = []
        self.translate_button.show()
        self.update()

    def clear_results(self) -> None:
        self._reset_translation_ui()

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)

        source_menu = menu.addMenu("Nguồn")
        self._add_language_actions(source_menu, SOURCE_LANGUAGES, self._source_language, self._set_source_language)

        target_menu = menu.addMenu("Đích")
        self._add_language_actions(target_menu, TARGET_LANGUAGES, self._target_language, self._set_target_language)

        menu.addSeparator()
        close_action = QAction("Tắt", menu)
        close_action.triggered.connect(self._on_hide)
        menu.addAction(close_action)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        edges = self._edges_at(event.position().toPoint())
        if edges:
            self._resize_edges = edges
            self._resize_start_pos = event.globalPosition().toPoint()
            self._resize_start_geometry = self.geometry()
            event.accept()
            return

        if not self.translate_button.geometry().contains(event.position().toPoint()):
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._resize_edges and self._resize_start_pos is not None and self._resize_start_geometry is not None:
            self._resize_to(event.globalPosition().toPoint())
            event.accept()
            return

        if self._drag_position is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return

        self._update_cursor(self._edges_at(event.position().toPoint()))

    def mouseReleaseEvent(self, event):
        changed = self._resize_start_geometry is not None or self._drag_position is not None
        self._drag_position = None
        self._resize_edges = set()
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self._update_cursor(self._edges_at(event.position().toPoint()))
        if changed:
            self._reset_translation_ui()
        event.accept()

    def leaveEvent(self, event):
        if not self._resize_edges:
            self.unsetCursor()

    def resizeEvent(self, event) -> None:
        self._update_translate_button_visibility()
        super().resizeEvent(event)

    def _add_language_actions(
        self,
        menu: QMenu,
        languages: list[tuple[str, str]],
        current: str,
        setter: Callable[[str], None],
    ) -> None:
        for label, code in languages:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(code == current)
            action.triggered.connect(lambda _checked=False, value=code: setter(value))
            menu.addAction(action)

    def _set_source_language(self, language: str) -> None:
        if self._source_language == language:
            return
        self._source_language = language
        self._reset_translation_ui()

    def _set_target_language(self, language: str) -> None:
        if self._target_language == language:
            return
        self._target_language = language
        self._reset_translation_ui()

    def _reset_translation_ui(self) -> None:
        self._status = ""
        self._translated_boxes = []
        self._update_translate_button_visibility()
        self.update()

    def _update_translate_button_visibility(self) -> None:
        if self._status or self._translated_boxes:
            self.translate_button.hide()
        elif self.width() >= 40 and self.height() >= 40:
            self.translate_button.show()
        else:
            self.translate_button.hide()

    def _edges_at(self, position: QPoint) -> set[str]:
        edges: set[str] = set()
        if position.x() <= RESIZE_MARGIN:
            edges.add("left")
        elif position.x() >= self.width() - RESIZE_MARGIN:
            edges.add("right")

        if position.y() <= RESIZE_MARGIN:
            edges.add("top")
        elif position.y() >= self.height() - RESIZE_MARGIN:
            edges.add("bottom")

        return edges

    def _update_cursor(self, edges: set[str]) -> None:
        if edges in ({"left", "top"}, {"right", "bottom"}):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in ({"right", "top"}, {"left", "bottom"}):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & {"left", "right"}:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & {"top", "bottom"}:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def _resize_to(self, global_position: QPoint) -> None:
        if self._resize_start_pos is None or self._resize_start_geometry is None:
            return

        delta = global_position - self._resize_start_pos
        geometry = QRect(self._resize_start_geometry)
        minimum = self.minimumSize()

        if "left" in self._resize_edges:
            new_left = min(geometry.right() - minimum.width() + 1, geometry.left() + delta.x())
            geometry.setLeft(new_left)
        if "right" in self._resize_edges:
            new_right = max(geometry.left() + minimum.width() - 1, geometry.right() + delta.x())
            geometry.setRight(new_right)
        if "top" in self._resize_edges:
            new_top = min(geometry.bottom() - minimum.height() + 1, geometry.top() + delta.y())
            geometry.setTop(new_top)
        if "bottom" in self._resize_edges:
            new_bottom = max(geometry.top() + minimum.height() - 1, geometry.bottom() + delta.y())
            geometry.setBottom(new_bottom)

        self.setGeometry(geometry)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        fill_color, border_color = OVERLAY_COLORS.get(
            self._overlay_color, OVERLAY_COLORS["blue"]
        )
        painter.fillRect(self.rect(), fill_color)
        painter.setPen(border_color)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        if self._status:
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(
                QRect(12, 12, self.width() - 24, 60),
                Qt.AlignmentFlag.AlignLeft,
                self._status,
            )

        for item in self._translated_boxes:
            rect = QRect(item.bbox.x, item.bbox.y, item.bbox.width, max(item.bbox.height, item.font_size + 4))
            painter.setFont(QFont("Segoe UI", item.font_size))
            painter.setPen(QColor(0, 0, 0, 160))
            painter.drawText(
                rect.adjusted(1, 1, 1, 1),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                item.translated,
            )
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                item.translated,
            )
