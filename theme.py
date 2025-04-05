def get_stylesheet(theme: str) -> str:
    if theme == "dark":
        return """
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 10.5pt;
        }

        QTableWidget {
            background-color: #1e1e1e;
            gridline-color: #2c2c2c;
            selection-background-color: #2d89ef;
        }

        QHeaderView::section {
            background-color: #2c2c2c;
            padding: 4px;
            border: 1px solid #444;
        }

        QMenuBar {
            background-color: #1e1e1e;
        }

        QMenuBar::item:selected {
            background: #2d89ef;
        }

        QMenu {
            background-color: #2c2c2c;
        }

        QMenu::item:selected {
            background-color: #2d89ef;
        }

        QPushButton, QComboBox, QCheckBox {
            background-color: #2c2c2c;
            border: 1px solid #444;
            padding: 4px;
        }

        QPushButton:hover, QComboBox:hover {
            border: 1px solid #2d89ef;
        }
        """

    elif theme == "light":
        return """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 10.5pt;
        }

        QTableWidget {
            background-color: #ffffff;
            gridline-color: #cccccc;
            selection-background-color: #0078d7;
        }

        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 4px;
            border: 1px solid #aaa;
        }

        QMenuBar {
            background-color: #e0e0e0;
        }

        QMenuBar::item:selected {
            background: #0078d7;
        }

        QMenu {
            background-color: #f0f0f0;
        }

        QMenu::item:selected {
            background-color: #0078d7;
        }

        QPushButton, QComboBox, QCheckBox {
            background-color: #ffffff;
            border: 1px solid #aaa;
            padding: 4px;
        }

        QPushButton:hover, QComboBox:hover {
            border: 1px solid #0078d7;
        }
        """

    return ""  # fallback empty string
