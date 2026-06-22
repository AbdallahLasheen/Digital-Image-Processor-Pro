<div align="center">
  <img src="https://img.icons8.com/color/144/000000/opencv.png" alt="OpenCV Logo" width="100"/>
  <h1>🌌 PixelForge</h1>
  <p><b>Advanced AI-Powered Digital Image Processing Platform</b></p>

  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](#)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg?logo=flask&logoColor=white)](#)
  [![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg?logo=opencv&logoColor=white)](#)
  [![NumPy](https://img.shields.io/badge/NumPy-1.20+-4d77cf.svg?logo=numpy&logoColor=white)](#)
  [![Vanilla JS](https://img.shields.io/badge/JavaScript-ES6+-f7df1e.svg?logo=javascript&logoColor=black)](#)
  [![License](https://img.shields.io/badge/License-MIT-purple.svg)](#)

  <p>
    <i>A state-of-the-art web application for real-time computer vision transformations, developed as a comprehensive semester project for CSE281.</i>
  </p>
</div>

<br />

## 🌟 Executive Summary

**PixelForge** bridges the gap between complex backend computer vision algorithms and an ultra-modern, user-friendly frontend. By simply uploading an image, the system autonomously routes the file through a highly optimized 15-step OpenCV pipeline, returning a complete suite of image analytics, enhancements, segmentations, and noise simulations.

The user interface features a **Premium Dark Glassmorphic Design** with custom 3D hover effects, interactive particle backgrounds, and dynamic data visualization, ensuring a seamless and visually stunning user experience.

---

## 🚀 Key Features & Capabilities

### 1. 📈 Statistical Analysis
- **Core Metrics**: Automatically calculates Mean, Standard Deviation, Variance, Entropy, and Min/Max intensity bounds.
- **Dimensionality**: Extracts image width, height, and channel resolution.

### 2. ✨ Image Enhancement Pipeline
| Technique | Description | OpenCV Implementation |
| :--- | :--- | :--- |
| **Histogram Equalization** | Global contrast enhancement via cumulative distribution function mapping. | `cv2.equalizeHist()` |
| **CLAHE** | Contrast Limited Adaptive Histogram Equalization for localized contrast boosting without noise amplification. | `cv2.createCLAHE()` |
| **Laplacian Sharpening** | High-pass filtering to highlight edges and rapid intensity transitions. | `cv2.filter2D()` |

### 3. 🔍 Segmentation & Edge Detection
| Technique | Description | OpenCV Implementation |
| :--- | :--- | :--- |
| **Otsu's Thresholding** | Automatic binarization by minimizing intra-class variance. | `cv2.threshold(..., cv2.THRESH_OTSU)` |
| **Adaptive Thresholding** | Local thresholding to handle uneven illumination. | `cv2.adaptiveThreshold()` |
| **Canny Edge Detection** | Multi-stage algorithm (Gradient calculation, NMS, Hysteresis thresholding). | `cv2.Canny()` |
| **Watershed Algorithm** | Morphological marker-based segmentation for separating touching objects. | `cv2.watershed()` |

### 4. 📊 Frequency Domain Analysis (DFT)
- Computes the 2D Discrete Fourier Transform using `np.fft.fft2`.
- Shifts the zero-frequency component to the center (`fftshift`).
- Visualizes the logarithmic magnitude spectrum to analyze spatial frequencies.

### 5. 🔊 Noise Simulation & Denoising
- **Gaussian Noise**: Synthetically injects normally distributed noise ($\sigma = 40$).
- **Salt & Pepper Noise**: Randomly corrupts 5% of pixels to extreme values (0 or 255).
- **Gaussian Blur**: Applies a $5 \times 5$ Gaussian kernel to smooth the image.
- **Median Filter**: Utilizes a non-linear $5 \times 5$ median filter, highly effective for removing Salt & Pepper noise while preserving edges.

### 6. 🎨 Color Space Decomposition
- Isolates and visualizes individual channels across multiple color spaces:
  - **RGB**: Red, Green, Blue channels.
  - **HSV**: Hue, Saturation, Value (brightness).
  - **LAB**: Lightness, Green-Red (A), Blue-Yellow (B).

---

## 🛠️ Architecture & Tech Stack

### 🖥️ Frontend (Client-Side)
- **Vanilla HTML5 & CSS3**: Pure, framework-less styling ensuring zero-bloat and maximum performance.
- **Glassmorphism UI**: Advanced CSS properties (`backdrop-filter`, `mix-blend-mode`, 3D transforms).
- **Vanilla JavaScript (ES6+)**: Handles async API requests via Fetch API, DOM manipulation, and dynamic HTML injection.
- **Canvas API**: Renders real-time, interactive histogram comparison charts.
- **Particles.js**: Provides the interactive, lightweight animated background network.

### ⚙️ Backend (Server-Side)
- **Flask (Python)**: Lightweight WSGI web application framework routing API requests.
- **OpenCV (cv2)**: The core engine for all image processing algorithms.
- **NumPy**: Facilitates highly efficient, vectorized matrix operations and Fourier transforms.
- **Base64 Encoding**: In-memory image processing. Processed NumPy arrays are encoded directly to Base64 strings, eliminating the need for persistent disk writes and significantly reducing I/O latency.

---

## ⚙️ Installation & Local Deployment

### Prerequisites
- Python 3.8+
- Git

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/PixelForge.git
   cd PixelForge
   ```

2. **Initialize a Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Server**
   ```bash
   python app.py
   ```
   *The server will start on port 5000.*

5. **Access the Application**
   Open your preferred web browser and navigate to:
   [http://localhost:5000](http://localhost:5000)

---

## 🧠 System Workflow

1. **Upload**: User uploads an image via Drag & Drop or file explorer.
2. **Transmission**: Image is packaged into `FormData` and POSTed to the `/api/process` endpoint.
3. **Validation & Decoding**: Flask decodes the image stream into a `NumPy` array.
4. **Execution**: The 15-step OpenCV pipeline executes sequentially in-memory.
5. **Encoding**: Results are encoded to JPEG format, then to Base64 strings.
6. **Response**: A structured JSON object containing all Base64 images and statistical metrics is returned.
7. **Rendering**: The Vanilla JS engine parses the JSON, updates the DOM, and draws the histograms onto HTML5 canvases with staggered animations.

---

## 👤 Author
Developed with passion as a demonstration of applying modern web design paradigms to complex backend computer vision tasks.

<div align="center">
  <br>
  <i>"Transforming pixels into insights."</i>
</div>
