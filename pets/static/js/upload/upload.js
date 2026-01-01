let currentFile = null;
let previewElement = null;

function updateFloating(group) {
  const input = group.querySelector('.floating-input, .floating-textarea');
  const hasValue = input && (input.value && input.value.trim().length > 0);
  group.classList.toggle('has-value', !!hasValue);
}

function initFloating() {
  document.querySelectorAll('[data-float]').forEach(group => {
    const input = group.querySelector('.floating-input, .floating-textarea');
    if (!input) return;

    updateFloating(group);

    ['input', 'change'].forEach(ev => {
      input.addEventListener(ev, () => updateFloating(group));
    });

    ['focus', 'blur'].forEach(ev => {
      input.addEventListener(ev, () => updateFloating(group));
    });

    setTimeout(() => updateFloating(group), 300);
    window.addEventListener('animationstart', (e) => {
      if (e.animationName === 'onAutoFillStart') updateFloating(group);
    }, { passive: true });
  });
}

async function handleFilePreview(file) {
  if (!file) return;

  const fd = new FormData();
  fd.append('file', file);

  try {
    // Upload to temporary storage endpoint
    const resp = await fetch('/api/upload/preview', { method: 'POST', body: fd });
    if (!resp.ok) throw new Error('Preview upload failed');

    const data = await resp.json();
    currentFile = data;

    // Display preview
    showPreview(data.url, data.type);
  } catch (err) {
    alert(err.message || 'Error previewing file');
  }
}

function showPreview(url, type) {
  const container = document.getElementById('preview-container');
  const preview = document.getElementById('file-preview');

  preview.innerHTML = '';

  if (type.startsWith('image')) {
    const img = document.createElement('img');
    img.src = url;
    img.alt = 'Preview';
    preview.appendChild(img);
  } else if (type.startsWith('video')) {
    const video = document.createElement('video');
    video.src = url;
    video.controls = true;
    preview.appendChild(video);
  }

  container.style.display = 'flex';
}

function clearPreview() {
  const container = document.getElementById('preview-container');
  const preview = document.getElementById('file-preview');
  preview.innerHTML = '';
  container.style.display = 'none';
  currentFile = null;
}

function initForm() {
  const form = document.getElementById('upload-form');
  const fileInput = document.getElementById('file');
  const resetBtn = document.getElementById('reset-btn');
  const changeBtn = document.getElementById('change-btn');

  // Auto-preview on file selection
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      await handleFilePreview(file);
    }
  });

  // Change file button
  if (changeBtn) {
    changeBtn.addEventListener('click', () => {
      fileInput.click();
    });
  }

  resetBtn.addEventListener('click', () => {
    form.reset();
    clearPreview();
    document.querySelectorAll('[data-float]').forEach(updateFloating);
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!currentFile) {
      alert('Please select a file first');
      return;
    }

    const caption = document.getElementById('caption').value.trim();
    const tagsRaw = document.getElementById('tags').value.trim();
    const tags = tagsRaw.split(',').map(s => s.trim()).filter(Boolean);

    try {
      // Submit final upload with metadata
      const resp = await fetch('/api/upload/finalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          temp_id: currentFile.temp_id,
          caption: caption,
          tags: tags.join(','),
          url: currentFile.url
        })
      });

      if (!resp.ok) throw new Error('Upload failed');

      alert('Upload successful');
      form.reset();
      clearPreview();
      document.querySelectorAll('[data-float]').forEach(updateFloating);
    } catch (err) {
      alert(err.message || 'Error');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initFloating();
  initForm();
});