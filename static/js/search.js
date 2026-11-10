/* サイト内検索（クライアントサイド / elasticlunr）
   検索用ドキュメントは Zola テンプレート（templates/search-index.json）で生成し、
   初回入力時に取得してブラウザ側で索引化する。日本語は文字バイグラムで分割する。 */
(function () {
  var form = document.querySelector(".site-search");
  var input = document.querySelector(".site-search-input");
  var resultsBox = document.querySelector(".search-results");
  if (!form || !input || !resultsBox || typeof elasticlunr === "undefined") return;

  var SECTION_NAMES = {
    std: "標準ライブラリ",
    crates: "クレート",
    errors: "エラー解決",
    tools: "ツール",
    web: "Webの基礎",
    books: "レビュー",
    "": ""
  };
  var MAX_RESULTS = 8;

  /* 日本語トークナイザ: 英数字の並びはそのまま1語として、CJK の並びは文字バイグラムに分割する */
  function tokenize(text) {
    var tokens = [];
    var s = text == null ? "" : String(text).toLowerCase();
    var runs = s.match(/[a-z0-9_+#.\-]+|[^\x00-\x7f]+/g) || [];
    runs.forEach(function (run) {
      if (/^[a-z0-9_+#.\-]+$/.test(run)) {
        tokens.push(run);
      } else if (run.length === 1) {
        tokens.push(run);
      } else {
        for (var i = 0; i + 1 < run.length; i++) {
          tokens.push(run.slice(i, i + 2));
        }
      }
    });
    return tokens;
  }
  elasticlunr.tokenizer = tokenize;

  var docs = null;
  var index = null;
  var loadPromise = null;

  function ensureIndex() {
    if (index) return Promise.resolve();
    if (loadPromise) return loadPromise;
    var url = form.getAttribute("data-index-url");
    loadPromise = fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        docs = data;
        index = elasticlunr(function () {
          this.addField("title");
          this.addField("description");
          this.addField("body");
          this.setRef("url");
          /* 英語前提の trimmer / stemmer / ストップワードは日本語トークンを壊すため外す */
          this.pipeline.remove(elasticlunr.trimmer);
          this.pipeline.remove(elasticlunr.stemmer);
          this.pipeline.remove(elasticlunr.stopWordFilter);
        });
        docs.forEach(function (doc) { index.addDoc(doc); });
      })
      .catch(function () { loadPromise = null; });
    return loadPromise;
  }

  var activeIndex = -1;

  function hideResults() {
    resultsBox.hidden = true;
    resultsBox.innerHTML = "";
    activeIndex = -1;
    input.removeAttribute("aria-activedescendant");
    input.setAttribute("aria-expanded", "false");
  }

  function showResults() {
    resultsBox.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function renderResults(query) {
    var refs = index.search(query, {
      fields: {
        title: { boost: 10 },
        description: { boost: 3 },
        body: { boost: 1 }
      },
      expand: false
    });
    resultsBox.innerHTML = "";
    activeIndex = -1;
    if (!refs.length) {
      var empty = document.createElement("p");
      empty.className = "search-empty";
      empty.textContent = "「" + query + "」に一致する記事はありません";
      resultsBox.appendChild(empty);
      showResults();
      return;
    }
    refs.slice(0, MAX_RESULTS).forEach(function (ref, i) {
      var doc = index.documentStore.getDoc(ref.ref);
      var link = document.createElement("a");
      link.className = "search-result";
      link.href = ref.ref;
      link.id = "search-result-" + i;
      var title = document.createElement("span");
      title.className = "search-result-title";
      title.textContent = doc.title;
      link.appendChild(title);
      var sectionName = SECTION_NAMES[doc.section] || "";
      if (sectionName) {
        var section = document.createElement("span");
        section.className = "search-result-section";
        section.textContent = sectionName;
        link.appendChild(section);
      }
      link.addEventListener("mouseenter", function () { setActive(i); });
      resultsBox.appendChild(link);
    });
    showResults();
  }

  function setActive(i) {
    var items = resultsBox.querySelectorAll(".search-result");
    if (!items.length) return;
    activeIndex = (i + items.length) % items.length;
    items.forEach(function (item, j) {
      item.classList.toggle("is-active", j === activeIndex);
    });
    input.setAttribute("aria-activedescendant", "search-result-" + activeIndex);
  }

  var debounce = null;
  input.addEventListener("input", function () {
    var query = input.value.trim();
    if (!query) {
      hideResults();
      return;
    }
    window.clearTimeout(debounce);
    debounce = window.setTimeout(function () {
      ensureIndex().then(function () {
        if (input.value.trim() === query) renderResults(query);
      });
    }, 120);
  });
  input.addEventListener("focus", function () {
    var query = input.value.trim();
    if (!query) return;
    ensureIndex().then(function () {
      if (input.value.trim() === query) renderResults(query);
    });
  });

  input.addEventListener("keydown", function (event) {
    if (resultsBox.hidden) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive(activeIndex + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive(activeIndex - 1);
    } else if (event.key === "Enter" && activeIndex >= 0) {
      var items = resultsBox.querySelectorAll(".search-result");
      if (items[activeIndex]) {
        event.preventDefault();
        window.location.href = items[activeIndex].href;
      }
    } else if (event.key === "Escape") {
      hideResults();
    }
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var first = resultsBox.querySelector(".search-result");
    if (first) window.location.href = first.href;
  });

  document.addEventListener("click", function (event) {
    if (!resultsBox.hidden && !form.contains(event.target)) hideResults();
  });
})();
