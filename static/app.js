/**
 * PixelForge - Advanced Image Processing Platform
 * Frontend Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    const $ = id => document.getElementById(id);
    const dropZone = $('dropZone'), fileInput = $('fileInput'), preview = $('preview');
    const previewImg = $('previewImg'), previewName = $('previewName'), previewMeta = $('previewMeta');
    const resultsEl = $('results'), summaryEl = $('summary'), loader = $('loader');
    let selectedFile = null, processedData = null;



    // ===== Navbar =====
    const navbar = $('navbar');
    window.addEventListener('scroll', () => navbar.classList.toggle('scrolled', scrollY > 60));

    // Active link tracking
    const sectionObs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                const link = document.querySelector(`.nav-link[data-target="${e.target.id}"]`);
                if (link) link.classList.add('active');
            }
        });
    }, { threshold: 0.25 });
    document.querySelectorAll('section[id]').forEach(s => sectionObs.observe(s));

    // ===== Stat counters =====
    document.querySelectorAll('.stat-num').forEach(el => {
        const target = +el.dataset.n; let cur = 0;
        const iv = setInterval(() => { cur = Math.min(cur + 1, target); el.textContent = cur; if (cur >= target) clearInterval(iv); }, 80);
    });

    // ===== Smooth scroll helper =====
    window.scrollTo_ = sel => document.querySelector(sel)?.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // ===== Upload =====
    dropZone.addEventListener('click', () => fileInput.click());
    ['dragenter', 'dragover'].forEach(e => dropZone.addEventListener(e, ev => { ev.preventDefault(); dropZone.classList.add('drag-over'); }));
    ['dragleave', 'drop'].forEach(e => dropZone.addEventListener(e, ev => { ev.preventDefault(); dropZone.classList.remove('drag-over'); }));
    dropZone.addEventListener('drop', e => e.dataTransfer.files[0] && handleFile(e.dataTransfer.files[0]));
    fileInput.addEventListener('change', e => e.target.files[0] && handleFile(e.target.files[0]));

    function handleFile(file) {
        if (!file.type.startsWith('image/')) return toast('Please select a valid image.', 'error');
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = e => {
            previewImg.src = e.target.result;
            previewName.textContent = file.name;
            previewMeta.textContent = `${(file.size / 1024).toFixed(1)} KB • ${file.type}`;
            preview.classList.remove('hidden');
            resultsEl.classList.add('hidden');
            summaryEl.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    $('btnRemove').addEventListener('click', () => {
        selectedFile = null; preview.classList.add('hidden'); fileInput.value = '';
        resultsEl.classList.add('hidden'); summaryEl.classList.add('hidden');
    });
    $('btnAnother')?.addEventListener('click', () => {
        scrollTo_('#upload'); selectedFile = null; preview.classList.add('hidden'); fileInput.value = '';
        resultsEl.classList.add('hidden'); summaryEl.classList.add('hidden');
    });

    $('btnProcess').addEventListener('click', () => selectedFile ? processImage(selectedFile) : toast('Select an image first!', 'error'));

    // ===== Tabs =====
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            $('tab-' + tab.dataset.tab).classList.add('active');
            // Re-trigger card animations
            $('tab-' + tab.dataset.tab).querySelectorAll('.card').forEach((c, i) => {
                c.style.animationDelay = `${i * 0.08}s`;
                c.style.animation = 'none'; c.offsetHeight; c.style.animation = '';
            });
        });
    });

    // ===== Process =====
    async function processImage(file) {
        loader.classList.remove('hidden');
        animateSteps();
        const fd = new FormData(); fd.append('image', file);
        try {
            const res = await fetch('/api/process', { method: 'POST', body: fd });
            const data = await res.json();
            if (!data.success) throw new Error(data.error);
            processedData = data;
            await delay(2800);
            loader.classList.add('hidden');
            populateResults(data);
            resultsEl.classList.remove('hidden');
            summaryEl.classList.remove('hidden');
            await delay(200);
            resultsEl.scrollIntoView({ behavior: 'smooth' });
            toast('Image processed successfully!', 'success');
        } catch (err) {
            loader.classList.add('hidden');
            toast('Error: ' + err.message, 'error');
        }
    }

    function populateResults(d) {
        const b64 = (s) => 'data:image/png;base64,' + s;
        const setImg = (id, s) => { const el = $(id); if (el) el.src = b64(s); };

        // Original
        setImg('imgOrgColor', d.original.color);
        setImg('imgOrgGray', d.original.gray);
        setImg('imgDFT', d.analysis.dft);

        // Stats
        $('sMean').textContent = d.stats.mean;
        $('sStd').textContent = d.stats.std;
        $('sMin').textContent = d.stats.min;
        $('sMax').textContent = d.stats.max;
        $('sMedian').textContent = d.stats.median;
        $('sEntropy').textContent = d.stats.entropy;
        $('sPixels').textContent = d.stats.pixels.toLocaleString();
        $('sDims').textContent = `${d.info.w}×${d.info.h}`;

        // Enhancement
        const eGrid = $('enhanceGrid');
        eGrid.innerHTML = '';
        const eKeys = Object.keys(d.enhancement);
        const eBadges = ['b-purple', 'b-cyan', 'b-orange', 'b-green'];
        eKeys.forEach((k, i) => {
            const e = d.enhancement[k];
            eGrid.innerHTML += `<div class="card" style="animation-delay:${i * .1}s">
                <div class="card-head"><span class="badge ${eBadges[i]}">Tech ${i + 1}</span><span>${e.name}</span></div>
                <div class="card-body"><img src="${b64(e.img)}" alt="${e.name}"></div>
                <div class="card-foot"><code>${e.code}</code><p>${e.desc}</p></div>
            </div>`;
        });

        // Segmentation
        const sGrid = $('segGrid');
        sGrid.innerHTML = '';
        const sKeys = ['otsu', 'adaptive', 'watershed'];
        const sBadges = ['b-orange', 'b-purple', 'b-blue'];
        sKeys.forEach((k, i) => {
            const s = d.segmentation[k];
            let extra = '';
            if (k === 'otsu') extra = `<div class="metric"><span>Threshold</span><span>${s.thresh.toFixed(0)}</span></div>`;
            if (k === 'watershed') extra = `<div class="metric"><span>Regions</span><span>${s.regions}</span></div>`;
            sGrid.innerHTML += `<div class="card" style="animation-delay:${i * .1}s">
                <div class="card-head"><span class="badge ${sBadges[i]}">${k}</span><span>${s.name}</span></div>
                <div class="card-body"><img src="${b64(s.img)}" alt="${s.name}"></div>
                <div class="card-foot" style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap"><div><code>${s.code}</code><p>${s.desc}</p></div>${extra}</div>
            </div>`;
        });
        // Canny
        const canny = d.segmentation.canny;
        sGrid.innerHTML += `<div class="card" style="animation-delay:.3s">
            <div class="card-head"><span class="badge b-green">Canny</span><span>${canny.name}</span></div>
            <div class="card-body"><img src="${b64(canny.edges)}" alt="Canny"></div>
            <div class="card-foot" style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap"><div><code>${canny.code}</code><p>${canny.desc}</p></div><div class="metric"><span>Contours</span><span>${canny.n}</span></div></div>
        </div>`;
        setImg('imgContours', canny.contours);

        // Noise
        setImg('imgNoiseG', d.analysis.noise.gaussian);
        setImg('imgNoiseSP', d.analysis.noise.saltPepper);
        setImg('imgDenG', d.analysis.noise.denoisedGaussian);
        setImg('imgDenM', d.analysis.noise.denoisedMedian);

        // Colors
        const ch = d.analysis.colors;
        setImg('chR', ch.r); setImg('chG', ch.g); setImg('chB', ch.b);
        setImg('chH', ch.h); setImg('chS', ch.s); setImg('chV', ch.v);
        setImg('chL', ch.l); setImg('chA', ch.a); setImg('chBL', ch.b_lab);

        // Histograms
        drawHist('histMain', d.histograms.original, '#7d7d9a', 200);
        drawHist('hOrg', d.histograms.original, '#7d7d9a');
        drawHist('hEq', d.histograms.histEq, '#7c5cfc');
        drawHist('hClahe', d.histograms.clahe, '#00d4ff');

        // Summary
        buildSummary(d);
    }

    function buildSummary(d) {
        const b64 = s => 'data:image/png;base64,' + s;
        const items = [
            { label: 'Original', color: '#00d4ff', img: d.original.color },
            { label: 'Histogram Eq.', color: '#7c5cfc', img: d.enhancement.histEq.img },
            { label: 'CLAHE', color: '#00d4ff', img: d.enhancement.clahe.img },
            { label: 'Sharpening', color: '#ffd93d', img: d.enhancement.sharpen.img },
            { label: "Otsu's Threshold", color: '#ffd93d', img: d.segmentation.otsu.img },
            { label: 'Canny Edges', color: '#00c853', img: d.segmentation.canny.edges },
            { label: 'Adaptive Thresh.', color: '#7c5cfc', img: d.segmentation.adaptive.img },
            { label: 'Watershed', color: '#00d4ff', img: d.segmentation.watershed.img },
            { label: 'Contour Overlay', color: '#00c853', img: d.segmentation.canny.contours },
            { label: 'DFT Spectrum', color: '#7c5cfc', img: d.analysis.dft },
            { label: 'Gaussian Noise', color: '#ff6b6b', img: d.analysis.noise.gaussian },
            { label: 'Denoised (Median)', color: '#00c853', img: d.analysis.noise.denoisedMedian },
        ];
        const grid = $('summaryGrid');
        grid.innerHTML = items.map((item, i) =>
            `<div class="sum-card" style="animation-delay:${i * 0.06}s">
                <div class="sum-label"><span class="sum-dot" style="background:${item.color}"></span>${item.label}</div>
                <div class="sum-img"><img src="${b64(item.img)}" alt="${item.label}"></div>
            </div>`
        ).join('');
    }

    function drawHist(id, data, color, height = 130) {
        const c = $(id); if (!c) return;
        const ctx = c.getContext('2d'), w = c.width, h = c.height;
        ctx.clearRect(0, 0, w, h);
        const max = Math.max(...data), bw = w / 256;
        const grad = ctx.createLinearGradient(0, h, 0, 0);
        grad.addColorStop(0, 'transparent'); grad.addColorStop(1, color);
        ctx.fillStyle = grad; ctx.beginPath(); ctx.moveTo(0, h);
        for (let i = 0; i < 256; i++) ctx.lineTo(i * bw, h - (data[i] / max) * (h - 8));
        ctx.lineTo(w, h); ctx.closePath(); ctx.fill();
        ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.beginPath();
        for (let i = 0; i < 256; i++) { const y = h - (data[i] / max) * (h - 8); i === 0 ? ctx.moveTo(0, y) : ctx.lineTo(i * bw, y); }
        ctx.stroke();
    }

    function animateSteps() {
        const steps = document.querySelectorAll('.ls');
        steps.forEach((s, i) => {
            s.className = 'ls';
            setTimeout(() => {
                if (i > 0) steps[i - 1].className = 'ls done';
                s.className = 'ls active';
            }, i * 500);
        });
        setTimeout(() => steps[steps.length - 1].className = 'ls done', steps.length * 500);
    }

    function toast(msg, type = 'success') {
        const t = $('toast');
        $('toastIcon').textContent = type === 'success' ? '✓' : '✕';
        $('toastMsg').textContent = msg;
        t.className = `toast ${type}`;
        setTimeout(() => t.classList.add('hidden'), 4000);
    }

    function delay(ms) { return new Promise(r => setTimeout(r, ms)); }
});

