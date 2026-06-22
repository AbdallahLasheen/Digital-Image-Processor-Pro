"""
PixelForge - Advanced Digital Image Processing Platform
========================================================
Flask backend with comprehensive image processing pipeline.

Enhancement: Histogram Equalization, CLAHE, Sharpening, Brightness/Contrast
Segmentation: Otsu, Canny Edge, Watershed, Adaptive Threshold
Analysis: DFT, Color Spaces, Noise, Statistics
"""

import os, cv2, numpy as np, base64, io, zipfile, tempfile
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

# C: drive is full locally, route temporary file uploads to a local tmp folder
# Ignore if running on Vercel (which uses a read-only filesystem except for /tmp)
try:
    if not os.environ.get('VERCEL'):
        tmp_folder = os.path.join(os.path.dirname(__file__), 'tmp')
        os.makedirs(tmp_folder, exist_ok=True)
        tempfile.tempdir = tmp_folder
except Exception:
    pass

app = Flask(__name__, static_folder='static')
CORS(app)

def img_to_b64(image):
    _, buf = cv2.imencode('.png', image)
    return base64.b64encode(buf).decode('utf-8')

def hist_data(image):
    g = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    return cv2.calcHist([g], [0], None, [256], [0, 256]).flatten().tolist()

# ===================== ENHANCEMENT =====================

def enhance_histogram_eq(img):
    if len(img.shape) == 3:
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    return cv2.equalizeHist(img)

def enhance_clahe(img, clip=3.0, grid=8):
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    if len(img.shape) == 3:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return clahe.apply(img)

def enhance_sharpen(img):
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    return cv2.filter2D(img, -1, kernel)

def enhance_brightness_contrast(img, alpha=1.3, beta=30):
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# ===================== SEGMENTATION =====================

