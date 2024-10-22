import pytest
from Wisp import MainWindow
from unittest.mock import patch

@pytest.fixture
def app(qtbot):
    """Fixture to initialize the MainWindow with forced English texts."""
    with patch("lang.LANG", "EN"):  # Force language to English
        window = MainWindow()
        qtbot.addWidget(window)
        return window

def test_app_starts(app):
    """Test to ensure the application starts and the main window is visible."""
    assert app.isVisible(), "Main window is not visible after startup."

# TODO: add additional tests for the GUI elements