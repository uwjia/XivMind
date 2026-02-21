import subprocess
import sys
import platform
import os


def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1


def check_nvidia_driver():
    output, code = run_command("nvidia-smi --query-gpu=driver_version --format=csv,noheader")
    if code == 0 and output:
        return output.split('\n')[0].strip()
    return None


def check_cuda_version():
    output, code = run_command("nvidia-smi --query-gpu=compute_cap --format=csv,noheader")
    if code == 0 and output:
        return output.split('\n')[0].strip()
    
    output, code = run_command("nvcc --version")
    if code == 0 and "release" in output:
        for line in output.split('\n'):
            if "release" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "release" and i + 1 < len(parts):
                        return parts[i + 1].rstrip(',')
    return None


def get_cuda_version_from_nvidia_smi():
    output, code = run_command("nvidia-smi")
    if code == 0:
        for line in output.split('\n'):
            if "CUDA Version" in line:
                for part in line.split():
                    try:
                        version = float(part)
                        if version >= 10:
                            return part
                    except:
                        continue
    return None


def check_gpu_info():
    output, code = run_command("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
    if code == 0 and output:
        lines = output.strip().split('\n')
        gpus = []
        for line in lines:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    memory = parts[1].strip()
                    gpus.append(f"{name} ({memory})")
        return gpus
    return []


def check_apple_silicon():
    if platform.system() == "Darwin":
        output, code = run_command("sysctl -n machinfo.cpu.brand_string")
        if code == 0:
            cpu_info = output.lower()
            if "apple" in cpu_info or "m1" in cpu_info or "m2" in cpu_info or "m3" in cpu_info:
                return True
        output, code = run_command("sysctl -n hw.optional.arm64")
        if code == 0 and output == "1":
            return True
    return False


def check_existing_pytorch():
    try:
        import torch
        version = torch.__version__
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if cuda_available else None
        mps_available = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        return {
            "installed": True,
            "version": version,
            "cuda_available": cuda_available,
            "cuda_version": cuda_version,
            "mps_available": mps_available
        }
    except ImportError:
        return {"installed": False}


def get_pytorch_install_command(cuda_version=None, use_mps=False):
    base_cmd = "pip install torch torchvision torchaudio"
    
    if use_mps:
        return base_cmd + "  # Apple Silicon (MPS)"
    
    if cuda_version:
        try:
            ver = float(cuda_version)
            if ver >= 12.8:
                return f"{base_cmd} --index-url https://download.pytorch.org/whl/cu128"
            elif ver >= 12.1:
                return f"{base_cmd} --index-url https://download.pytorch.org/whl/cu121"
            elif ver >= 11.8:
                return f"{base_cmd} --index-url https://download.pytorch.org/whl/cu118"
            else:
                return f"{base_cmd} --index-url https://download.pytorch.org/whl/cu118  # CUDA 11.8 (oldest supported)"
        except:
            return f"{base_cmd} --index-url https://download.pytorch.org/whl/cu121"
    
    return base_cmd + "  # CPU only"


def main():
    print("=" * 70)
    print("PyTorch Installation Detection Script")
    print("=" * 70)
    
    print(f"\n[1] System Information")
    print(f"    OS: {platform.system()} {platform.release()}")
    print(f"    Python: {platform.python_version()}")
    print(f"    Architecture: {platform.machine()}")
    
    print(f"\n[2] GPU Detection")
    
    gpus = check_gpu_info()
    has_nvidia = len(gpus) > 0
    has_apple_silicon = check_apple_silicon()
    
    if has_nvidia:
        print(f"    NVIDIA GPU detected:")
        for gpu in gpus:
            print(f"      - {gpu}")
        
        driver = check_nvidia_driver()
        if driver:
            print(f"    Driver Version: {driver}")
        
        cuda_ver = get_cuda_version_from_nvidia_smi()
        if cuda_ver:
            print(f"    CUDA Version: {cuda_ver}")
    elif has_apple_silicon:
        print("    Apple Silicon GPU detected (MPS supported)")
    else:
        print("    No NVIDIA GPU or Apple Silicon detected")
        print("    Will use CPU only")
    
    print(f"\n[3] Existing PyTorch Installation")
    pytorch_info = check_existing_pytorch()
    if pytorch_info["installed"]:
        print(f"    PyTorch Version: {pytorch_info['version']}")
        print(f"    CUDA Available: {pytorch_info['cuda_available']}")
        if pytorch_info['cuda_version']:
            print(f"    CUDA Version: {pytorch_info['cuda_version']}")
        print(f"    MPS Available: {pytorch_info['mps_available']}")
    else:
        print("    PyTorch not installed")
    
    print(f"\n[4] Recommended Installation")
    print("-" * 70)
    
    if has_nvidia:
        cuda_ver = get_cuda_version_from_nvidia_smi()
        cmd = get_pytorch_install_command(cuda_version=cuda_ver)
        print(f"    Device: NVIDIA GPU (CUDA {cuda_ver})")
        print(f"\n    Command:")
        print(f"    {cmd}")
    elif has_apple_silicon:
        cmd = get_pytorch_install_command(use_mps=True)
        print("    Device: Apple Silicon (MPS)")
        print(f"\n    Command:")
        print(f"    {cmd}")
    else:
        cmd = get_pytorch_install_command()
        print("    Device: CPU only")
        print(f"\n    Command:")
        print(f"    {cmd}")
    
    print("\n" + "=" * 70)
    print("Notes:")
    print("  - CUDA 12.8: Latest, recommended for RTX 40-series, RTX 50-series")
    print("  - CUDA 12.1: Stable, good compatibility")
    print("  - CUDA 11.8: For older GPUs (GTX 10-series, RTX 20-series)")
    print("  - MPS: Apple Silicon Mac (M1/M2/M3)")
    print("=" * 70)


if __name__ == "__main__":
    main()
