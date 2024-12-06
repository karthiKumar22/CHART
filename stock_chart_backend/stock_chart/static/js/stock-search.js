export function initStockSearch() {
  const searchInput = document.getElementById("stock-search");
  const searchResults = document.getElementById("search-results");
  let debounceTimer;
  const searchCache = new Map();

  searchInput.addEventListener("input", function (e) {
    const query = e.target.value.trim().toUpperCase();

    clearTimeout(debounceTimer);
    if (query.length < 2) {
      searchResults.innerHTML = "";
      searchResults.style.display = "none";
      return;
    }

    if (searchCache.has(query)) {
      displayResults(searchCache.get(query));
      return;
    }

    debounceTimer = setTimeout(() => {
      fetchStockResults(query);
    }, 300);
  });

  async function fetchStockResults(query) {
    try {
      const response = await fetch(
        `/search_stocks/?q=${encodeURIComponent(query)}`
      );
      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();
      searchCache.set(query, data);
      displayResults(data.stocks);
    } catch (error) {
      console.error("Error fetching stock results:", error);
      searchResults.innerHTML =
        '<div class="search-error">Error fetching results</div>';
      searchResults.style.display = "block";
    }
  }

  function displayResults(results) {
    if (!results.length) {
      searchResults.innerHTML =
        '<div class="no-results">No results found</div>';
      searchResults.style.display = "block";
      return;
    }

    const html = results
      .map(
        (stock) => `
          <div class="search-result" data-symbol="${stock.symbol}">
            ${stock.symbol} - ${stock.name}
          </div>
        `
      )
      .join("");

    searchResults.innerHTML = html;
    searchResults.style.display = "block";

    // Add click handlers for search results
    document.querySelectorAll(".search-result").forEach((result) => {
      result.addEventListener("click", function () {
        const symbol = this.dataset.symbol;
        window.location.href = `/display_ticker/${symbol}/`;
        searchInput.value = "";
        searchResults.style.display = "none";
      });
    });
  }

  // Close search results when clicking outside
  document.addEventListener("click", function (e) {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = "none";
    }
  });

  // Handle keyboard navigation
  searchInput.addEventListener("keydown", function (e) {
    const results = searchResults.querySelectorAll(".search-result");
    const current = searchResults.querySelector(".search-result.selected");

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        if (!current) {
          results[0]?.classList.add("selected");
        } else {
          const next = current.nextElementSibling;
          if (next) {
            current.classList.remove("selected");
            next.classList.add("selected");
          }
        }
        break;

      case "ArrowUp":
        e.preventDefault();
        if (current) {
          const prev = current.previousElementSibling;
          if (prev) {
            current.classList.remove("selected");
            prev.classList.add("selected");
          }
        }
        break;

      case "Enter":
        if (current) {
          const symbol = current.dataset.symbol;
          window.location.href = `/display_ticker/${symbol}/`;
        }
        break;
    }
  });
}
