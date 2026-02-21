#!/bin/bash

VENV_DIR="venv"
BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== XivMind Backend Virtual Environment Setup ==="

cd "$BACKEND_DIR"

if [ -d "$VENV_DIR" ]; then
    echo ""
    echo "Virtual environment already exists at: $BACKEND_DIR/$VENV_DIR"
    echo ""
    echo "Please choose an option:"
    echo "  [1] Delete and recreate (remove old venv, create new one)"
    echo "  [2] Activate existing (keep current venv, just activate it)"
    echo "  [3] Exit (cancel operation)"
    echo ""
    
    read -p "Enter your choice (1/2/3): " Choice
    
    case $Choice in
        1)
            echo "Removing existing venv..."
            rm -rf "$VENV_DIR"
            ;;
        2)
            echo ""
            echo "To activate the virtual environment, please run:"
            echo "    source $VENV_DIR/bin/activate"
            echo ""
            echo "Or source this script to keep activation in current shell:"
            echo "    source ./setup_venv.sh"
            echo ""
            exit 0
            ;;
        3)
            echo "Operation cancelled."
            exit 0
            ;;
        *)
            echo "Invalid choice. Operation cancelled."
            exit 1
            ;;
    esac
fi

echo ""
echo "Select PyTorch version:"
echo "  [1] CPU only (smaller, no GPU support)"
echo "  [2] GPU with CUDA 12.1 (requires NVIDIA GPU)"
echo "  [3] GPU with CUDA 11.8 (requires NVIDIA GPU)"
echo ""

read -p "Enter your choice (1/2/3): " TorchChoice

echo "Creating new virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Upgrading pip..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip

echo "Installing base dependencies..."
"$VENV_DIR/bin/pip" install "setuptools>=68.0.0"

case $TorchChoice in
    1)
        echo "Installing PyTorch (CPU version)..."
        "$VENV_DIR/bin/pip" install torch --index-url https://download.pytorch.org/whl/cpu
        ;;
    2)
        echo "Installing PyTorch (CUDA 12.1)..."
        "$VENV_DIR/bin/pip" install torch --index-url https://download.pytorch.org/whl/cu121
        ;;
    3)
        echo "Installing PyTorch (CUDA 11.8)..."
        "$VENV_DIR/bin/pip" install torch --index-url https://download.pytorch.org/whl/cu118
        ;;
    *)
        echo "Invalid choice. Installing CPU version by default..."
        "$VENV_DIR/bin/pip" install torch --index-url https://download.pytorch.org/whl/cpu
        ;;
esac

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "Installing dev dependencies..."
"$VENV_DIR/bin/pip" install pytest pytest-asyncio==0.23.6

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Virtual environment created at: $BACKEND_DIR/$VENV_DIR"
echo ""
echo "To activate the virtual environment, run:"
echo "    source $VENV_DIR/bin/activate"
echo ""
echo "To run tests:"
echo "    pytest tests/"
echo ""
