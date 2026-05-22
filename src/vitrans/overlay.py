from collections.abc import Callable

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from vitrans.config import AppConfig
from vitrans.models import Rect, TranslatedBox

TOP_BAR_HEIGHT = 36
RESIZE_MARGIN = 8


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
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(QSize(240, 140))
        self.setGeometry(config.x, config.y, config.width, config.height)
        self._build_ui(config.target_language)

    def _build_ui(self, target_language: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top_bar = QWidget(self)
        top_bar.setFixedHeight(TOP_BAR_HEIGHT)
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("#topBar { background: rgba(20, 20, 20, 210); color: white; }")

        row = QHBoxLayout(top_bar)
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)

        self.language_box = QComboBox(top_bar)
        self.language_box.addItem("Vietnamese", "vi")
        self.language_box.setCurrentIndex(0 if target_language == "vi" else 0)
        row.addWidget(self.language_box)

        translate_button = QPushButton("ViTrans", top_bar)
        translate_button.clicked.connect(self._on_translate)
        row.addWidget(translate_button)

        close_button = QPushButton("X", top_bar)
        close_button.setFixedWidth(32)
        close_button.clicked.connect(self._on_hide)
        row.addWidget(close_button)

        root.addWidget(top_bar)

        self.content = QWidget(self)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        root.addWidget(self.content, 1)

    def current_config(self) -> AppConfig:
        geometry = self.geometry()
        return AppConfig(
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            target_language=self.target_language(),
        )

    def target_language(self) -> str:
        return str(self.language_box.currentData())

    def overlay_rect(self) -> Rect:
        geometry = self.geometry()
        return Rect(x=geometry.x(), y=geometry.y(), width=geometry.width(), height=geometry.height())

    def set_translated_boxes(self, boxes: list[TranslatedBox]) -> None:
        self._status = ""
        self._translated_boxes = boxes
        self.update()

    def set_status(self, message: str) -> None:
        self._status = message
        self._translated_boxes = []
        self.update()

    def clear_results(self) -> None:
        self._status = ""
        self._translated_boxes = []
        self.update()

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

        if event.position().y() <= TOP_BAR_HEIGHT:
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
        self._drag_position = None
        self._resize_edges = set()
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self._update_cursor(self._edges_at(event.position().toPoint()))
        event.accept()

    def leaveEvent(self, event):
        if not self._resize_edges:
            self.unsetCursor()

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
        painter.fillRect(self.rect(), QColor(40, 120, 220, 45))
        painter.setPen(QColor(80, 180, 255, 180))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        if self._status:
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(
                QRect(12, TOP_BAR_HEIGHT + 12, self.width() - 24, 60),
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
