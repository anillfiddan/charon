(function () {
  // Formların gönderileceği adres (Formspree, Web3Forms ya da Charon API, JSON POST). Boşsa form gönderilmez.
  var FORM_ENDPOINT = "";

  var header = document.querySelector(".site-header");
  function onScroll() { header.classList.toggle("scrolled", window.scrollY > 4); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  var toggle = document.querySelector(".menu-toggle");
  var mnav = document.getElementById("mobile-nav");
  if (toggle && mnav) {
    toggle.addEventListener("click", function () {
      var open = mnav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Menüyü kapat" : "Menüyü aç");
    });
  }

  var y = document.querySelectorAll("[data-year]");
  for (var i = 0; i < y.length; i++) y[i].textContent = new Date().getFullYear();

  // Başvuru formu: tip seçimi (?tip=startup) ve alan etiketi
  var apply = document.getElementById("apply-form");
  if (apply) {
    var params = new URLSearchParams(location.search);
    if (params.get("tip") === "startup") document.getElementById("tip-s").checked = true;
    var msgLabel = document.getElementById("mesaj-label");
    var update = function () {
      var s = document.getElementById("tip-s").checked;
      msgLabel.firstChild.nodeValue = s ? "Ürününüzü kısaca anlatın " : "Nasıl bir çözüm arıyorsunuz? ";
    };
    apply.querySelectorAll('input[name="tip"]').forEach(function (r) { r.addEventListener("change", update); });
    update();
    apply._update = update;
  }

  document.querySelectorAll("form[data-form]").forEach(function (form) {
    var msg = form.querySelector(".form-msg");
    var submit = form.querySelector('button[type="submit"]');
    var label = submit.textContent;
    function show(cls, text) { msg.className = "form-msg " + cls; msg.textContent = text; }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      form.querySelectorAll("[aria-invalid]").forEach(function (el) { el.removeAttribute("aria-invalid"); });
      if (!form.checkValidity()) {
        var bad = form.querySelectorAll(":invalid");
        bad.forEach(function (el) { if (el.type !== "checkbox") el.setAttribute("aria-invalid", "true"); });
        var first = bad[0];
        show("err", first && first.type === "checkbox" ? "Devam etmek için aydınlatma metnini okuduğunuzu onaylayın." : "Lütfen zorunlu alanları doldurun.");
        if (first) first.focus();
        return;
      }
      if (form.querySelector(".hp input").value) return;
      if (!FORM_ENDPOINT) { show("err", "Form şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin."); return; }

      var data = { form: form.getAttribute("data-form") };
      new FormData(form).forEach(function (v, k) { if (k !== "website_url") data[k] = v; });
      submit.disabled = true; submit.textContent = "Gönderiliyor…";
      fetch(FORM_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(data)
      }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        form.reset();
        if (form._update) form._update();
        show("ok", form.getAttribute("data-ok"));
      }).catch(function () {
        show("err", "Gönderilemedi. Lütfen tekrar deneyin.");
      }).finally(function () {
        submit.disabled = false; submit.textContent = label;
      });
    });
  });
})();
