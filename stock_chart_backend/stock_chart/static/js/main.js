class WatchlistManager {
  constructor() {
    this.watchlistContainer = document.getElementById("watchlist-items");
    this.addSymbolForm = document.getElementById("add-symbol-form");
    this.symbolInput = document.getElementById("symbol-input");
    this.importBtn = document.getElementById("import-symbols-btn");
    this.importModal = document.getElementById("import-modal");
    this.closeBtn = document.querySelector(".close");
    this.importForm = document.getElementById("import-symbols-form");

    this.initializeEventListeners();
    this.startWatchlistUpdates();
  }

  initializeEventListeners() {
    // Add symbol form
    this.addSymbolForm.addEventListener("submit", (e) =>
      this.handleAddSymbol(e)
    );

    // Import functionality
    this.importBtn.addEventListener(
      "click",
      () => (this.importModal.style.display = "block")
    );
    this.closeBtn.addEventListener(
      "click",
      () => (this.importModal.style.display = "none")
    );
    this.importForm.addEventListener("submit", (e) =>
      this.handleImportSymbols(e)
    );

    // Close modal on outside click
    window.addEventListener("click", (e) => {
      if (e.target === this.importModal) {
        this.importModal.style.display = "none";
      }
    });
  }

  async clearWatchlist() {
    try {
      const formData = new FormData();
      formData.append("action", "clear");

      const response = await fetch("/manage_watchlist/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      await this.updateWatchlist();
    } catch (error) {
      console.error("Error clearing watchlist:", error);
      this.showError("Failed to clear watchlist");
    }
  }

  async handleAddSymbol(e) {
    e.preventDefault();
    const symbol = this.symbolInput.value.trim().toUpperCase();
    if (!symbol) return;

    try {
      const formData = new FormData();
      formData.append("action", "add");
      formData.append("ticker", symbol);

      const response = await fetch("/manage_watchlist/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const result = await response.json();
      if (result.errors) {
        this.showError(result.errors.join("\n"));
      }

      this.symbolInput.value = "";
      await this.updateWatchlist();
    } catch (error) {
      console.error("Error adding symbol:", error);
      this.showError(`Error adding symbol: ${error.message}`);
    }
  }

  async handleDeleteSymbol(symbol) {
    if (
      !confirm(`Are you sure you want to remove ${symbol} from your watchlist?`)
    ) {
      return;
    }

    try {
      const formData = new FormData();
      formData.append("action", "delete");
      formData.append("ticker", symbol);

      const response = await fetch("/manage_watchlist/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      await this.updateWatchlist();
    } catch (error) {
      console.error("Error deleting symbol:", error);
      this.showError(`Error deleting symbol: ${error.message}`);
    }
  }

  async handleImportSymbols(e) {
    e.preventDefault();
    const symbolsInput = document.getElementById("symbols-input");
    const symbols = symbolsInput.value
      .split(/[\n,]+/)
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s);

    try {
      const formData = new FormData();
      formData.append("action", "add");
      formData.append("ticker", symbols.join(","));

      const response = await fetch("/manage_watchlist/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const result = await response.json();
      if (result.errors) {
        this.showError(result.errors.join("\n"));
      }

      this.importModal.style.display = "none";
      symbolsInput.value = "";
      await this.updateWatchlist();
    } catch (error) {
      console.error("Error importing symbols:", error);
      this.showError(`Error importing symbols: ${error.message}`);
    }
  }

  showError(message) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "error";
    errorDiv.textContent = message;
    this.watchlistContainer.prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
  }

  async updateWatchlist() {
    try {
      const response = await fetch("/update_watchlist_data/");
      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();

      this.watchlistContainer.innerHTML = `
                <table class="watchlist-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Last</th>
                            <th>Change %</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            `;

      const tbody = this.watchlistContainer.querySelector("tbody");

      data.watchlist.forEach((item) => {
        const row = document.createElement("tr");
        row.className = "watchlist-item";

        if (item.error) {
          row.innerHTML = `
                        <td>${item.symbol}</td>
                        <td colspan="2" class="error">${item.error}</td>
                        <td>
                            <button class="delete-btn" title="Remove from watchlist">×</button>
                        </td>
                    `;
        } else {
          const changeClass =
            item.change_percent >= 0 ? "positive" : "negative";
          row.innerHTML = `
                        <td>${item.symbol}</td>
                        <td>${item.last_price.toFixed(2)}</td>
                        <td class="${changeClass}">${item.change_percent.toFixed(
            2
          )}%</td>
                        <td>
                            <button class="delete-btn" title="Remove from watchlist">×</button>
                        </td>
                    `;
        }

        const deleteBtn = row.querySelector(".delete-btn");
        deleteBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          await this.handleDeleteSymbol(item.symbol);
        });

        row.addEventListener("click", () => {
          if (!item.error) {
            window.location.href = `/display_ticker/${item.symbol}/`;
          }
        });

        tbody.appendChild(row);
      });
    } catch (error) {
      console.error("Error updating watchlist:", error);
      this.watchlistContainer.innerHTML = `<p class="error">Error updating watchlist: ${error.message}</p>`;
    }
  }

  startWatchlistUpdates() {
    // Initial update
    this.updateWatchlist();

    // Update every 10 seconds
    setInterval(() => this.updateWatchlist(), 10000);
  }
}

// Initialize watchlist when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const watchlistManager = new WatchlistManager();

  // Add a button to clear the watchlist
  const clearButton = document.createElement("button");
  clearButton.textContent = "Clear Watchlist";
  clearButton.className = "btn btn-danger";
  clearButton.addEventListener("click", () =>
    watchlistManager.clearWatchlist()
  );
  document.querySelector("#symbol-form").appendChild(clearButton);
});
