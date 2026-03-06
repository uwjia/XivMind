#!/bin/bash

echo "=========================================="
echo "  Install PyTorch from Local Wheels"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default wheel directory
WHEEL_DIR="$HOME/Downloads"

echo ""
echo "Local wheel files should be in: $WHEEL_DIR"
echo "Expected files:"
echo "  - torch-2.8.0+cu128-cp312-cp312-linux_x86_64.whl (or similar)"
echo "  - torchvision-0.23.0+cu128-cp312-cp312-linux_x86_64.whl (or similar)"
echo ""

read -p "Enter wheel directory path (or press Enter for default): " INPUT_DIR
if [ -n "$INPUT_DIR" ]; then
    WHEEL_DIR="$INPUT_DIR"
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "ERROR: Virtual environment not found!"
    echo ""
    echo "Please run the following command first to create the virtual environment:"
    echo "  ./start.sh install"
    echo ""
    echo "Or for development mode:"
    echo "  ./start.sh dev"
    echo ""
    exit 1
fi

# Find wheel files
TORCH_WHEEL=$(find "$WHEEL_DIR" -name "torch-*+cu*-cp312-*.whl" 2>/dev/null | head -1)
TORCHVISION_WHEEL=$(find "$WHEEL_DIR" -name "torchvision-*+cu*-cp312-*.whl" 2>/dev/null | head -1)

if [ -z "$TORCH_WHEEL" ]; then
    echo "ERROR: torch wheel not found in $WHEEL_DIR"
    echo ""
    echo "Please download from: https://download.pytorch.org/whl/cu128/torch/"
    exit 1
fi

if [ -z "$TORCHVISION_WHEEL" ]; then
    echo "ERROR: torchvision wheel not found in $WHEEL_DIR"
    echo ""
    echo "Please download from: https://download.pytorch.org/whl/cu128/torchvision/"
    exit 1
fi

echo "Found wheel files:"
echo "  - $TORCH_WHEEL"
echo "  - $TORCHVISION_WHEEL"
echo ""

source venv/bin/activate

echo "Installing PyTorch from local wheels..."
pip install "$TORCH_WHEEL" "$TORCHVISION_WHEEL"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyTorch."
    exit 1
fi

echo ""
echo "Installing pillow (required by torchvision)..."
pip install pillow>=9.0.0

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "To verify PyTorch GPU:"
echo "  python -c \"import torch; print('CUDA available:', torch.cuda.is_available())\""
echo ""
