/** Kho việc làm form interactions; server routes remain the source of truth. */
function initKvlForm() {
  const form = document.querySelector('form[data-kvl-unsaved]');
  if (!form) return;
  const list = form.querySelector('[data-kvl-requirements]');
  let dirty = false;
  let submitting = false;
  form.addEventListener('input', () => { dirty = true; });
  form.addEventListener('change', () => { dirty = true; });
  form.addEventListener('submit', () => {
    submitting = true;
    form.querySelectorAll('button[type="submit"]').forEach((button) => {
      if (button === document.activeElement) button.textContent = 'Đang lưu…';
    });
  });
  window.addEventListener('beforeunload', (event) => {
    if (dirty && !submitting) {
      event.preventDefault();
      event.returnValue = '';
    }
  });
  form.querySelector('[data-kvl-add]')?.addEventListener('click', () => {
    const original = list.querySelector('.tc-kvl-requirement');
    if (!original) return;
    const row = original.cloneNode(true);
    row.querySelectorAll('input').forEach((input) => { input.value = ''; });
    row.querySelector('[name="requirement_category"]').value = 'technical';
    row.querySelector('[name="requirement_priority"]').value = 'mandatory';
    list.append(row);
    row.querySelector('input')?.focus();
    dirty = true;
  });
  list?.addEventListener('click', (event) => {
    if (!event.target.closest('[data-kvl-remove]')) return;
    const row = event.target.closest('.tc-kvl-requirement');
    if (list.querySelectorAll('.tc-kvl-requirement').length > 1) row.remove();
    else row.querySelector('[name="requirement_name"]').value = '';
    dirty = true;
  });
  const sector = form.querySelector('[name="sector_id"]');
  const updateSectorFields = (clearHidden = false) => {
    const code = sector?.selectedOptions[0]?.dataset.code || '';
    form.querySelectorAll('[data-kvl-sector]').forEach((field) => {
      const standard = ['sales', 'marketing', 'health', 'ecommerce'].includes(code);
      const visible = !standard || field.dataset.kvlSector.split(',').includes(code);
      field.hidden = !visible;
      if (!visible && clearHidden) field.querySelector('input').checked = false;
    });
  };
  sector?.addEventListener('change', () => updateSectorFields(true));
  updateSectorFields();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initKvlForm, { once: true });
} else {
  initKvlForm();
}
