(function () {
  "use strict";

  // Theme preference kept in memory / window.name (no localStorage).
  var themeState = { dark: false };
  try {
    if (window.name && window.name.indexOf("theme:dark") === 0) themeState.dark = true;
  } catch (e) {}

  function applyTheme() {
    document.documentElement.setAttribute("data-theme", themeState.dark ? "dark" : "light");
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = themeState.dark ? "浅色" : "深色";
    try {
      window.name = themeState.dark ? "theme:dark" : "theme:light";
    } catch (e) {}
  }
  applyTheme();

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      themeState.dark = !themeState.dark;
      applyTheme();
    });
  }

  // Sticky TOC active section
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  var sections = tocLinks
    .map(function (a) {
      return document.querySelector(a.getAttribute("href"));
    })
    .filter(Boolean);

  if (sections.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          tocLinks.forEach(function (a) {
            a.classList.toggle("active", a.getAttribute("href") === "#" + id);
          });
        });
      },
      { rootMargin: "-35% 0px -55% 0px", threshold: 0 }
    );
    sections.forEach(function (s) {
      io.observe(s);
    });
  }

  // System timeline track toggles
  document.querySelectorAll("[data-tracks]").forEach(function (root) {
    root.querySelectorAll("[data-track-btn]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var key = btn.getAttribute("data-track-btn");
        var track = root.querySelector('[data-track="' + key + '"]');
        if (!track) return;
        var on = track.classList.toggle("on");
        btn.classList.toggle("active", on);
      });
    });
  });

  // Annotation toggle for crops
  document.querySelectorAll("[data-crop]").forEach(function (root) {
    var img = root.querySelector("img");
    var btn = root.querySelector("[data-annot-toggle]");
    if (!img || !btn) return;
    var annotated = img.getAttribute("data-annotated");
    var clean = img.getAttribute("data-clean");
    var showAnnot = true;
    btn.addEventListener("click", function () {
      showAnnot = !showAnnot;
      img.src = showAnnot ? annotated : clean;
      btn.textContent = showAnnot ? "隐藏标注" : "显示标注";
      btn.classList.toggle("active", showAnnot);
    });
  });

  // Perspective grid overlay
  document.querySelectorAll("[data-grid]").forEach(function (root) {
    var btn = root.querySelector("[data-grid-toggle]");
    var stage = root.querySelector(".grid-stage");
    if (!btn || !stage) return;
    btn.addEventListener("click", function () {
      var on = stage.classList.toggle("show-grid");
      btn.classList.toggle("active", on);
      btn.textContent = on ? "隐藏透视网格" : "显示透视网格";
    });
  });

  // Chiaroscuro / temperature channels
  document.querySelectorAll("[data-temp]").forEach(function (root) {
    var stage = root.querySelector(".temp-stage");
    root.querySelectorAll("[data-temp-mode]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var mode = btn.getAttribute("data-temp-mode");
        stage.setAttribute("data-mode", mode);
        root.querySelectorAll("[data-temp-mode]").forEach(function (b) {
          b.classList.toggle("active", b === btn);
        });
      });
    });
  });

  // Compare slider
  document.querySelectorAll("[data-compare]").forEach(function (root) {
    var after = root.querySelector(".compare-after");
    var range = root.querySelector("input[type=range]");
    if (!after || !range) return;
    function update() {
      var pct = 100 - Number(range.value);
      after.style.clipPath = "inset(0 " + pct + "% 0 0)";
    }
    range.addEventListener("input", update);
    update();
  });

  // Layer stack
  document.querySelectorAll("[data-layers]").forEach(function (root) {
    root.querySelectorAll("input[type=checkbox][data-layer]").forEach(function (cb) {
      cb.addEventListener("change", function () {
        var img = root.querySelector('img[data-layer-img="' + cb.getAttribute("data-layer") + '"]');
        if (img) img.style.opacity = cb.checked ? "1" : "0";
      });
    });
  });

  // Pigment timeline
  document.querySelectorAll("[data-timeline=pigments]").forEach(function (root) {
    var yearEl = root.querySelector(".pigment-year");
    var range = root.querySelector("input[type=range]");
    var swatches = Array.prototype.slice.call(root.querySelectorAll(".pigment-swatch"));
    function update() {
      var y = Number(range.value);
      yearEl.textContent = String(y);
      swatches.forEach(function (s) {
        var intro = Number(s.getAttribute("data-year"));
        s.classList.toggle("on", intro <= y);
      });
    }
    range.addEventListener("input", update);
    update();
  });

  // Loupe / magnifier on plates
  var modal = document.getElementById("loupe-modal");
  var zoom = modal ? modal.querySelector(".loupe-zoom") : null;

  function openLoupe(src, xRatio, yRatio) {
    if (!modal || !zoom) return;
    zoom.style.backgroundImage = "url('" + src + "')";
    zoom.style.backgroundPosition = xRatio * 100 + "% " + yRatio * 100 + "%";
    modal.hidden = false;
  }
  function closeLoupe() {
    if (modal) modal.hidden = true;
  }

  if (modal) {
    modal.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", closeLoupe);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLoupe();
    });
  }

  document.querySelectorAll("[data-loupe] img").forEach(function (img) {
    img.addEventListener("click", function (e) {
      var rect = img.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width;
      var y = (e.clientY - rect.top) / rect.height;
      var src = img.getAttribute("data-hires") || img.src;
      openLoupe(src, Math.min(Math.max(x, 0), 1), Math.min(Math.max(y, 0), 1));
    });
  });
})();
