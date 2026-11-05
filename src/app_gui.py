"""
app_gui.py - Modern Figma-Engineered Desktop GUI for TTEmbed 2.0
Designed with Figma AutoLayout design tokens, high-DPI scaling, and robust Windows file safety.
"""

import os
import sys
import stat
import html
from typing import List, Optional, Tuple

# Windows portable standalone: uses embedded PE icon directly

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QCheckBox, QButtonGroup,
    QFileDialog, QMessageBox, QFrame, QSplitter, QListWidget,
    QListWidgetItem, QLineEdit, QStatusBar, QScrollArea,
    QSizePolicy, QSystemTrayIcon, QMenu, QSplashScreen, QProgressBar
)

from font_engine import (
    FontInfo, patch_font_fstype, decode_fstype, classify_file_format,
    FSTYPE_INSTALLABLE, FSTYPE_RESTRICTED, FSTYPE_PREVIEW_PRINT,
    FSTYPE_EDITABLE, FSTYPE_NO_SUBSET, FSTYPE_BITMAP_ONLY
)
from app_assets import get_app_icon, apply_native_windows_icon, get_splash_pixmap


# Figma Design System Stylesheet
FIGMA_THEME_QSS = """
QMainWindow {
    background-color: #0b0f17;
}
QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}
QFrame#headerCard {
    background-color: #141a26;
    border: 1px solid #252f44;
    border-radius: 8px;
}
QFrame#dropZone {
    background-color: #111722;
    border: 2px dashed #2d3748;
    border-radius: 8px;
}
QFrame#dropZone:hover {
    background-color: #162033;
    border-color: #3b82f6;
}
QFrame#contentCard {
    background-color: #141a26;
    border: 1px solid #252f44;
    border-radius: 8px;
}

/* Visible subtle 1px divider with comfortable drag zone */
QSplitter::handle:horizontal {
    background-color: transparent;
    width: 10px;
    border-left: 1px solid #1e293b;
    margin: 4px 4px;
}
QSplitter::handle:horizontal:hover {
    border-left: 1px solid #3b82f6;
    background-color: rgba(59, 130, 246, 0.08);
}

/* High-Contrast Dialog & MessageBox Styling - Prevents invisible white text */
QDialog, QMessageBox {
    background-color: #141a26;
    color: #f8fafc;
}
QMessageBox QLabel {
    color: #f8fafc;
    font-size: 13px;
    background-color: transparent;
}
QMessageBox QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
    min-width: 75px;
    min-height: 22px;
}
QMessageBox QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}
QPushButton#secondaryBtn {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #cbd5e1;
}
QPushButton#secondaryBtn:hover {
    background-color: #334155;
    border-color: #64748b;
    color: #ffffff;
}
QPushButton#dangerBtn {
    background-color: #991b1b;
    border: 1px solid #dc2626;
    color: #ffffff;
}
QPushButton#dangerBtn:hover {
    background-color: #b91c1c;
}
QPushButton#successBtn {
    background-color: #065f46;
    border: 1px solid #059669;
    color: #ffffff;
}
QPushButton#successBtn:hover {
    background-color: #047857;
}
QPushButton#unlockBtn {
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #34d399;
    font-weight: bold;
    border-radius: 5px;
    padding: 4px 10px;
}
QPushButton#unlockBtn:hover {
    background-color: #059669;
}
QPushButton#clearBtn {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    padding: 3px 8px;
    font-size: 11px;
    border-radius: 4px;
}
QPushButton#clearBtn:hover {
    background-color: #334155;
    color: #f87171;
    border-color: #f87171;
}
QListWidget {
    background-color: #141a26;
    border: 1px solid #252f44;
    border-radius: 8px;
    padding: 4px;
}
QListWidget::item {
    border-radius: 6px;
    padding: 0px;
    margin-bottom: 4px;
    background-color: #172030;
    border: 1px solid #222d42;
}
QListWidget::item:selected {
    background-color: #1e3a8a;
    border: 1px solid #3b82f6;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background-color: #1d273b;
    border-color: #334155;
}
QLineEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 8px;
    color: #38bdf8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
QLineEdit:focus {
    border-color: #38bdf8;
}
QRadioButton, QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
    padding: 3px 0;
    min-height: 20px;
    background: transparent;
}
QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #64748b;
    border-radius: 8px;
    background-color: #0f172a;
}
QRadioButton::indicator:checked {
    border: 4px solid #3b82f6;
    background-color: #ffffff;
}
QRadioButton::indicator:hover {
    border-color: #93c5fd;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #64748b;
    border-radius: 4px;
    background-color: #0f172a;
}
QCheckBox::indicator:checked {
    border-color: #10b981;
    background-color: #10b981;
}
QCheckBox::indicator:hover {
    border-color: #93c5fd;
}
QScrollArea, QScrollArea > QWidget > QWidget {
    background-color: transparent;
    border: none;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QStatusBar {
    background-color: #070a10;
    border-top: 1px solid #1e293b;
    color: #94a3b8;
    font-size: 11px;
}
"""


