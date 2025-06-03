# 円の為替相場チェッカー シーケンス図

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant UI as 為替相場チェッカーUI
    participant JS as JavaScript (script.js)
    participant API as ExchangeRate-API

    User->>Browser: index.htmlを開く
    Browser->>UI: ページを表示
    UI->>User: 通貨選択メニューを表示

    Note over User,UI: ユーザーが通貨を選択し操作を行う

    User->>UI: 通貨を選択 (例: USD)
    User->>UI: 「為替レートを確認」ボタンをクリック
    UI->>JS: イベントを発火
    JS->>UI: ローディング表示
    
    JS->>API: 為替レートデータをリクエスト
    Note right of JS: fetch('https://open.er-api.com/v6/latest/JPY')
    
    API->>JS: レスポンス（JSONデータ）
    
    alt 成功した場合
        JS->>JS: レートを計算 (1/data.rates[selectedCurrency])
        JS->>JS: データをフォーマット
        JS->>UI: 結果を表示
        UI->>User: 為替レート情報を表示
    else エラーが発生した場合
        JS->>UI: エラーメッセージを表示
        UI->>User: エラーメッセージを表示
    end

    Note over User,UI: ユーザーは別の通貨を選択して再度確認可能
```

## シーケンス図の説明

1. **初期表示**:
   - ユーザーがブラウザでindex.htmlを開く
   - 通貨選択メニューとボタンが表示される

2. **ユーザー操作**:
   - ユーザーがドロップダウンメニューから通貨（USD, EUR, GBP など）を選択
   - 「為替レートを確認」ボタンをクリック

3. **データ取得**:
   - JavaScriptがイベントを検知
   - UI上にローディング表示
   - ExchangeRate-APIにHTTPリクエストを送信
   - APIからJSONデータを受信

4. **結果表示**:
   - 成功時: レート計算 → データ整形 → 結果表示
   - エラー時: エラーメッセージを表示

5. **繰り返し使用**:
   - ユーザーは別の通貨を選択して再度確認可能