const dialog = document.querySelector('.drawing-dialog');

if (dialog && typeof dialog.showModal === 'function') {
  const dialogImage = dialog.querySelector('.dialog-image');
  const dialogVideo = dialog.querySelector('.dialog-video');
  const dialogTitle = dialog.querySelector('#drawing-title');

  document.querySelectorAll('[data-lightbox]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const sourceImage = link.querySelector('img');
      const sourceVideo = link.querySelector('video');
      const scale = link.dataset.dialogScale || '1';
      if (sourceVideo && dialogVideo) {
        dialogImage.hidden = true;
        dialogImage.removeAttribute('src');
        dialogVideo.hidden = false;
        dialogVideo.src = link.href;
        dialogVideo.setAttribute('aria-label', sourceVideo.getAttribute('aria-label') || '');
        dialogVideo.style.setProperty('--dialog-scale', scale);
      } else {
        if (dialogVideo) {
          dialogVideo.pause();
          dialogVideo.hidden = true;
          dialogVideo.removeAttribute('src');
          dialogVideo.load();
        }
        dialogImage.hidden = false;
        dialogImage.src = link.href;
        dialogImage.alt = sourceImage?.alt || '';
        dialogImage.style.setProperty('--dialog-scale', scale);
      }
      dialogTitle.textContent = link.dataset.title || 'A closer look';
      dialog.showModal();
      if (sourceVideo && dialogVideo) dialogVideo.play().catch(() => {});
    });
  });

  dialog.querySelector('.close-dialog')?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    const bounds = dialog.getBoundingClientRect();
    const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
    if (event.target === dialog && outside) dialog.close();
  });
  dialog.addEventListener('close', () => {
    if (!dialogVideo) return;
    dialogVideo.pause();
    dialogVideo.removeAttribute('src');
    dialogVideo.load();
  });
}

// Annotation points use normalized coordinates over the complete source image:
// [0, 0] is top-left and [1, 1] is bottom-right.
document.querySelectorAll('.annotated-view').forEach((view) => {
  const image = view.querySelector('.annotated-image');
  const svg = view.querySelector('.annotation-lines');
  const notes = [...view.querySelectorAll('.view-note')];
  if (!image || !svg) return;

  const namespace = 'http://www.w3.org/2000/svg';
  let frame;

  const draw = () => {
    const bounds = view.getBoundingClientRect();
    const picture = image.getBoundingClientRect();
    if (!picture.width || !picture.height || !bounds.width) return;
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    svg.replaceChildren();

    const stacked = getComputedStyle(view).getPropertyValue('--stacked').trim() === '1';
    const notesOnRight = view.classList.contains('notes--right');

    notes.forEach((note) => {
      let point;
      try { point = JSON.parse(note.dataset.point); } catch { return; }
      const valid = Array.isArray(point) && point.length === 2 && point.every((number) => Number.isFinite(number) && number >= 0 && number <= 1);
      if (!valid) return;

      const headingElement = note.querySelector('h3');
      if (!headingElement) return;
      const heading = headingElement.getBoundingClientRect();
      const x = picture.left - bounds.left + point[0] * picture.width;
      const y = picture.top - bounds.top + point[1] * picture.height;
      const path = document.createElementNS(namespace, 'path');
      if (stacked) {
        const group = note.parentElement;
        const onTop = group.classList.contains('view-notes--top');
        const noteBounds = note.getBoundingClientRect();
        const row = [...group.children].filter(sibling => {
          const siblingBounds = sibling.getBoundingClientRect();
          return Math.abs((onTop ? siblingBounds.bottom : siblingBounds.top) -
            (onTop ? noteBounds.bottom : noteBounds.top)) < 1;
        });
        const groupNotes = [...group.children];
        const nearestRow = onTop
          ? Math.max(...groupNotes.map(sibling => sibling.getBoundingClientRect().bottom))
          : Math.min(...groupNotes.map(sibling => sibling.getBoundingClientRect().top));
        const rowEdge = onTop ? noteBounds.bottom : noteBounds.top;
        const laterRow = Math.abs(rowEdge - nearestRow) > 1;
        const elbowY = (onTop ? picture.top - 18 : picture.bottom + 18) - bounds.top;
        // Staggered notes share a grid row. Route their leaders across the row's
        // empty gutter before heading toward the image, never through copy.
        const contentBottom = Math.max(heading.bottom, note.querySelector('p')?.getBoundingClientRect().bottom || 0);
        const startX = heading.left - bounds.left + heading.width / 2;
        const startY = (onTop ? contentBottom + 10 : heading.top - 10) - bounds.top;
        const railY = (onTop
          ? Math.max(...row.map(sibling => sibling.getBoundingClientRect().bottom)) + 12
          : Math.min(...row.map(sibling => sibling.getBoundingClientRect().top)) - 12) - bounds.top;
        if (laterRow) {
          const left = noteBounds.left + noteBounds.width / 2 < bounds.left + bounds.width / 2;
          const gutter = left ? -12 : bounds.width + 12;
          path.setAttribute('d', `M ${startX} ${startY} L ${startX} ${railY} L ${gutter} ${railY} L ${gutter} ${elbowY} L ${x} ${y}`);
        } else {
          path.setAttribute('d', `M ${startX} ${startY} L ${startX} ${elbowY} L ${x} ${y}`);
        }
      } else {
        const startX = notesOnRight ? heading.left - bounds.left - 8 : heading.right - bounds.left + 8;
        const startY = heading.bottom - bounds.top - 3;
        const elbowX = notesOnRight ? picture.right - bounds.left + 18 : picture.left - bounds.left - 18;
        path.setAttribute('d', `M ${startX} ${startY} L ${elbowX} ${startY} L ${x} ${y}`);
      }
      const dot = document.createElementNS(namespace, 'circle');
      dot.setAttribute('cx', x);
      dot.setAttribute('cy', y);
      dot.setAttribute('r', '3');
      svg.append(path, dot);
    });
  };

  const schedule = () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(draw);
  };

  const observer = new ResizeObserver(schedule);
  observer.observe(view);
  observer.observe(image);
  notes.forEach((note) => observer.observe(note));
  image.addEventListener('load', schedule);
  image.addEventListener('loadedmetadata', schedule);
  document.fonts.ready.then(schedule);
  schedule();
});
