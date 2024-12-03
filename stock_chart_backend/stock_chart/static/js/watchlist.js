// static/js/watchlist.js
document.addEventListener('DOMContentLoaded', function() {
    const watchlistContainer = document.getElementById('watchlist-items');
    const addSymbolForm = document.getElementById('add-symbol-form');
    const symbolInput = document.getElementById('symbol-input');

    function formatNumber(number) {
        return new Intl.NumberFormat('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(number);
    }

    function updateWatchlist() {
        fetch('/update_watchlist_data/')
            .then(response => response.json())
            .then(data => {
                watchlistContainer.innerHTML = '';
                data.watchlist.forEach(item => {
                    const row = document.createElement('div');
                    row.className = 'watchlist-item';
                    const changeClass = item.change >= 0 ? 'positive' : 'negative';
                    const changeSign = item.change >= 0 ? '+' : '';
                    
                    row.innerHTML = `
                        <div class="symbol-info">
                            <span class="symbol">${item.symbol}</span>
                            <span class="name">${item.name}</span>
                        </div>
                        <div class="price-info">
                            <span class="price">${formatNumber(item.last_price)}</span>
                            <span class="change ${changeClass}">
                                ${changeSign}${formatNumber(item.change)} (${changeSign}${formatNumber(item.change_percent)}%)
                            </span>
                        </div>
                        <button class="delete-btn" data-symbol="${item.symbol}">×</button>
                    `;
                    
                    row.querySelector('.delete-btn').addEventListener('click', function(e) {
                        e.stopPropagation();e.stopPropagation();
                        deleteSymbol(this.dataset.symbol);
                    });
                    
                    row.addEventListener('click', function() {
                        window.location.href = `/display_ticker/${item.symbol}/`;
                    });
                    
                    watchlistContainer.appendChild(row);
                });
            });
    }

    function addSymbol(symbol) {
        const formData = new FormData();
        formData.append('action', 'add');
        formData.append('ticker', symbol);

        fetch('/manage_watchlist/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateWatchlist();
            } else {
                alert('Error adding symbol to watchlist');
            }
        });
    }

    function deleteSymbol(symbol) {
        const formData = new FormData();
        formData.append('action', 'delete');
        formData.append('ticker', symbol);

        fetch('/manage_watchlist/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateWatchlist();
            }
        });
    }

    addSymbolForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const symbol = symbolInput.value.trim().toUpperCase();
        if (symbol) {
            addSymbol(symbol);
            symbolInput.value = '';
        }
    });

    // Initial watchlist update
    updateWatchlist();

    // Update watchlist every 10 seconds
    setInterval(updateWatchlist, 10000);
});