function showAlert(type, msg) {
  const box = document.getElementById('alert-box');
  box.className = 'alert ' + type;
  box.textContent = msg;
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert() {
  const box = document.getElementById('alert-box');
  box.className = 'alert';
  box.textContent = '';
}

// Привязка кликов на file-area к input
document.getElementById('img-drop').addEventListener('click', () => {
  document.getElementById('img-input').click();
});
document.getElementById('nb-drop').addEventListener('click', () => {
  document.getElementById('nb-input').click();
});

// Показ выбранных изображений
document.getElementById('img-input').addEventListener('change', function () {
  const drop = document.getElementById('img-drop');
  if (this.files.length) {
    drop.textContent = '✅ ' + [...this.files].map(f => f.name).join(', ');
    drop.classList.add('selected');
  } else {
    drop.textContent = '📎 Нажми чтобы выбрать изображения';
    drop.classList.remove('selected');
  }
});

// Показ выбранного notebook
document.getElementById('nb-input').addEventListener('change', function () {
  const drop = document.getElementById('nb-drop');
  if (this.files.length) {
    drop.textContent = '✅ ' + this.files[0].name;
    drop.classList.add('selected');
  } else {
    drop.textContent = '📓 Нажми чтобы выбрать .ipynb файл';
    drop.classList.remove('selected');
  }
});

// Markdown → PDF
document.getElementById('md-btn').addEventListener('click', async () => {
  const mdText = document.getElementById('md-input').value;
  if (!mdText.trim()) { showAlert('error', 'Пффф... Введи текст!'); return; }

  hideAlert();
  const btn = document.getElementById('md-btn');
  btn.disabled = true;
  btn.textContent = 'Генерируем...';

  try {
    const formData = new FormData();
    formData.append('markdown_text', mdText);
    [...document.getElementById('img-input').files].forEach(f => formData.append('images', f));

    const response = await fetch('/generate', { method: 'POST', body: formData });
    if (!response.ok) {
      const data = await response.json();
      showAlert('error', data.error || 'Ошибка');
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'report.pdf'; a.click();
    URL.revokeObjectURL(url);
    showAlert('success', 'PDF скачан!');
  } catch (err) {
    showAlert('error', 'Ошибка: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Сгенерировать PDF';
  }
});

// Notebook → PDF
document.getElementById('nb-btn').addEventListener('click', async () => {
  const nbFile = document.getElementById('nb-input').files[0];
  if (!nbFile) { showAlert('error', 'Выбери .ipynb файл!'); return; }

  hideAlert();
  const btn = document.getElementById('nb-btn');
  btn.disabled = true;
  btn.textContent = 'Конвертируем...';

  try {
    const formData = new FormData();
    formData.append('notebook', nbFile);

    const response = await fetch('/generate-notebook', { method: 'POST', body: formData });
    if (!response.ok) {
      const data = await response.json();
      showAlert('error', data.error || 'Ошибка');
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'notebook.pdf'; a.click();
    URL.revokeObjectURL(url);
    showAlert('success', 'Notebook сконвертирован и скачан!');
  } catch (err) {
    showAlert('error', 'Ошибка: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Конвертировать в PDF';
  }
});

// Привязка кликов для pandoc
document.getElementById('pandoc-drop').addEventListener('click', () => {
  document.getElementById('pandoc-input').click();
});
document.getElementById('pandoc-imgs-drop').addEventListener('click', () => {
  document.getElementById('pandoc-imgs').click();
});

document.getElementById('pandoc-input').addEventListener('change', function () {
  const drop = document.getElementById('pandoc-drop');
  if (this.files.length) {
    drop.textContent = '✅ ' + this.files[0].name;
    drop.classList.add('selected');
  } else {
    drop.textContent = '📄 Нажми чтобы выбрать .md файл';
    drop.classList.remove('selected');
  }
});

document.getElementById('pandoc-imgs').addEventListener('change', function () {
  const drop = document.getElementById('pandoc-imgs-drop');
  if (this.files.length) {
    drop.textContent = '✅ ' + [...this.files].map(f => f.name).join(', ');
    drop.classList.add('selected');
  } else {
    drop.textContent = '🖼️ Нажми чтобы выбрать картинки (папка image/)';
    drop.classList.remove('selected');
  }
});

document.getElementById('pandoc-btn').addEventListener('click', async () => {
  const file = document.getElementById('pandoc-input').files[0];
  if (!file) { showAlert('error', 'Выбери .md файл!'); return; }

  hideAlert();
  const btn = document.getElementById('pandoc-btn');
  const btnText = document.getElementById('pandoc-btn-text');
  btn.disabled = true;
  btnText.textContent = 'Компилируем...';

  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('output_format', document.getElementById('pandoc-format').value);
    formData.append('doc_type', document.getElementById('pandoc-type').value);
    [...document.getElementById('pandoc-imgs').files].forEach(f => formData.append('images', f));

    const response = await fetch('/generate-pandoc', { method: 'POST', body: formData });
    if (!response.ok) {
      const data = await response.json();
      showAlert('error', data.error);
      return;
    }

    const format = document.getElementById('pandoc-format').value;
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.' + format;
    a.click();
    URL.revokeObjectURL(url);
    showAlert('success', 'Файл скомпилирован и скачан!');
  } catch (err) {
    showAlert('error', 'Ошибка: ' + err.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = '📄 Скомпилировать';
  }
});
