# Docker学習コンポーネント 統合図

```
┌────────────────────────────────────────────────────────────────┐
│                    Playground (page.tsx)                       │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                   DockerLearningProvider                       │
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │             │    │             │    │                     │ │
│  │ DockerGuide ◄────► Learning    ◄────► DockerChallenges    │ │
│  │             │    │ Context     │    │                     │ │
│  └──────┬──────┘    │             │    └──────────┬──────────┘ │
│         │           │             │               │            │
│         │           │             │               │            │
│  ┌──────▼──────┐    │             │    ┌──────────▼──────────┐ │
│  │             │    │             │    │                     │ │
│  │ Visualizer  ◄────┤             ├────► Terminal            │ │
│  │             │    │             │    │                     │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘

```

## コンポーネント間のデータフロー

1. **DockerLearningContext**
   - 中央の状態管理システム
   - 学習進捗、トピック完了状態、難易度レベルを管理
   - LocalStorageを使用してユーザー設定を永続化

2. **DockerGuide ←→ LearningContext**
   - 学習進捗に基づいてコンテンツを適応表示
   - 完了したトピックを記録
   - ユーザーレベルに応じた追加情報を表示

3. **DockerChallenges ←→ LearningContext**
   - 完了したチャレンジの状態を同期
   - ユーザーレベルに基づいて利用可能なチャレンジをフィルタリング
   - バッジやレベルアップ条件をチェック

4. **DockerTerminal ←→ LearningContext**
   - ユーザーのレベルに応じてコマンド機能を解放
   - 学習進捗に基づいたヒントを表示
   - 実行されたコマンドを記録して学習状態を更新

5. **DockerVisualizer ←→ LearningContext**
   - 教育モードの有効/無効を同期
   - 学習レベルに応じたヒントの表示
   - インタラクティブな学習ポイントを強調表示

6. **DockerTerminal ←→ DockerVisualizer**
   - ターミナルでのコマンド実行結果を視覚化
   - DockerStateオブジェクトを共有
   - コンテナ、ネットワーク、ボリュームの状態変化を連動

7. **DockerTerminal ←→ DockerChallenges**
   - チャレンジで提示されたコマンドをターミナルで実行
   - ターミナルの入力をチャレンジの達成条件として検証
   - 両方のコンポーネントでの進捗を同期

## 現在の実装状況

- ✅ DockerGuide ←→ LearningContext
- ✅ DockerChallenges ←→ LearningContext
- ✅ DockerVisualizer ←→ LearningContext
- ✅ DockerTerminal ←→ LearningContext
- ✅ DockerTerminal ←→ DockerVisualizer
- 🔄 DockerTerminal ←→ DockerChallenges (部分的に実装、最適化が必要)