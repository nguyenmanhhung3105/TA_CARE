/** Native form enhancements only. Authorization and validation live on the server. */
function initRecruitmentProfile() {
  const create = document.querySelector('[data-profile-create]');
  if (create) {
    const group = create.querySelector('[data-recruitment-start]');
    const sector = create.querySelector('[data-create-sector]');
    const position = create.querySelector('[data-create-position]');
    const filter = () => {
      for (const option of position.options) {
        const hidden = Boolean(option.value && (!sector.value || option.dataset.sector !== sector.value));
        option.hidden = hidden; option.disabled = hidden;
      }
      if (position.selectedOptions[0]?.disabled) position.value = '';
    };
    const purpose = () => {
      const recruitment = create.querySelector('[name=kind]:checked')?.value === 'recruitment';
      group.hidden = !recruitment;
      group.disabled = !recruitment;
      filter();
    };
    create.querySelectorAll('[name=kind]').forEach(n => n.addEventListener('change',purpose));
    sector.addEventListener('change', filter); purpose();
  }
  document.querySelectorAll('[data-profile-timeline]').forEach(form => {
    const current = form.querySelector('[data-timeline-current]');
    const end = form.querySelector('[data-timeline-end]');
    const update = () => { end.disabled = current.checked; };
    current.addEventListener('change',update);update();
  });
  document.getElementById('profile-editor-error')?.focus({preventScroll:false});
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initRecruitmentProfile,{once:true});
else initRecruitmentProfile();
