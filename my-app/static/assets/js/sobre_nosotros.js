(function () {
  'use strict';

  const IMAGES = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u'
  ];

  const SKELETON_COUNT = IMAGES.length;
  const MIN_SK_HEIGHT = 180;
  const MAX_SK_HEIGHT = 320;

  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function getImgUrl(letter) {
    return '../static/img/' + letter + '.jpeg';
  }

  function createSkeletonCard(index) {
    const height = randomInt(MIN_SK_HEIGHT, MAX_SK_HEIGHT);
    const div = document.createElement('div');
    div.className = 'masonry-item skeleton';
    div.style.height = height + 'px';
    div.setAttribute('data-index', index);
    div.setAttribute('aria-hidden', 'true');
    return div;
  }

  function createImageCard(index) {
    const div = document.createElement('div');
    div.className = 'masonry-item';
    div.setAttribute('data-index', index);

    const img = document.createElement('img');
    img.src = getImgUrl(IMAGES[index]);
    img.alt = 'Galería Invilara ' + (index + 1);
    img.loading = 'lazy';
    img.className = 'masonry-img';

    function onLoad() {
      img.classList.add('loaded');
    }

    img.addEventListener('load', onLoad);
    if (img.complete) {
      onLoad();
    }

    img.onerror = function () {
      img.style.display = 'none';
    };

    div.appendChild(img);
    return div;
  }

  function initMasonry() {
    const grid = document.getElementById('masonryGrid');
    if (!grid) return;

    const fragment = document.createDocumentFragment();
    for (let i = 0; i < SKELETON_COUNT; i++) {
      fragment.appendChild(createSkeletonCard(i));
    }
    grid.appendChild(fragment);

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            const el = entry.target;
            const index = parseInt(el.getAttribute('data-index'), 10);
            if (!isNaN(index)) {
              const newCard = createImageCard(index);
              el.replaceWith(newCard);
            }
            observer.unobserve(el);
          }
        });
      },
      {
        rootMargin: '200px 0px',
        threshold: 0.01
      }
    );

    const skeletons = grid.querySelectorAll('.skeleton');
    skeletons.forEach(function (sk) {
      observer.observe(sk);
    });

    setTimeout(function () {
      skeletons.forEach(function (sk) {
        const rect = sk.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
          const index = parseInt(sk.getAttribute('data-index'), 10);
          if (!isNaN(index)) {
            const newCard = createImageCard(index);
            sk.replaceWith(newCard);
          }
          observer.unobserve(sk);
        }
      });
    }, 1000);
  }

  function initDrawer() {
    var openBtn = document.getElementById('navbarDrawerOpen');
    var closeBtn = document.getElementById('navbarDrawerClose');
    var drawer = document.getElementById('navbarDrawer');
    var backdrop = document.getElementById('navbarDrawerBackdrop');
    var drawerLinks = document.querySelectorAll('.drawer-link');

    if (!openBtn || !closeBtn || !drawer || !backdrop) return;

    function openDrawer() {
      drawer.classList.add('is-open');
      backdrop.classList.add('is-open');
      drawer.setAttribute('aria-hidden', 'false');
      backdrop.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      closeBtn.focus();
    }

    function closeDrawer() {
      drawer.classList.remove('is-open');
      backdrop.classList.remove('is-open');
      drawer.setAttribute('aria-hidden', 'true');
      backdrop.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      openBtn.focus();
    }

    openBtn.addEventListener('click', openDrawer);
    closeBtn.addEventListener('click', closeDrawer);
    backdrop.addEventListener('click', closeDrawer);

    drawerLinks.forEach(function (link) {
      link.addEventListener('click', closeDrawer);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initDrawer();
    initMasonry();
  });
})();
