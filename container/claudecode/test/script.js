document.addEventListener('DOMContentLoaded', function() {
    const currencySelect = document.getElementById('currency-select');
    const checkRateButton = document.getElementById('check-rate');
    const resultArea = document.getElementById('result-area');

    checkRateButton.addEventListener('click', checkExchangeRate);

    async function checkExchangeRate() {
        const selectedCurrency = currencySelect.value;
        
        // Show loading state
        resultArea.innerHTML = '<div class="loading"></div> データを取得中...';
        
        try {
            // Using ExchangeRate-API for free exchange rate data
            const response = await fetch(`https://open.er-api.com/v6/latest/JPY`);
            
            if (!response.ok) {
                throw new Error('データの取得に失敗しました');
            }
            
            const data = await response.json();
            
            // Calculate JPY exchange rate (API returns rates relative to selected base currency)
            // Since we're getting rates with JPY as base, we need the inverse for "X currency to 1 JPY"
            const rate = 1 / data.rates[selectedCurrency];
            
            // Format the results
            const formattedRate = rate.toFixed(4);
            const currencyName = getCurrencyName(selectedCurrency);
            const updateTime = new Date(data.time_last_update_utc).toLocaleString('ja-JP');
            
            resultArea.innerHTML = `
                <p>1${currencyName}は</p>
                <div class="rate-display">${formattedRate} 円</div>
                <p>です。</p>
                <p class="updated-time">更新時間: ${updateTime}</p>
            `;
        } catch (error) {
            resultArea.innerHTML = `<p>エラーが発生しました: ${error.message}</p>`;
        }
    }
    
    function getCurrencyName(code) {
        const currencies = {
            'USD': '米ドル',
            'EUR': 'ユーロ',
            'GBP': '英ポンド',
            'AUD': '豪ドル',
            'CAD': 'カナダドル',
            'CNY': '中国元'
        };
        
        return currencies[code] ? currencies[code] : code;
    }
});