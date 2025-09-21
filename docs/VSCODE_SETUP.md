# Running WikiRace from VSCode

This guide shows you how to run and debug your WikiRace project directly from VSCode using Python 3.13.

## 🚀 Quick Start

### 1. **First Time Setup**
Before running the project, make sure you've set up the environment:

1. **Run the setup script** (choose one):
   ```cmd
   # Option 1: Batch file
   setup.bat
   
   # Option 2: Python script
   python setup_environment.py
   ```

2. **Test your setup**:
   ```cmd
   python test_python313.py
   ```

### 2. **Running from VSCode**

#### Method 1: Using the Debug Panel (Recommended)
1. **Open VSCode** in your project folder
2. **Go to the Debug panel** (Ctrl+Shift+D)
3. **Select "WikiRace - Main Application"** from the dropdown
4. **Click the green play button** or press F5

#### Method 2: Using the Command Palette
1. **Press Ctrl+Shift+P**
2. **Type "Python: Select Interpreter"**
3. **Choose your Python 3.13 interpreter**
4. **Open `src/app.py`**
5. **Press F5** to run

#### Method 3: Using the Terminal
1. **Open integrated terminal** (Ctrl+`)
2. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
3. **Run the application**:
   ```cmd
   python bin/main.py
   ```

#### Method 4: Running the Multiplayer Server
1. **Open integrated terminal** (Ctrl+`)
2. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
3. **Start the server**:
   ```cmd
   python server/start_server.py
   ```

## 🔧 Debug Configurations

I've set up several debug configurations for you:

### 1. **WikiRace - Main Application**
- **Purpose**: Run the main WikiRace game
- **File**: `bin/main.py`
- **Python**: Uses your local Python 3.13
- **Features**: Full debugging support

### 2. **WikiRace - Multiplayer Server**
- **Purpose**: Run the multiplayer server for real-time gaming
- **File**: `server/start_server.py`
- **Python**: Uses your local Python 3.13
- **Features**: FastAPI server with Socket.IO support

### 3. **WikiRace - Test Setup**
- **Purpose**: Test your Python 3.13 setup
- **File**: `test_python313.py`
- **Use**: Verify everything is working correctly

### 4. **WikiRace - Setup Environment**
- **Purpose**: Run the setup script
- **File**: `setup_environment.py`
- **Use**: Set up dependencies and virtual environment

### 5. **Python Debugger: Current File**
- **Purpose**: Run any Python file you have open
- **Use**: For testing individual components

## 🐛 Debugging Features

### Breakpoints
- **Set breakpoints** by clicking in the left margin of any line
- **Conditional breakpoints** by right-clicking and selecting "Edit Breakpoint"
- **Logpoints** for logging without stopping execution

### Debug Console
- **Inspect variables** during debugging
- **Execute Python code** in the current context
- **Test expressions** and function calls

### Variable Inspection
- **Hover over variables** to see their values
- **Expand complex objects** in the Variables panel
- **Watch specific expressions** in the Watch panel

## ⚙️ VSCode Settings

I've configured VSCode with optimal settings for your project:

- **Python Interpreter**: Points to your local Python 3.13
- **Linting**: Enabled with flake8
- **Formatting**: Black code formatter
- **Type Checking**: Basic type checking enabled
- **Auto Import**: Automatic import completions

## 🎯 Common Tasks

### Running the Game
1. **F5** → Select "WikiRace - Main Application"
2. **Wait for the GUI** to load
3. **Start playing!**

### Testing Setup
1. **F5** → Select "WikiRace - Test Setup"
2. **Check the output** for any issues
3. **Fix any problems** before running the main app

### Debugging Issues
1. **Set breakpoints** in the code where you suspect issues
2. **Run with F5** to start debugging
3. **Step through the code** using F10 (step over) or F11 (step into)
4. **Inspect variables** in the Debug Console

### Code Formatting
1. **Right-click** in any Python file
2. **Select "Format Document"** or press Shift+Alt+F
3. **Code will be formatted** according to Black standards

## 🔍 Troubleshooting

### Python Not Found
- **Check**: `.vscode/settings.json` points to correct Python path
- **Verify**: `Python313/python.exe` exists
- **Solution**: Update the `python.defaultInterpreterPath` in settings

### Import Errors
- **Check**: Virtual environment is activated
- **Verify**: Dependencies are installed (`pip install -e .`)
- **Solution**: Run setup script again

### GUI Not Showing
- **Check**: PyQt6 is installed correctly
- **Verify**: No error messages in the Debug Console
- **Solution**: Try running from terminal first

### Debugging Not Working
- **Check**: Python extension is installed
- **Verify**: Debug configuration is selected
- **Solution**: Restart VSCode and try again

## 📋 Keyboard Shortcuts

- **F5**: Start debugging
- **F10**: Step over (next line)
- **F11**: Step into (enter function)
- **Shift+F11**: Step out (exit function)
- **Ctrl+Shift+F5**: Restart debugging
- **Shift+F5**: Stop debugging
- **Ctrl+Shift+P**: Command palette

## 💡 Pro Tips

1. **Use the Debug Console** to test code snippets
2. **Set conditional breakpoints** for specific scenarios
3. **Use the Watch panel** to monitor important variables
4. **Enable "justMyCode": false** to debug into libraries
5. **Use the Call Stack** to understand execution flow

## 🎮 Ready to Play!

Your WikiRace project is now fully configured for VSCode development. You can:

- **Run the game** with F5
- **Debug issues** with breakpoints
- **Format code** automatically
- **Test components** individually
- **Develop new features** with full IDE support

Happy coding! 🚀
