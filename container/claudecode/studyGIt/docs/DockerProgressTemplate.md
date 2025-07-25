# Docker コマンド シミュレーション 進捗報告テンプレート

このテンプレートは GitHub Issue #48 に進捗報告を投稿する際の標準フォーマットです。
1日1回以上の報告をお願いします。

## 進捗報告フォーマット

```markdown
## 日次進捗報告 - YYYY-MM-DD

### 担当者
[担当者名]

### 完了したタスク
- [タスク1の説明]
- [タスク2の説明]
- [タスク3の説明]

### 現在取り組んでいる作業
- [現在の作業内容]
- [進捗状況（％）]
- [今日のマイルストーン]

### 次に予定している作業
- [次のタスク1]
- [次のタスク2]

### 発生している課題や質問事項
- [課題1の説明]
- [質問1の内容]

### スクリーンショット
[実装したコンポーネントのスクリーンショット]
```

## スクリーンショット共有プロセス

1. 実装したコンポーネントのスクリーンショットを撮影
2. GitHub Issue #48 にアップロード
3. 以下の情報を添えて共有：
   - スクリーンショットの説明（何を示しているか）
   - 実装した機能
   - ユーザーの操作方法
   - 既知の問題点（もしあれば）

## テスト結果報告

podman-compose での動作確認結果は以下のフォーマットで報告してください：

```markdown
## Docker コマンドシミュレーション テスト結果

### テスト概要
- テスト実施日: YYYY-MM-DD
- テスト環境: [ブラウザ/OS]

### テスト結果サマリー
- 正常動作: [項目数]
- 問題あり: [項目数]

### 確認済み機能
- [機能1]: ✅
- [機能2]: ✅
- [機能3]: ❌ - [問題の詳細]

### podman-compose ログ
```
[関連するログ出力]
```

### 発見された問題点
1. [問題1の説明]
   - 再現手順: [手順]
   - 予想される原因: [原因]
   - 提案される解決策: [解決策]

2. [問題2の説明]
   - 再現手順: [手順]
   - 予想される原因: [原因]
   - 提案される解決策: [解決策]
```

## 定期ミーティングの準備

毎日11:00の定期ミーティングでの報告内容を以下の通り準備してください：

1. 完了したタスクのサマリー（箇条書き・5項目以内）
2. 現在の作業状況（1-2文）
3. ブロッカーとなっている課題（もしあれば）
4. チームからのサポートが必要な点（もしあれば）
5. 明日の目標（1-2文）

## 問題発生時の報告

問題が発生した場合は、以下のフォーマットで直ちに報告してください：

```markdown
## 🚨 問題報告

### 問題の概要
[簡潔な問題の説明]

### 発生状況
- 発生日時: YYYY-MM-DD HH:MM
- 環境: [開発環境の詳細]
- 再現性: [毎回/時々/一度だけ]

### 再現手順
1. [手順1]
2. [手順2]
3. [手順3]

### 期待される動作
[本来どのように動作すべきか]

### 実際の動作
[実際にどのように動作したか]

### エラーメッセージ/ログ
```
[エラーメッセージやログの内容]
```

### スクリーンショット/動画
[問題を示すスクリーンショット/動画]

### 緊急度
[高/中/低] - [理由]

### 提案される解決策
[もし考えがあれば]
```

---

これらのテンプレートを活用して、チーム全体での効率的な情報共有と問題解決を促進しましょう。
報告の質と頻度がプロジェクトの成功に直結します。