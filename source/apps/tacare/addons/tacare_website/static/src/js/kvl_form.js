/** Progressive enhancement only; the server validates every write. */
function initCareForms() {
  document.querySelectorAll('form[data-kvl-unsaved]').forEach((form) => {
    let dirty = false;
    let submitting = false;
    form.addEventListener('input', () => { dirty = true; });
    form.addEventListener('change', () => { dirty = true; });
    form.addEventListener('submit', () => { submitting = true; });
    window.addEventListener('beforeunload', (event) => {
      if (dirty && !submitting) { event.preventDefault(); event.returnValue = ''; }
    });
    const sector = form.querySelector('[name="sector_id"], [name="sector"]');
    const position = form.querySelector('[data-position-select]');
    const updatePositions = () => {
      if (!position || !sector) return;
      [...position.options].forEach((option) => {
        const visible = !option.value || !sector.value || option.dataset.sector === sector.value;
        option.hidden = !visible;
        option.disabled = !visible;
      });
      if (position.selectedOptions[0]?.disabled) position.value = '';
    };
    const experience = form.querySelector('[name="experience_known"]');
    const confirmedPosition = form.querySelector('[name="experience_position_id"]');
    const resetExperience = () => {
      if (experience && confirmedPosition) { experience.checked = false; confirmedPosition.value = ''; }
    };
    position?.addEventListener('change', resetExperience);
    sector?.addEventListener('change', resetExperience);
    experience?.addEventListener('change', () => {
      if (confirmedPosition) confirmedPosition.value = experience.checked ? position?.value || '' : '';
    });
    sector?.addEventListener('change', updatePositions);
    updatePositions();
    const input = form.querySelector('[data-skill-input]');
    const picker = form.querySelector('[data-skill-picker]');
    const mandatory = new Set([...form.querySelectorAll('[name="mandatory_skill"]:checked')]
      .map((box) => box.value.toLocaleLowerCase('vi')));
    picker?.addEventListener('change', (event) => {
      if (event.target.name !== 'mandatory_skill') return;
      const key = event.target.value.toLocaleLowerCase('vi');
      if (event.target.checked) mandatory.add(key); else mandatory.delete(key);
    });
    const updateSkills = () => {
      if (!input || !picker) return;
      picker.replaceChildren();
      const seen = new Set();
      input.value.split(',').map((value) => value.trim()).filter(Boolean).forEach((name) => {
        const key = name.toLocaleLowerCase('vi');
        if (seen.has(key)) return;
        seen.add(key);
        const label = document.createElement('label'); label.className = 'tc-skill-choice';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox'; checkbox.name = 'mandatory_skill'; checkbox.value = name;
        checkbox.checked = mandatory.has(key);
        const text = document.createElement('span'); text.textContent = name;
        label.append(checkbox, text); picker.append(label);
      });
    };
    input?.addEventListener('input', updateSkills);
    updateSkills();
    const display = form.querySelector('[name="salary_display"]');
    const salaryDetails = form.querySelector('[data-salary-details]');
    const updateSalary = () => {
      if (!display || !salaryDetails) return;
      salaryDetails.hidden = display.value === 'negotiable' || !display.value;
      const min = salaryDetails.querySelector('[name="salary_min"]');
      const max = salaryDetails.querySelector('[name="salary_max"]');
      if (min) min.closest('label').hidden = display.value === 'to';
      if (max) max.closest('label').hidden = display.value === 'from';
    };
    display?.addEventListener('change', updateSalary);
    updateSalary();
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCareForms, { once: true });
else initCareForms();