def segment_otsu(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    blur = cv2.GaussianBlur(g, (5,5), 0)
    thresh_val, seg = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return seg, float(thresh_val)

def segment_canny(img, low=30, high=200):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    blur = cv2.GaussianBlur(g, (5,5), 0)
    edges = cv2.Canny(blur, low, high)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    overlay = img.copy() if len(img.shape) == 3 else cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(overlay, contours, -1, (0,255,0), 2)
    return edges, overlay, len(contours)

def segment_adaptive(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    blur = cv2.GaussianBlur(g, (5,5), 0)
    return cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

def segment_watershed(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    _, thresh = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    dist = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    color = img.copy() if len(img.shape) == 3 else cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    markers = cv2.watershed(color, markers)
    result = color.copy()
    result[markers == -1] = [0, 0, 255]
    return result, int(markers.max() - 1)

# ===================== ANALYSIS =====================

def analyze_dft(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    f = np.float32(g)
    dft = cv2.dft(f, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    mag = cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1])
    mag = 20 * np.log(mag + 1)
    mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return mag

def analyze_color_spaces(img):
    if len(img.shape) != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    b, g, r = cv2.split(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a_ch, b_ch = cv2.split(lab)
    return {'r': r, 'g': g, 'b': b, 'h': h, 's': s, 'v': v, 'l': l, 'a': a_ch, 'b_lab': b_ch}

def add_noise(img, noise_type='gaussian', amount=50):
    if noise_type == 'gaussian':
        noise = np.random.normal(0, amount, img.shape).astype(np.float64)
        noisy = np.clip(img.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    else:  # salt_pepper
        noisy = img.copy()
        prob = amount / 500.0
        salt = np.random.random(img.shape[:2]) < prob
        pepper = np.random.random(img.shape[:2]) < prob
        if len(img.shape) == 3:
            noisy[salt] = [255, 255, 255]
            noisy[pepper] = [0, 0, 0]
        else:
            noisy[salt] = 255
            noisy[pepper] = 0
    return noisy

def denoise(img, method='median', ksize=5):
    if method == 'median':
        return cv2.medianBlur(img, ksize)
    elif method == 'gaussian':
        return cv2.GaussianBlur(img, (ksize, ksize), 0)
    else:  # bilateral
        return cv2.bilateralFilter(img, 9, 75, 75)

def image_stats(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    return {
        'mean': round(float(np.mean(g)), 2),
        'std': round(float(np.std(g)), 2),
        'min': int(np.min(g)),
        'max': int(np.max(g)),
        'median': int(np.median(g)),
        'pixels': int(g.size),
        'entropy': round(float(-np.sum((cv2.calcHist([g],[0],None,[256],[0,256]).flatten()/g.size + 1e-10) * np.log2(cv2.calcHist([g],[0],None,[256],[0,256]).flatten()/g.size + 1e-10))), 2)
    }

# ===================== ROUTES =====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    buf = np.frombuffer(file.read(), np.uint8)
    original = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if original is None:
        return jsonify({'error': 'Invalid image'}), 400

    h, w = original.shape[:2]
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # Enhancement
    eh1 = enhance_histogram_eq(original)
    eh2 = enhance_clahe(original)
    eh3 = enhance_sharpen(original)
    eh4 = enhance_brightness_contrast(original)

    # Segmentation
    seg_otsu, otsu_thresh = segment_otsu(original)
    seg_edges, seg_contours, n_contours = segment_canny(original)
    seg_adaptive = segment_adaptive(original)
    seg_water, n_regions = segment_watershed(original)

    # Analysis
    dft_mag = analyze_dft(original)
    colors = analyze_color_spaces(original)
    stats = image_stats(original)

    # Noise demo
    noisy_gauss = add_noise(original, 'gaussian', 40)
    noisy_sp = add_noise(original, 'salt_pepper', 30)
    denoised_median = denoise(noisy_sp, 'median')
    denoised_gauss = denoise(noisy_gauss, 'gaussian')

    return jsonify({
        'success': True,
        'info': {'w': w, 'h': h, 'ch': original.shape[2] if len(original.shape) == 3 else 1, 'name': file.filename},
        'stats': stats,
        'original': {'color': img_to_b64(original), 'gray': img_to_b64(gray)},
        'enhancement': {
            'histEq': {'img': img_to_b64(eh1), 'name': 'Histogram Equalization', 'code': 'cv2.equalizeHist()', 'desc': 'Spreads intensity values evenly across histogram for better contrast.'},
            'clahe': {'img': img_to_b64(eh2), 'name': 'CLAHE', 'code': 'cv2.createCLAHE()', 'desc': 'Adaptive histogram equalization on local tiles. clipLimit=3.0, tileGrid=8×8.'},
            'sharpen': {'img': img_to_b64(eh3), 'name': 'Sharpening Filter', 'code': 'cv2.filter2D()', 'desc': 'Laplacian-based sharpening kernel enhances edges and fine details.'},
            'brightness': {'img': img_to_b64(eh4), 'name': 'Brightness & Contrast', 'code': 'cv2.convertScaleAbs()', 'desc': 'Linear transform: α=1.3 (contrast), β=30 (brightness).'}
        },
        'segmentation': {
            'otsu': {'img': img_to_b64(seg_otsu), 'name': "Otsu's Thresholding", 'code': 'THRESH_BINARY + THRESH_OTSU', 'desc': f'Auto threshold = {otsu_thresh:.0f}', 'thresh': otsu_thresh},
            'canny': {'edges': img_to_b64(seg_edges), 'contours': img_to_b64(seg_contours), 'name': 'Canny Edge Detection', 'code': 'cv2.Canny() + findContours()', 'desc': f'Found {n_contours} contours. Thresholds: 30/200.', 'n': n_contours},
            'adaptive': {'img': img_to_b64(seg_adaptive), 'name': 'Adaptive Threshold', 'code': 'cv2.adaptiveThreshold()', 'desc': 'Gaussian adaptive thresholding with blockSize=11, C=2.'},
            'watershed': {'img': img_to_b64(seg_water), 'name': 'Watershed', 'code': 'cv2.watershed()', 'desc': f'Distance transform + watershed. {n_regions} regions found.', 'regions': n_regions}
        },
        'analysis': {
            'dft': img_to_b64(dft_mag),
            'colors': {k: img_to_b64(v) for k, v in colors.items()},
            'noise': {
                'gaussian': img_to_b64(noisy_gauss), 'saltPepper': img_to_b64(noisy_sp),
                'denoisedMedian': img_to_b64(denoised_median), 'denoisedGaussian': img_to_b64(denoised_gauss)
            }
        },
        'histograms': {'original': hist_data(original), 'histEq': hist_data(eh1), 'clahe': hist_data(eh2)}
    })

@app.route('/api/adjust', methods=['POST'])
def adjust_params():
    """Real-time parameter adjustment endpoint."""
    data = request.json
    img_b64 = data.get('image')
    if not img_b64:
        return jsonify({'error': 'No image'}), 400
    
    buf = base64.b64decode(img_b64)
    arr = np.frombuffer(buf, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    
    op = data.get('operation')
    params = data.get('params', {})
    
    if op == 'clahe':
        result = enhance_clahe(img, clip=params.get('clip', 3.0), grid=params.get('grid', 8))
    elif op == 'canny':
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.Canny(g, params.get('low', 30), params.get('high', 200))
    elif op == 'threshold':
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, result = cv2.threshold(g, params.get('value', 127), 255, cv2.THRESH_BINARY)
    elif op == 'brightness':
        result = enhance_brightness_contrast(img, alpha=params.get('alpha', 1.3), beta=params.get('beta', 30))
    else:
        return jsonify({'error': 'Unknown operation'}), 400
    
    return jsonify({'success': True, 'img': img_to_b64(result)})

if __name__ == '__main__':
    print("\n" + "="*55)
    print("  PixelForge - Digital Image Processing Platform")
    print("  CSE281 Semester Project")
    print("="*55)
    print("\n  -> http://localhost:5000\n")
    app.run(debug=True, port=5000)
