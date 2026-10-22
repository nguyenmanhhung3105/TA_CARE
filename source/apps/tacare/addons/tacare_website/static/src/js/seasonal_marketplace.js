/** Estimate only: no booking, geolocation, payment or network request. */
(() => {
  function init() {
    document.querySelectorAll('[data-seasonal-quote]').forEach(form => {
      const output = form.querySelector('[data-quote-output]');
      function update() {
        const values = Object.fromEntries(['rate','hours','materials','travel'].map(k => [k, Number(form.elements[k].value)]));
        if (!form.checkValidity() || Object.values(values).some(v => !Number.isFinite(v) || v < 0)) {
          output.textContent = 'Kiểm tra đơn giá, số giờ và các khoản chi phí.';
          return;
        }
        const total = values.rate * values.hours + values.materials + values.travel;
        output.textContent = 'Tổng dự kiến: ' + Math.round(total).toLocaleString('vi-VN') + 'đ';
      }
      form.addEventListener('input', update);
      form.addEventListener('submit', event => { event.preventDefault(); update(); });
      update();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
