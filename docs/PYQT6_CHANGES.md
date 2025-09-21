# PyQt6 Changes from PyQt5

This document summarizes the key changes when migrating from PyQt5 to PyQt6.

## 🔄 Import Changes

### WebEngine
```python
# PyQt5
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# PyQt6
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
```

### Core Modules
```python
# PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# PyQt6
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
```

## 🎯 Alignment Changes

### Qt.AlignCenter
```python
# PyQt5
Qt.AlignCenter
Qt.AlignLeft
Qt.AlignRight

# PyQt6
Qt.AlignmentFlag.AlignCenter
Qt.AlignmentFlag.AlignLeft
Qt.AlignmentFlag.AlignRight
```

### QSizePolicy Changes
```python
# PyQt5
QSizePolicy.Maximum
QSizePolicy.Preferred
QSizePolicy.Expanding
QSizePolicy.Minimum
QSizePolicy.Fixed
QSizePolicy.Ignored

# PyQt6
QSizePolicy.Policy.Maximum
QSizePolicy.Policy.Preferred
QSizePolicy.Policy.Expanding
QSizePolicy.Policy.Minimum
QSizePolicy.Policy.Fixed
QSizePolicy.Policy.Ignored
```

## 🔧 Method Changes

### Application Execution
```python
# PyQt5
sys.exit(app.exec_())

# PyQt6
sys.exit(app.exec())
```

### Dialog Execution
```python
# PyQt5
dialog.exec_()

# PyQt6
dialog.exec()
```

## 📋 Complete Migration Checklist

- [x] Update all imports from PyQt5 to PyQt6
- [x] Fix QWebEnginePage import (moved to QtWebEngineCore)
- [x] Update Qt.AlignCenter to Qt.AlignmentFlag.AlignCenter
- [x] Update Qt.AlignLeft to Qt.AlignmentFlag.AlignLeft
- [x] Update Qt.AlignRight to Qt.AlignmentFlag.AlignRight
- [x] Change app.exec_() to app.exec()
- [x] Test all functionality

## 🚀 Benefits of PyQt6

1. **Better Python 3.13 Support**: Full compatibility with latest Python
2. **Improved Performance**: Faster rendering and better memory management
3. **Modern API**: Cleaner, more consistent API design
4. **Better Type Hints**: Improved type checking and IDE support
5. **Active Development**: Ongoing updates and bug fixes

## 🔍 Common Issues and Solutions

### Import Errors
```python
# Problem: ModuleNotFoundError for PyQt6
# Solution: Install PyQt6
pip install PyQt6 PyQt6-WebEngine

# Problem: QWebEnginePage not found
# Solution: Import from QtWebEngineCore
from PyQt6.QtWebEngineCore import QWebEnginePage
```

### Alignment Errors
```python
# Problem: Qt.AlignCenter not found
# Solution: Use Qt.AlignmentFlag.AlignCenter
Qt.AlignmentFlag.AlignCenter
```

### Execution Errors
```python
# Problem: app.exec_() not found
# Solution: Use app.exec()
app.exec()
```

## 🎮 Your WikiRace Project

Your project has been successfully migrated to PyQt6 with:
- ✅ All imports updated
- ✅ All alignment flags fixed
- ✅ All method calls updated
- ✅ Python 3.13 compatibility
- ✅ Modern PyQt6 features

You can now run your WikiRace project with full PyQt6 support!