class HeroDropZone(QFrame):
    """Figma Hero Drop Zone Bar."""
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(54)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(12)
        
        icon = QLabel("📥")
        icon.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(icon)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        main_label = QLabel("Drag & Drop Font Files or Folders Here (.ttf, .otf, .ttc)")
        main_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #38bdf8; background: transparent;")
        sub_label = QLabel("Multiple files, folders, and read-only fonts supported")
        sub_label.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
        
        text_layout.addWidget(main_label)
        text_layout.addWidget(sub_label)
        layout.addLayout(text_layout)
        
        layout.addStretch()
        
        self.choose_btn = QPushButton("📁 Browse Files...")
        self.choose_btn.setObjectName("secondaryBtn")
        self.choose_btn.setCursor(Qt.PointingHandCursor)
        self.choose_btn.setMinimumWidth(130)
        self.choose_btn.setFixedHeight(30)
        layout.addWidget(self.choose_btn)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#dropZone {
                    background-color: #064e3b;
                    border: 2px dashed #10b981;
                }
            """)

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent):
        self.setStyleSheet("")

    def dropEvent(self, event: QtGui.QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        paths = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                            paths.append(os.path.join(root, file))
        if paths:
            self.files_dropped.emit(paths)


class QueueItemCard(QFrame):
    remove_requested = Signal(str)
    clicked = Signal()

    def __init__(self, info: FontInfo, parent=None):
        super().__init__(parent)
        self.info = info
        self.setObjectName("queueItemCard")
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        code = info.current_fstype
        if code == 0:
            badge_dot = "🟢"
            badge_text = "Installable"
            badge_color = "#34d399"
        elif code & FSTYPE_RESTRICTED:
            badge_dot = "🔴"
            badge_text = "Restricted"
            badge_color = "#f87171"
        elif code & FSTYPE_PREVIEW_PRINT:
            badge_dot = "🟡"
            badge_text = "Preview"
            badge_color = "#fbbf24"
        elif code & FSTYPE_EDITABLE:
            badge_dot = "🔵"
            badge_text = "Editable"
            badge_color = "#60a5fa"
        else:
            badge_dot = "🟣"
            badge_text = hex(code)
            badge_color = "#c084fc"

        self.dot_label = QLabel(badge_dot)
        self.dot_label.setStyleSheet("font-size: 13px; background: transparent;")
        self.dot_label.setFixedWidth(18)
        layout.addWidget(self.dot_label, 0, Qt.AlignTop)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        name_text = info.full_name or info.family_name or info.file_name
        self.lbl_title = QLabel(name_text)
        self.lbl_title.setStyleSheet("font-weight: 600; color: #f8fafc; font-size: 13px; background: transparent;")
        self.lbl_title.setWordWrap(True)
        info_layout.addWidget(self.lbl_title)

        safe_fname = html.escape(info.file_name)
        sub_parts = [f"<span style='color:{badge_color}'>{badge_text}</span>", f"File: {safe_fname}"]
        if info.postscript_name and info.postscript_name != name_text:
            safe_ps = html.escape(info.postscript_name)
            sub_parts.append(f"PS: {safe_ps}")

        self.lbl_sub = QLabel(" • ".join(sub_parts))
        self.lbl_sub.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
        self.lbl_sub.setWordWrap(True)
        info_layout.addWidget(self.lbl_sub)

        layout.addLayout(info_layout, 1)

        # Clear button per font
        self.btn_del = QPushButton("✕")
        self.btn_del.setToolTip("Remove this font from queue")
        self.btn_del.setCursor(Qt.PointingHandCursor)
        self.btn_del.setFixedSize(20, 20)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.06);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: #991b1b;
                color: #ffffff;
                border-color: #ef4444;
            }
        """)
        self.btn_del.clicked.connect(lambda: self.remove_requested.emit(self.info.file_path))
        layout.addWidget(self.btn_del, 0, Qt.AlignTop)

    def sizeHint(self):
        hint = self.layout().sizeHint()
        return QtCore.QSize(hint.width(), max(58, hint.height() + 4))

    def update_font_info(self, info: FontInfo):
        self.info = info
        code = info.current_fstype
        if code == 0:
            badge_dot = "🟢"
            badge_text = "Installable"
            badge_color = "#34d399"
        elif code & FSTYPE_RESTRICTED:
            badge_dot = "🔴"
            badge_text = "Restricted"
            badge_color = "#f87171"
        elif code & FSTYPE_PREVIEW_PRINT:
            badge_dot = "🟡"
            badge_text = "Preview"
            badge_color = "#fbbf24"
        elif code & FSTYPE_EDITABLE:
            badge_dot = "🔵"
            badge_text = "Editable"
            badge_color = "#60a5fa"
        else:
            badge_dot = "🟣"
            badge_text = hex(code)
            badge_color = "#c084fc"

        self.dot_label.setText(badge_dot)
        name_text = info.full_name or info.family_name or info.file_name
        self.lbl_title.setText(name_text)

        safe_fname = html.escape(info.file_name)
        sub_parts = [f"<span style='color:{badge_color}'>{badge_text}</span>", f"File: {safe_fname}"]
        if info.postscript_name and info.postscript_name != name_text:
            safe_ps = html.escape(info.postscript_name)
            sub_parts.append(f"PS: {safe_ps}")
        self.lbl_sub.setText(" • ".join(sub_parts))
        self.layout().activate()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class DropListWidget(QListWidget):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)

    def update_item_sizes(self):
        w = max(80, self.viewport().width() - 8)
        for i in range(self.count()):
            item = self.item(i)
            card = self.itemWidget(item)
            if card:
                card.setFixedWidth(w)
                card.layout().activate()
                card.adjustSize()
                item.setSizeHint(card.sizeHint())

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        self.update_item_sizes()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QListWidget {
                    border: 2px dashed #10b981;
                }
            """)
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent):
        self.setStyleSheet("")
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        paths = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                            paths.append(os.path.join(root, file))
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTEmbed 2.0 — Font Embedding Permission Manager")
        self.resize(1140, 740)
        self.setMinimumSize(880, 560)
        self.setStyleSheet(FIGMA_THEME_QSS)

        # Set Icon for Window
        self.app_icon = get_app_icon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self.font_items: List[FontInfo] = []
        self.current_selected_index: int = -1
        self._updating_ui = False
        self.setAcceptDrops(True)

        self._init_ui()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent):
        urls = event.mimeData().urls()
        paths = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                            paths.append(os.path.join(root, file))
        if paths:
            self.load_fonts(paths)
            event.acceptProposedAction()

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        try:
            apply_native_windows_icon(int(self.winId()))
        except Exception:
            pass

    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 10, 12, 8)
        main_layout.setSpacing(8)

        # 1. Top App Header Card (Fixed Height: 46px)
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_card.setFixedHeight(46)
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(12, 4, 12, 4)
        h_layout.setSpacing(10)

        # Real App Logo (Replacing generic emoji)
        self.logo_icon_lbl = QLabel()
        if not self.app_icon.isNull():
            self.logo_icon_lbl.setPixmap(self.app_icon.pixmap(24, 24))
        self.logo_icon_lbl.setStyleSheet("background: transparent;")
        h_layout.addWidget(self.logo_icon_lbl)

        logo_title = QLabel("TTEmbed")
        logo_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        h_layout.addWidget(logo_title)

        tag = QLabel("2.0")
        tag.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
        h_layout.addWidget(tag)

        subtitle = QLabel("•  OpenType & TrueType fsType Permissions Editor")
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        h_layout.addWidget(subtitle)

        h_layout.addStretch()

        self.lbl_queue_count = QLabel("0 fonts loaded")
        self.lbl_queue_count.setStyleSheet("color: #94a3b8; font-size: 12px;")
        h_layout.addWidget(self.lbl_queue_count)

        main_layout.addWidget(header_card)

        # 2. Hero Drop Zone (Fixed Height: 54px)
        self.drop_zone = HeroDropZone()
        self.drop_zone.files_dropped.connect(self.load_fonts)
        self.drop_zone.choose_btn.clicked.connect(self.browse_fonts)
        main_layout.addWidget(self.drop_zone)

        # 3. Content Splitter (Takes all remaining vertical space!)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        splitter.setHandleWidth(10)
        splitter.setChildrenCollapsible(False)

        # --- Left Panel: Loaded Fonts Sidebar ---
        left_widget = QWidget()
        left_widget.setMinimumWidth(220)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(6)

        left_bar = QHBoxLayout()
        left_title = QLabel("Queue")
        left_title.setStyleSheet("font-weight: 600; color: #f8fafc; font-size: 13px;")
        left_bar.addWidget(left_title)
        left_bar.addStretch()

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_fonts)
        left_bar.addWidget(self.clear_btn)
        left_layout.addLayout(left_bar)

        # Filter Search Bar
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("🔍 Filter by name, PostScript, or filename (e.g. Nu, Vilna)...")
        self.txt_filter.textChanged.connect(self.filter_fonts)
        left_layout.addWidget(self.txt_filter)

        self.font_list = DropListWidget()
        self.font_list.setWordWrap(True)
        self.font_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.font_list.currentRowChanged.connect(self.on_font_selected)
        self.font_list.files_dropped.connect(self.load_fonts)
        left_layout.addWidget(self.font_list)

        splitter.addWidget(left_widget)

        # --- Right Panel: Scrollable Inspector & Controls ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(8, 0, 4, 0)
        right_layout.setSpacing(8)

        # Card 1: Font Overview with Complete Name Display
        card1 = QFrame()
        card1.setObjectName("contentCard")
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(12, 10, 12, 10)
        c1_layout.setSpacing(5)

        c1_top = QHBoxLayout()
        self.lbl_font_name = QLabel("No Font Selected")
        self.lbl_font_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        c1_top.addWidget(self.lbl_font_name)
        c1_top.addStretch()

        self.lbl_status_pill = QLabel("—")
        self.lbl_status_pill.setStyleSheet("background-color: #1e293b; color: #94a3b8; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;")
        c1_top.addWidget(self.lbl_status_pill)
        c1_layout.addLayout(c1_top)

        # Detailed Name Breakdown (Display Name, Family, PostScript, File)
        self.lbl_name_breakdown = QLabel("Family: —  •  PostScript: —  •  File: —")
        self.lbl_name_breakdown.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: 500;")
        self.lbl_name_breakdown.setWordWrap(True)
        c1_layout.addWidget(self.lbl_name_breakdown)

        self.lbl_font_meta = QLabel("Format: — • Size: — • Version: —")
        self.lbl_font_meta.setStyleSheet("color: #94a3b8; font-size: 11px;")
        c1_layout.addWidget(self.lbl_font_meta)

        self.lbl_font_path = QLabel("Path: —")
        self.lbl_font_path.setStyleSheet("color: #64748b; font-size: 11px;")
        self.lbl_font_path.setWordWrap(True)
        c1_layout.addWidget(self.lbl_font_path)

        right_layout.addWidget(card1)

        # Card 2: Permissions Configuration
        card2 = QFrame()
        card2.setObjectName("contentCard")
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(12, 10, 12, 10)
        c2_layout.setSpacing(6)

        c2_title = QLabel("EMBEDDING PERMISSIONS (fsType)")
        c2_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        c2_layout.addWidget(c2_title)

        self.radio_group = QButtonGroup(self)

        self.radio_installable = QRadioButton("🟢  Installable (0x0000) — Unrestricted / Full Embedding Rights (ttembed)")
        self.radio_installable.setToolTip("Fonts may be embedded in documents and permanently installed on remote systems.\nRemoves all embedding restrictions (original ttembed behavior).")
        self.radio_group.addButton(self.radio_installable, FSTYPE_INSTALLABLE)
        c2_layout.addWidget(self.radio_installable)

        self.radio_editable = QRadioButton("🔵  Editable Embedding (0x0008) — Permitted for Document Editing")
        self.radio_editable.setToolTip("Fonts may be embedded in documents and temporarily installed on other systems to edit documents.")
        self.radio_group.addButton(self.radio_editable, FSTYPE_EDITABLE)
        c2_layout.addWidget(self.radio_editable)

        self.radio_preview = QRadioButton("🟡  Preview & Print (0x0004) — Read-Only Viewing & Printing")
        self.radio_preview.setToolTip("Fonts may be embedded for viewing and printing only. Receiving documents must open read-only.")
        self.radio_group.addButton(self.radio_preview, FSTYPE_PREVIEW_PRINT)
        c2_layout.addWidget(self.radio_preview)

        self.radio_restricted = QRadioButton("🔴  Restricted License (0x0002) — Prohibit Embedding")
        self.radio_restricted.setToolTip("Font must NOT be modified, embedded or exchanged without explicit license from the owner.")
        self.radio_group.addButton(self.radio_restricted, FSTYPE_RESTRICTED)
        c2_layout.addWidget(self.radio_restricted)

        self.radio_installable.setChecked(True)
        self.radio_group.idToggled.connect(self.on_radio_toggled)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #1e293b; margin: 4px 0;")
        c2_layout.addWidget(sep)

        # Modifiers
        mod_label = QLabel("MODIFIERS & ADVANCED")
        mod_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        c2_layout.addWidget(mod_label)

        mod_box = QHBoxLayout()
        mod_box.setSpacing(24)
        self.chk_no_subset = QCheckBox("No Subsetting (Bit 8, 0x0100)")
        self.chk_no_subset.setToolTip("When checked, applications cannot embed a subset of glyphs; the complete font must be embedded.")
        self.chk_no_subset.toggled.connect(self.on_checkbox_toggled)
        mod_box.addWidget(self.chk_no_subset)

        self.chk_bitmap_only = QCheckBox("Bitmap Only (Bit 9, 0x0200)")
        self.chk_bitmap_only.setToolTip("When checked, only bitmap strike data may be embedded (no vector outlines).")
        self.chk_bitmap_only.toggled.connect(self.on_checkbox_toggled)
        mod_box.addWidget(self.chk_bitmap_only)
        mod_box.addStretch()
        c2_layout.addLayout(mod_box)

        # Hex Sync Bar + Quick Unlock Button
        hex_bar = QHBoxLayout()
        hex_bar.setSpacing(8)
        lbl_hex = QLabel("Target Raw Hex:")
        lbl_hex.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        self.txt_hex = QLineEdit("0x0000")
        self.txt_hex.setFixedWidth(85)
        self.txt_hex.setFixedHeight(26)
        self.txt_hex.setAlignment(Qt.AlignCenter)
        self.txt_hex.textEdited.connect(self.on_hex_edited)
        
        self.btn_quick_unlock = QPushButton("⚡ Set 0x0000 (Unlock)")
        self.btn_quick_unlock.setObjectName("unlockBtn")
        self.btn_quick_unlock.setCursor(Qt.PointingHandCursor)
        self.btn_quick_unlock.clicked.connect(self.quick_unlock)

        hex_bar.addWidget(lbl_hex)
        hex_bar.addWidget(self.txt_hex)
        hex_bar.addWidget(self.btn_quick_unlock)
        hex_bar.addStretch()
        c2_layout.addLayout(hex_bar)

        right_layout.addWidget(card2)

        # Card 3: Save Actions Card
        card3 = QFrame()
        card3.setObjectName("contentCard")
        c3_layout = QVBoxLayout(card3)
        c3_layout.setContentsMargins(12, 10, 12, 10)
        c3_layout.setSpacing(8)

        c3_title = QLabel("EXPORT & SAVE")
        c3_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        c3_layout.addWidget(c3_title)

        save_row = QHBoxLayout()
        save_row.setSpacing(10)

        self.btn_save_as = QPushButton("💾 Save As New Font...")
        self.btn_save_as.setCursor(Qt.PointingHandCursor)
        self.btn_save_as.setFixedHeight(34)
        self.btn_save_as.clicked.connect(self.save_as_new)
        save_row.addWidget(self.btn_save_as, stretch=1)

        self.btn_overwrite = QPushButton("⚡ Overwrite Current Font")
        self.btn_overwrite.setObjectName("dangerBtn")
        self.btn_overwrite.setCursor(Qt.PointingHandCursor)
        self.btn_overwrite.setFixedHeight(34)
        self.btn_overwrite.clicked.connect(self.save_overwrite)
        save_row.addWidget(self.btn_overwrite, stretch=1)
        c3_layout.addLayout(save_row)

        batch_row = QHBoxLayout()
        batch_row.setSpacing(10)

        self.btn_batch = QPushButton("🚀 Batch Export All Fonts to Folder...")
        self.btn_batch.setObjectName("successBtn")
        self.btn_batch.setCursor(Qt.PointingHandCursor)
        self.btn_batch.setFixedHeight(34)
        self.btn_batch.clicked.connect(self.batch_apply)
        batch_row.addWidget(self.btn_batch, stretch=6)

        self.chk_create_backup = QCheckBox("Backup (.bak) on overwrite")
        self.chk_create_backup.setChecked(True)
        self.chk_create_backup.setStyleSheet("color: #94a3b8; font-size: 11px;")
        batch_row.addWidget(self.chk_create_backup, stretch=4)
        c3_layout.addLayout(batch_row)

        right_layout.addWidget(card3)

        # 4. Legal Disclaimer Banner (Fills void to bottom of screen)
        disclaimer_frame = QFrame()
        disclaimer_frame.setObjectName("disclaimerFrame")
        disclaimer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        disclaimer_frame.setStyleSheet("""
            QFrame#disclaimerFrame {
                background-color: #0c121e;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        disclaimer_layout = QVBoxLayout(disclaimer_frame)
        disclaimer_layout.setContentsMargins(14, 12, 14, 12)
        disclaimer_layout.setSpacing(8)

        disc_header = QHBoxLayout()
        disc_icon = QLabel("⚖️")
        disc_icon.setStyleSheet("font-size: 16px; background: transparent;")
        disc_header.addWidget(disc_icon)

        disc_title = QLabel("LEGAL NOTICE & EULA COMPLIANCE")
        disc_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px; background: transparent;")
        disc_header.addWidget(disc_title)
        disc_header.addStretch()
        disclaimer_layout.addLayout(disc_header)

        disc_text = QLabel()
        disc_text.setTextFormat(Qt.RichText)
        disc_text.setText(
            "<html><body style='color: #94a3b8; font-family: Segoe UI, sans-serif; font-size: 11px; line-height: 140%;'>"
            "Modifying font embedding permissions (fsType) alters technical binary file flags only. "
            "It does not grant, alter, or transfer copyright ownership, trademark rights, commercial usage rights, or foundry EULA permissions.<br><br>"
            "Users remain strictly bound by the original font vendor's End User License Agreement (EULA). "
            "Always ensure you possess legitimate rights for commercial use or document distribution.<br><br>"
            "<b style='color: #ffffff; font-weight: bold;'>Use at your own risk.</b>"
            "</body></html>"
        )
        disc_text.setStyleSheet("background: transparent;")
        disc_text.setWordWrap(True)
        disclaimer_layout.addWidget(disc_text)
        disclaimer_layout.addStretch()

        right_layout.addWidget(disclaimer_frame, 1)

        scroll_area.setWidget(right_container)
        splitter.addWidget(scroll_area)

        splitter.setStretchFactor(0, 35)
        splitter.setStretchFactor(1, 65)
        
        main_layout.addWidget(splitter, 1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Drag & drop fonts or click Browse Files to begin.")

        self._update_action_state()

    # --- Font Management ---

    def browse_fonts(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Font Files",
            "",
            "Font Files (*.ttf *.otf *.ttc);;TrueType Fonts (*.ttf);;OpenType Fonts (*.otf);;Font Collections (*.ttc);;All Files (*.*)"
        )
        if files:
            self.load_fonts(files)

    def load_fonts(self, file_paths: List[str], show_dialog: bool = True):
        loaded_count = 0
        skipped_files: List[Tuple[str, str]] = []
        duplicate_files: List[str] = []
        existing_paths = {item.file_path for item in self.font_items}

        for path in file_paths:
            norm_path = os.path.abspath(path)
            if norm_path in existing_paths:
                duplicate_files.append(os.path.basename(path))
                continue

            info = FontInfo(path)
            if info.is_valid:
                self.font_items.append(info)
                existing_paths.add(norm_path)
                self._add_list_item(info, update_sizes=False)
                loaded_count += 1
            else:
                reason = info.error_message or "Unsupported file format."
                skipped_files.append((os.path.basename(path), reason))

        # Update item sizes once for batch efficiency
        if loaded_count > 0:
            self.font_list.update_item_sizes()

        self.lbl_queue_count.setText(f"{len(self.font_items)} font(s) loaded")

        if loaded_count > 0:
            msg = f"Loaded {loaded_count} font(s)"
            details = []
            if skipped_files:
                details.append(f"skipped {len(skipped_files)} unsupported")
            if duplicate_files:
                details.append(f"{len(duplicate_files)} duplicate(s) already in queue")
            if details:
                msg += f" ({', '.join(details)})"
            self.status_bar.showMessage(msg + ".", 5000)
            if self.font_list.currentRow() == -1:
                self.font_list.setCurrentRow(0)
        else:
            if duplicate_files and not skipped_files:
                if len(duplicate_files) == 1:
                    self.status_bar.showMessage(f"'{duplicate_files[0]}' is already loaded in the queue.", 5000)
                else:
                    self.status_bar.showMessage(f"All {len(duplicate_files)} font(s) are already loaded in the queue.", 5000)
            elif skipped_files and not duplicate_files:
                if len(skipped_files) == 1:
                    self.status_bar.showMessage(f"Skipped '{skipped_files[0][0]}': {skipped_files[0][1]}", 7000)
                else:
                    self.status_bar.showMessage(f"Skipped {len(skipped_files)} unsupported file(s) (only .ttf/.otf/.ttc supported).", 6000)
            elif skipped_files and duplicate_files:
                self.status_bar.showMessage(f"No fonts loaded ({len(skipped_files)} unsupported, {len(duplicate_files)} duplicate).", 6000)

        # Human-friendly modal guidance when unsupported files were dropped
        if show_dialog and skipped_files:
            if len(skipped_files) == 1:
                name, reason = skipped_files[0]
                QMessageBox.information(
                    self,
                    "Unsupported File Format",
                    f"Could not load '{name}':\n\n{reason}\n\n"
                    "Supported formats: TrueType (.ttf), OpenType (.otf), and TrueType Collections (.ttc)."
                )
            else:
                lines = [f"• {name}: {reason}" for name, reason in skipped_files[:8]]
                if len(skipped_files) > 8:
                    lines.append(f"... and {len(skipped_files) - 8} more file(s).")
                QMessageBox.information(
                    self,
                    "Unsupported Files Skipped",
                    f"{len(skipped_files)} file(s) could not be loaded into TTEmbed 2.0:\n\n"
                    + "\n".join(lines)
                    + "\n\nSupported formats: TrueType (.ttf), OpenType (.otf), and TrueType Collections (.ttc)."
                )

        self._update_action_state()

    def _add_list_item(self, info: FontInfo, update_sizes: bool = True):
        item_widget = QListWidgetItem()
        item_widget.setText("")
        card = QueueItemCard(info)
        card.remove_requested.connect(self.remove_single_font)
        card.clicked.connect(lambda it=item_widget: self.font_list.setCurrentItem(it))
        item_widget.setSizeHint(card.sizeHint())
        item_widget.setData(Qt.UserRole, info.file_path)
        item_widget.setData(Qt.UserRole + 1, f"{info.full_name} {info.family_name} {info.postscript_name} {info.file_name}")
        item_widget.setToolTip(f"Full Name: {info.full_name}\nFamily: {info.family_name}\nPostScript: {info.postscript_name}\nFile: {info.file_name}\nPath: {info.file_path}\nStatus: {info.decoded_fstype.get('summary', '')}")
        self.font_list.addItem(item_widget)
        self.font_list.setItemWidget(item_widget, card)
        if update_sizes:
            self.font_list.update_item_sizes()

    def remove_single_font(self, file_path: str):
        """Removes an individual font from the loaded queue."""
        target_idx = -1
        for i, info in enumerate(self.font_items):
            if info.file_path == file_path:
                target_idx = i
                break
        if target_idx == -1:
            return

        curr_idx = self.current_selected_index
        self.font_items.pop(target_idx)

        for r in range(self.font_list.count()):
            item = self.font_list.item(r)
            if item.data(Qt.UserRole) == file_path:
                self.font_list.takeItem(r)
                break

        self.lbl_queue_count.setText(f"{len(self.font_items)} font(s) loaded")
        if len(self.font_items) == 0:
            self.clear_fonts()
        else:
            if curr_idx == target_idx:
                new_row = min(target_idx, self.font_list.count() - 1)
            elif curr_idx > target_idx:
                new_row = curr_idx - 1
            else:
                new_row = min(curr_idx, self.font_list.count() - 1)
            
            if new_row >= 0:
                self.font_list.setCurrentRow(new_row)
                self.on_font_selected(new_row)
        self._update_action_state()

    def filter_fonts(self, text: str):
        query = text.strip().lower()
        for i in range(self.font_list.count()):
            item = self.font_list.item(i)
            searchable = item.data(Qt.UserRole + 1) or ""
            match = (query in searchable.lower())
            item.setHidden(not match)

    def clear_fonts(self):
        self.font_items.clear()
        self.font_list.clear()
        self.txt_filter.clear()
        self.current_selected_index = -1
        self.lbl_font_name.setText("No Font Selected")
        self.lbl_status_pill.setText("—")
        self.lbl_status_pill.setStyleSheet("background-color: #1e293b; color: #94a3b8; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        self.lbl_name_breakdown.setText("Family: —  •  PostScript: —  •  File: —")
        self.lbl_font_meta.setText("Format: — • Size: — • Version: —")
        self.lbl_font_path.setText("Path: —")
        self.lbl_queue_count.setText("0 fonts loaded")
        self.txt_hex.setStyleSheet("")
        self.txt_hex.setToolTip("Raw 16-bit hex fsType value (0x0000 - 0xFFFF)")
        self.status_bar.showMessage("Queue cleared.", 3000)
        self._update_action_state()

    def on_font_selected(self, row: int):
        if row < 0 or row >= len(self.font_items):
            self.current_selected_index = -1
            return

        self.current_selected_index = row
        info = self.font_items[row]

        # Display Name (Full Name)
        self.lbl_font_name.setText(f"{info.full_name}")

        # Name Breakdown: Family, PostScript, File Name
        ps_str = info.postscript_name or "—"
        fam_str = info.family_name or "—"
        self.lbl_name_breakdown.setText(f"Family: {fam_str}  •  PostScript: {ps_str}  •  File: {info.file_name}")

        self.lbl_font_meta.setText(f"Format: {info.format_type} • Size: {info.file_size / 1024:.1f} KB • Version: {info.font_version or '1.0'}")
        self.lbl_font_path.setText(f"Path: {info.file_path}")

        fs_info = info.decoded_fstype
        cat = fs_info.get("status_category", "installable")
        if cat == "installable":
            pill_color = "background-color: #064e3b; color: #34d399; border: 1px solid #059669;"
        elif cat == "restricted":
            pill_color = "background-color: #7f1d1d; color: #f87171; border: 1px solid #dc2626;"
        elif cat == "editable":
            pill_color = "background-color: #1e3a8a; color: #60a5fa; border: 1px solid #2563eb;"
        elif cat == "preview":
            pill_color = "background-color: #78350f; color: #fbbf24; border: 1px solid #d97706;"
        else:
            pill_color = "background-color: #4c1d95; color: #c084fc; border: 1px solid #7c3aed;"

        self.lbl_status_pill.setText(f"{fs_info['hex_value']} — {fs_info['summary']}")
        self.lbl_status_pill.setStyleSheet(f"{pill_color} padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: bold;")

        self._set_ui_from_fstype(info.current_fstype)
        self._update_action_state()

    # --- Embedding Options Sync ---

    def _validate_hex(self, text: str) -> Tuple[bool, Optional[int], str]:
        """
        Validates hex input string.
        Returns (is_valid, parsed_int_or_None, error_message).
        """
        clean = text.strip()
        if not clean:
            return False, None, "fsType hex value cannot be empty. Enter a value between 0x0000 and 0xFFFF."
        if clean.startswith('-'):
            return False, None, "fsType cannot be negative. Enter a value between 0x0000 and 0xFFFF."
        try:
            val = int(clean, 16)
        except ValueError:
            return False, None, f"'{clean}' is not a valid hexadecimal number. Use digits 0-9 and A-F (e.g. 0x0000)."

        if val < 0 or val > 0xFFFF:
            return False, None, f"Value 0x{val:X} exceeds 16-bit range (max 0xFFFF / 65535)."

        return True, val, ""

    def quick_unlock(self):
        """One-click unlock font to Installable (0x0000)."""
        self._set_ui_from_fstype(0x0000)
        self.txt_hex.setStyleSheet("")
        self.txt_hex.setToolTip("Raw 16-bit hex fsType value (0x0000 - 0xFFFF)")
        self.status_bar.showMessage("Set to Installable (0x0000) - Unrestricted", 3000)

    def _get_target_fstype(self) -> Optional[int]:
        """Reads target fsType directly from hex text box with strict validation."""
        valid, val, _ = self._validate_hex(self.txt_hex.text())
        if valid and val is not None:
            return val
        return None

    def _set_ui_from_fstype(self, fstype: int):
        self._updating_ui = True
        try:
            base = fstype & 0x000F
            if base & FSTYPE_RESTRICTED:
                self.radio_restricted.setChecked(True)
            elif base & FSTYPE_EDITABLE:
                self.radio_editable.setChecked(True)
            elif base & FSTYPE_PREVIEW_PRINT:
                self.radio_preview.setChecked(True)
            elif base == 0:
                self.radio_installable.setChecked(True)
            else:
                self.radio_group.setExclusive(False)
                self.radio_installable.setChecked(False)
                self.radio_editable.setChecked(False)
                self.radio_preview.setChecked(False)
                self.radio_restricted.setChecked(False)
                self.radio_group.setExclusive(True)

            self.chk_no_subset.setChecked(bool(fstype & FSTYPE_NO_SUBSET))
            self.chk_bitmap_only.setChecked(bool(fstype & FSTYPE_BITMAP_ONLY))
            self.txt_hex.setStyleSheet("")
            self.txt_hex.setToolTip("Raw 16-bit hex fsType value (0x0000 - 0xFFFF)")
            self.txt_hex.setText(f"0x{fstype:04X}")
        finally:
            self._updating_ui = False

    def on_radio_toggled(self, button_id, checked):
        if not checked or self._updating_ui:
            return
        val = 0
        if self.radio_restricted.isChecked():
            val |= FSTYPE_RESTRICTED
        elif self.radio_editable.isChecked():
            val |= FSTYPE_EDITABLE
        elif self.radio_preview.isChecked():
            val |= FSTYPE_PREVIEW_PRINT
        elif self.radio_installable.isChecked():
            val |= FSTYPE_INSTALLABLE

        if self.chk_no_subset.isChecked():
            val |= FSTYPE_NO_SUBSET
        if self.chk_bitmap_only.isChecked():
            val |= FSTYPE_BITMAP_ONLY

        self.txt_hex.setStyleSheet("")
        self.txt_hex.setToolTip("Raw 16-bit hex fsType value (0x0000 - 0xFFFF)")
        self.txt_hex.setText(f"0x{val:04X}")

    def on_checkbox_toggled(self, checked):
        if self._updating_ui:
            return
        self.on_radio_toggled(None, True)

    def on_hex_edited(self, text: str):
        if self._updating_ui:
            return
        valid, val, err = self._validate_hex(text)
        if not valid:
            self.txt_hex.setStyleSheet("background-color: #2a1215; border: 1px solid #ef4444; color: #fca5a5; font-family: 'Consolas', monospace; font-size: 12px; padding: 5px 8px; border-radius: 6px;")
            self.txt_hex.setToolTip(f"⚠️ {err}")
            self.status_bar.showMessage(f"⚠️ Hex Editor: {err}", 5000)
            return

        self.txt_hex.setStyleSheet("")
        self.txt_hex.setToolTip("Raw 16-bit hex fsType value (0x0000 - 0xFFFF)")
        self._updating_ui = True
        try:
            base = val & 0x000F
            if base & FSTYPE_RESTRICTED:
                self.radio_restricted.setChecked(True)
            elif base & FSTYPE_EDITABLE:
                self.radio_editable.setChecked(True)
            elif base & FSTYPE_PREVIEW_PRINT:
                self.radio_preview.setChecked(True)
            elif base == 0:
                self.radio_installable.setChecked(True)
            else:
                self.radio_group.setExclusive(False)
                self.radio_installable.setChecked(False)
                self.radio_editable.setChecked(False)
                self.radio_preview.setChecked(False)
                self.radio_restricted.setChecked(False)
                self.radio_group.setExclusive(True)

            self.chk_no_subset.setChecked(bool(val & FSTYPE_NO_SUBSET))
            self.chk_bitmap_only.setChecked(bool(val & FSTYPE_BITMAP_ONLY))
            self.status_bar.showMessage(f"fsType set to 0x{val:04X}", 3000)
        finally:
            self._updating_ui = False

    def _update_action_state(self):
        has_items = bool(self.font_items)
        has_selection = (self.current_selected_index >= 0)
        self.btn_save_as.setEnabled(has_selection)
        self.btn_overwrite.setEnabled(has_selection)
        self.btn_batch.setEnabled(has_items)

    # --- Save Operations ---

    def save_as_new(self):
        if self.current_selected_index < 0:
            return
        target_fstype = self._get_target_fstype()
        if target_fstype is None:
            _, _, err = self._validate_hex(self.txt_hex.text())
            QMessageBox.warning(
                self,
                "Invalid fsType Value",
                f"Cannot save font with an invalid fsType:\n\n{err}\n\nPlease enter a valid hex value (e.g. 0x0000) or click '⚡ Set 0x0000 (Unlock)'."
            )
            self.txt_hex.setFocus()
            return

        info = self.font_items[self.current_selected_index]

        dir_name = os.path.dirname(info.file_path)
        base_name, ext = os.path.splitext(info.file_name)
        suggested = os.path.join(dir_name, f"{base_name}_unlocked{ext}")

        dest_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save As New Font",
            suggested,
            f"Font File (*{ext});;All Files (*.*)"
        )
        if not dest_file:
            return

        success, msg = patch_font_fstype(info.file_path, target_fstype, output_path=dest_file)
        if success:
            QMessageBox.information(
                self,
                "Font Saved Successfully",
                f"New font created with fsType 0x{target_fstype:04X}!\n\nFile:\n{dest_file}"
            )
            self.status_bar.showMessage(f"Saved: {dest_file}", 5000)
            self.load_fonts([dest_file])
        else:
            QMessageBox.critical(self, "Save Failed", f"Could not save font:\n\n{msg}")

    def save_overwrite(self):
        if self.current_selected_index < 0:
            return
        target_fstype = self._get_target_fstype()
        if target_fstype is None:
            _, _, err = self._validate_hex(self.txt_hex.text())
            QMessageBox.warning(
                self,
                "Invalid fsType Value",
                f"Cannot overwrite font with an invalid fsType:\n\n{err}\n\nPlease enter a valid hex value (e.g. 0x0000) or click '⚡ Set 0x0000 (Unlock)'."
            )
            self.txt_hex.setFocus()
            return

        info = self.font_items[self.current_selected_index]
        create_bak = self.chk_create_backup.isChecked()

        reply = QMessageBox.warning(
            self,
            "Confirm Overwrite",
            f"Are you sure you want to overwrite the original font file?\n\n"
            f"Font: {info.full_name}\n"
            f"File: {info.file_path}\n"
            f"New fsType: 0x{target_fstype:04X}\n"
            + (f"\n(A backup copy will be created as .bak)" if create_bak else "\n(NO backup copy will be made)"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        success, msg = patch_font_fstype(info.file_path, target_fstype, create_backup=create_bak)
        if success:
            refreshed = FontInfo(info.file_path)
            self.font_items[self.current_selected_index] = refreshed
            self.on_font_selected(self.current_selected_index)
            
            # Refresh list item widget in-place (no ghost text)
            item = self.font_list.item(self.current_selected_index)
            item.setText("")
            card = self.font_list.itemWidget(item)
            if isinstance(card, QueueItemCard):
                card.update_font_info(refreshed)
            self.font_list.update_item_sizes()
            item.setData(Qt.UserRole + 1, f"{refreshed.full_name} {refreshed.family_name} {refreshed.postscript_name} {refreshed.file_name}")
            item.setToolTip(f"Full Name: {refreshed.full_name}\nFamily: {refreshed.family_name}\nPostScript: {refreshed.postscript_name}\nFile: {refreshed.file_name}\nPath: {refreshed.file_path}\nStatus: {refreshed.decoded_fstype.get('summary', '')}")

            QMessageBox.information(
                self,
                "Overwrite Successful",
                f"Font updated in-place successfully!\n\n{msg}"
            )
            self.status_bar.showMessage(f"Overwritten: {info.file_name}", 5000)
        else:
            QMessageBox.critical(self, "Overwrite Failed", f"Could not overwrite font:\n\n{msg}")

    def batch_apply(self):
        if not self.font_items:
            return
        target_fstype = self._get_target_fstype()
        if target_fstype is None:
            _, _, err = self._validate_hex(self.txt_hex.text())
            QMessageBox.warning(
                self,
                "Invalid fsType Value",
                f"Cannot batch export fonts with an invalid fsType:\n\n{err}\n\nPlease enter a valid hex value (e.g. 0x0000) or click '⚡ Set 0x0000 (Unlock)'."
            )
            self.txt_hex.setFocus()
            return

        reply = QMessageBox.question(
            self,
            "Batch Export Mode",
            f"You have {len(self.font_items)} font(s) in the queue.\n\n"
            f"Apply fsType 0x{target_fstype:04X} to all fonts?\n\n"
            "• Yes: Export All to a Destination Folder (Safe, recommended)\n"
            "• No: Overwrite All Original Files in-place\n"
            "• Cancel: Abort",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Cancel:
            return

        is_folder_export = (reply == QMessageBox.Yes)
        target_folder = None
        if is_folder_export:
            default_dir = os.path.join(os.path.dirname(self.font_items[0].file_path), "result_fonts")
            if not os.path.exists(default_dir):
                default_dir = os.path.dirname(self.font_items[0].file_path)
                
            target_folder = QFileDialog.getExistingDirectory(self, "Select Output Destination Folder", default_dir)
            if not target_folder:
                return

        create_bak = self.chk_create_backup.isChecked()
        success_count = 0
        error_count = 0
        error_msgs = []

        for info in self.font_items:
            dest = os.path.join(target_folder, info.file_name) if is_folder_export else None
            ok, err = patch_font_fstype(info.file_path, target_fstype, output_path=dest, create_backup=create_bak)
            if ok:
                success_count += 1
            else:
                error_count += 1
                error_msgs.append(f"{info.file_name}: {err}")

        summary = f"Batch processing finished!\n\nSuccessfully processed: {success_count} font(s)"
        if error_count > 0:
            summary += f"\nErrors / Skipped: {error_count}\n\n" + "\n".join(error_msgs[:8])

        QMessageBox.information(self, "Batch Complete", summary)
        self.status_bar.showMessage(f"Batch complete: {success_count} exported, {error_count} failed", 6000)

        if not is_folder_export:
            curr = self.current_selected_index
            paths = [info.file_path for info in self.font_items]
            self.clear_fonts()
            self.load_fonts(paths)
            if 0 <= curr < len(self.font_items):
                self.font_list.setCurrentRow(curr)


class LiveSplashScreen(QWidget):
    """
    High-DPI Frameless Vector Splash Screen with a Live Smooth Progress Bar.
    - Zero Tcl/Tk dependency (never hangs on Windows 11).
    - NOT forced on top (no WindowStaysOnTopHint).
    - Live animated progress bar with dynamic stage text.
    - Automated watchdog timer guarantees it can never freeze or get stuck.
    """
    def __init__(self, on_finish_callback=None):
        super().__init__()
        self.on_finish_callback = on_finish_callback
        self._finished = False
        self._val = 0

        # Standalone vector splash screen (no taskbar clutter)
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(520, 240)
        self.app_icon = get_app_icon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        # Center on primary screen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        # Top Header Row: Crisp App Logo + Titles
        head_row = QHBoxLayout()
        head_row.setSpacing(14)

        icon_lbl = QLabel()
        app_icon = get_app_icon()
        if not app_icon.isNull():
            icon_lbl.setPixmap(app_icon.pixmap(46, 46))
        icon_lbl.setStyleSheet("background: transparent;")
        head_row.addWidget(icon_lbl)

        titles_layout = QVBoxLayout()
        titles_layout.setSpacing(3)

        title_tag_row = QHBoxLayout()
        title_tag_row.setSpacing(8)

        lbl_title = QLabel("TTEmbed")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #ffffff; background: transparent;")
        title_tag_row.addWidget(lbl_title)

        lbl_tag = QLabel("2.0")
        lbl_tag.setStyleSheet("background-color: #1e3a8a; color: #93c5fd; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px;")
        title_tag_row.addWidget(lbl_tag)
        title_tag_row.addStretch()
        titles_layout.addLayout(title_tag_row)

        lbl_sub = QLabel("OpenType & TrueType fsType Permissions Editor")
        lbl_sub.setStyleSheet("font-size: 12px; color: #38bdf8; font-weight: 500; background: transparent;")
        titles_layout.addWidget(lbl_sub)

        head_row.addLayout(titles_layout)
        head_row.addStretch()
        layout.addLayout(head_row)

        # Subtitle highlights
        lbl_desc = QLabel("⚡ 1-Click Embedding Unlock  •  Safe Atomic Overwrites  •  Batch Export")
        lbl_desc.setStyleSheet("font-size: 11px; color: #94a3b8; background: transparent; padding-top: 2px;")
        layout.addWidget(lbl_desc)

        layout.addStretch()

        # REAL LIVE ANIMATED PROGRESS BAR
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #141a26;
                border: 1px solid #1e293b;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)

        # Bottom Status Row
        bot_row = QHBoxLayout()
        self.lbl_status = QLabel("Initializing Font Engine...")
        self.lbl_status.setStyleSheet("font-size: 11px; color: #64748b; background: transparent;")
        bot_row.addWidget(self.lbl_status)
        bot_row.addStretch()

        lbl_brand = QLabel("TTEmbed 2.0")
        lbl_brand.setStyleSheet("font-size: 10px; color: #475569; font-weight: 600; background: transparent;")
        bot_row.addWidget(lbl_brand)
        layout.addLayout(bot_row)

        # Smooth live animation timer: 30ms interval * 100 steps = 3000ms (3.0 seconds minimum duration)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(30)

        # Watchdog safety timer: unconditionally finishes after 3.8 seconds max so it NEVER gets stuck
        QtCore.QTimer.singleShot(3800, self.finish)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#0b0f17")))
        painter.setPen(QtGui.QPen(QtGui.QColor("#2563eb"), 1.5))
        card_rect = QtCore.QRectF(self.rect().adjusted(1, 1, -1, -1))
        painter.drawRoundedRect(card_rect, 22.0, 22.0)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor("#1e293b"), 1.0))
        painter.drawRoundedRect(card_rect.adjusted(2, 2, -2, -2), 19.0, 19.0)

    def _step(self):
        if self._finished:
            return
        self._val += 1
        self.progress.setValue(min(100, self._val))
        if self._val < 30:
            self.lbl_status.setText("Initializing Font Engine...")
        elif self._val < 65:
            self.lbl_status.setText("Loading SFNT Table Engine...")
        elif self._val < 90:
            self.lbl_status.setText("Preparing Workspace...")
        else:
            self.lbl_status.setText("Ready.")

        if self._val >= 100:
            self.finish()

    def finish(self):
        if self._finished:
            return
        self._finished = True
        self.timer.stop()
        self.close()
        if self.on_finish_callback:
            self.on_finish_callback()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("TTEmbed")
    app.setApplicationDisplayName("TTEmbed 2.0")

    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = MainWindow()

    def launch_main():
        window.show()
        window.raise_()
        window.activateWindow()

    splash = LiveSplashScreen(on_finish_callback=launch_main)
    splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
