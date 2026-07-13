# AI/ML Multi-Lab Environment Monorepo

Welcome to the **AI/ML Lab**. This monorepo is a beginner-friendly, educational environment for learning and experimenting with machine learning, deep learning, computer vision, natural language processing, and reinforcement learning.

It uses a modular **Docker Compose** structure so you can run each lab environment completely isolated, while sharing a unified network, volumes, and a centralized **MLflow** server for tracking your runs and metrics.

---

## 📂 Repository Structure

The monorepo is organized as follows:

```text
.
├── .env.example              # Configuration variables (ports, tokens)
├── .gitignore                # Git ignore patterns
├── Makefile                  # Simple build/run commands
├── README.md                 # Project documentation (this file)
├── compose.shared.yml        # Shared MLflow service, volumes, and networks
├── compose.basic-ml.yml      # Basic ML Lab Compose (scikit-learn, XGBoost, etc.)
├── compose.deep-ml.yml       # Deep ML Lab Compose (PyTorch, TensorFlow, etc.)
├── compose.nlp.yml           # NLP Lab Compose (spaCy, LangChain, vector DBs)
├── compose.cv.yml            # Computer Vision Lab Compose (OpenCV, YOLOv8)
├── compose.rl.yml            # Reinforcement Learning Lab Compose (Gymnasium, SB3)
│
├── base/                     # Shared base Dockerfiles
│   ├── Dockerfile.cpu        # Shared CPU Python 3.11 environment
│   └── Dockerfile.cuda123    # Shared GPU CUDA 12.3 environment
│
├── basic-ml/                 # Basic ML Lab
│   ├── Dockerfile            # Inherits from base/Dockerfile.cpu
│   ├── pyproject.toml        # Lab configuration and package specifications
│   ├── uv.lock               # Resolved locked dependencies
│   └── notebooks/            # Jupyter Notebooks folder (mounted)
│       └── starter_basic_ml.ipynb
│
├── deep-ml/                  # Deep ML Lab (GPU)
│   ├── Dockerfile            # Inherits from base/Dockerfile.cuda123
│   ├── pyproject.toml
│   ├── uv.lock
│   └── notebooks/
│       └── starter_deep_ml.ipynb
│
├── nlp-lab/                  # NLP Lab
│   ├── Dockerfile            # Inherits from base/Dockerfile.cpu
│   ├── pyproject.toml
│   ├── uv.lock
│   └── notebooks/
│       └── starter_nlp.ipynb
│
├── cv-lab/                   # Computer Vision Lab (GPU)
│   ├── Dockerfile            # Inherits from base/Dockerfile.cuda123
│   ├── pyproject.toml
│   ├── uv.lock
│   └── notebooks/
│       └── starter_cv.ipynb
│
├── rl-lab/                   # Reinforcement Learning Lab (GPU)
│   ├── Dockerfile            # Inherits from base/Dockerfile.cuda123
│   ├── pyproject.toml
│   ├── uv.lock
│   └── notebooks/
│       └── starter_rl.ipynb
│
└── shared/                   # Shared scripts and utilities
    └── scripts/
        └── wait-for-it.sh    # Script to sync Jupyter startup with MLflow
```

---

## 🚀 Getting Started

### Prerequisites
1. **Docker** and **Docker Compose (v2)** installed.
2. *(Optional)* **NVIDIA GPU** & **NVIDIA Container Toolkit** for GPU-accelerated labs (Deep ML, CV, RL).

---

### Step 1: Initialize the Environment
Copy the example environment file and initialize the shared networks and volumes:
```bash
make init
```
This creates your `.env` file and creates the shared Docker network `ml-lab-net` and volume `shared_notebooks`.

---

### Step 2: Build Base Images
Build the base CPU and CUDA images. This optimizes compilation and caching:
```bash
make build-base
```
*Note: If you do not have an NVIDIA GPU, you can build just the CPU base image: `make build-base-cpu`.*

---

### Step 3: Run a Lab Environment
To launch a specific lab, run the corresponding command:

| Lab | Command | Port | Primary Libraries |
| :--- | :--- | :--- | :--- |
| **Basic ML** | `make basic` | `http://localhost:8888` | scikit-learn, XGBoost, LightGBM, SHAP |
| **Deep ML** | `make deep` | `http://localhost:8889` | PyTorch, TensorFlow, Keras, Lightning |
| **NLP Lab** | `make nlp` | `http://localhost:8890` | spaCy, NLTK, LangChain, FAISS, Chroma |
| **CV Lab** | `make cv` | `http://localhost:8891` | OpenCV, YOLOv8, torchvision, SAM |
| **RL Lab** | `make rl` | `http://localhost:8892` | Gymnasium, Stable-Baselines3, Ray, MuJoCo |

When you launch any lab, **MLflow** starts automatically at **`http://localhost:5000`**.

---

### Step 4: Accessing JupyterLab
Open the URL shown in your terminal or navigate to the port corresponding to the lab. 
Enter the token defined in `.env` (default is **`antigravity`**).

---

## 🐳 Running Labs via Docker Compose Directly

You can skip the Makefile and run directly with Docker Compose by combining files.

**Example: Start Basic ML and MLflow**
```bash
docker compose -f compose.shared.yml -f compose.basic-ml.yml up -d --build
```

**Example: Start NLP Lab and MLflow**
```bash
docker compose -f compose.shared.yml -f compose.nlp.yml up -d --build
```

**Example: Stop all labs**
```bash
docker compose -f compose.shared.yml -f compose.basic-ml.yml -f compose.deep-ml.yml -f compose.nlp.yml -f compose.cv.yml -f compose.rl.yml down
```

---

## ⚡ GPU (NVIDIA CUDA 12.3) Support
Deep ML, CV, and RL labs are pre-configured to utilize your host NVIDIA GPU. 

### Prerequisites for GPU:
1. Ensure your host machine has NVIDIA drivers installed.
2. Install the **NVIDIA Container Toolkit**:
   - **Ubuntu/Debian**: [Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
   - **Windows**: Enable WSL2 GPU support.
3. Verify your installation by running:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
   ```

### CPU-Only Mode
If you do not have an NVIDIA GPU, you can run all labs on CPU:
1. Open the lab's `compose.<lab>.yml` file (e.g., `compose.deep-ml.yml`).
2. Comment out or delete the `deploy:` block at the bottom of the service definition:
   ```yaml
   # Comment out this block:
   # deploy:
   #   resources:
   #     reservations:
   #       devices:
   #         - driver: nvidia
   #           count: all
   #           capabilities: [gpu]
   ```

---

## 🛠️ Troubleshooting

### 1. `Error response from daemon: could not select device driver "" with capabilities: [gpu]`
*   **Cause**: Docker cannot access your GPU because the NVIDIA Container Toolkit is missing or not configured.
*   **Fix**: Install/configure the toolkit or follow the "CPU-Only Mode" instructions above to disable GPU requests.

### 2. `ImportError: libGL.so.1` or related rendering errors in CV / RL
*   **Cause**: Running GUI-bound code inside a headless Docker container.
*   **Fix**: Ensure you use `opencv-python-headless` instead of `opencv-python`. For RL rendering, verify the virtual display (`Display(visible=0)`) is initiated at the top of your notebooks.

### 3. MLflow Connection Errors
*   **Cause**: Jupyter container launched before the MLflow server was fully initialized.
*   **Fix**: The containers use `wait-for-it.sh` to delay startup. If a container fails to sync, run `make down` and start it again with `make <lab>`.
