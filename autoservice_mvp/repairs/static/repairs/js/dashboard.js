document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('filter-form');
  const resetBtn = document.getElementById('reset-filters');
  const container = document.getElementById('requests-container');

  form.addEventListener('change', () => {
    const formData = new FormData(form);
    const params = new URLSearchParams(formData).toString();

    fetch(`/repairs/filter-requests/?${params}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(res => res.text())
      .then(html => {
        container.innerHTML = html;
      });
  });

  resetBtn.addEventListener('click', () => {
    form.reset();
    form.dispatchEvent(new Event('change'));
  });
});
