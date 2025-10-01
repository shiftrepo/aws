/**
 * DockerCommandInterpreter.ts
 * Docker コマンドの解釈と実行、および他コンポーネントとの連携を担当
 */

import { DockerSimulator, DockerState, DifficultyLevel, CommandResult } from './DockerSimulator';

// Docker コマンド実行イベントの型定義
export interface DockerCommandEvent {
  command: string;         // 実行されたコマンド
  result: CommandResult;   // 実行結果
  previousState: DockerState; // 実行前のDocker状態
  currentState: DockerState;  // 実行後のDocker状態
  timestamp: number;       // イベント発生時刻
}

// 学習イベントの型定義
export interface DockerLearningEvent {
  topic: string;           // 学習したトピック
  command: string;         // 関連するコマンド
  level: DifficultyLevel;  // 学習レベル
  completed: boolean;      // 完了フラグ
  timestamp: number;       // イベント発生時刻
}

// イベントリスナーの型定義
export type DockerCommandListener = (event: DockerCommandEvent) => void;
export type DockerLearningListener = (event: DockerLearningEvent) => void;

// 学習テーマの定義
export enum DockerLearningTopic {
  CONTAINER_BASICS = 'container_basics',
  CONTAINER_VS_VM = 'container_vs_vm',
  CONTAINER_HOST_RELATION = 'container_host_relation',
  IMAGES = 'images',
  VOLUMES = 'volumes',
  NETWORKS = 'networks',
  COMPOSE = 'compose'
}

// 学習ヒントのマッピング
interface DockerLearningHint {
  topic: DockerLearningTopic;
  message: string;
  commands: string[];
}

/**
 * Docker コマンドインタープリター
 * DockerSimulator のラッパーとして機能し、イベント通知とコンポーネント連携を提供
 */
export class DockerCommandInterpreter {
  private simulator: DockerSimulator;
  private commandListeners: DockerCommandListener[] = [];
  private learningListeners: DockerLearningListener[] = [];
  private learningProgress: Record<DockerLearningTopic, boolean> = {
    [DockerLearningTopic.CONTAINER_BASICS]: false,
    [DockerLearningTopic.CONTAINER_VS_VM]: false,
    [DockerLearningTopic.CONTAINER_HOST_RELATION]: false,
    [DockerLearningTopic.IMAGES]: false,
    [DockerLearningTopic.VOLUMES]: false,
    [DockerLearningTopic.NETWORKS]: false,
    [DockerLearningTopic.COMPOSE]: false
  };

  // 学習ヒントのマッピング
  private learningHints: DockerLearningHint[] = [
    {
      topic: DockerLearningTopic.CONTAINER_BASICS,
      message: 'コンテナは軽量な実行環境です。アプリケーションとその依存関係をパッケージ化しています。',
      commands: ['docker ps', 'docker run', 'docker start', 'docker stop']
    },
    {
      topic: DockerLearningTopic.CONTAINER_VS_VM,
      message: 'コンテナは仮想マシン(VM)と異なり、ホストOSのカーネルを共有するため、軽量で高速に起動できます。',
      commands: ['docker run', 'docker images']
    },
    {
      topic: DockerLearningTopic.CONTAINER_HOST_RELATION,
      message: 'コンテナはホストマシンと分離されていますが、ポートマッピングやボリュームマウントでホストと連携できます。',
      commands: ['docker run -p', 'docker run -v']
    },
    {
      topic: DockerLearningTopic.IMAGES,
      message: 'Dockerイメージはアプリケーションと実行環境を含む読み取り専用のテンプレートです。',
      commands: ['docker images', 'docker pull', 'docker build', 'docker rmi']
    },
    {
      topic: DockerLearningTopic.VOLUMES,
      message: 'Dockerボリュームはデータを永続化し、コンテナ間で共有するための仕組みです。',
      commands: ['docker volume', 'docker run -v']
    },
    {
      topic: DockerLearningTopic.NETWORKS,
      message: 'Dockerネットワークはコンテナ間の通信を管理し、分離やセキュリティを確保します。',
      commands: ['docker network', 'docker run --network']
    },
    {
      topic: DockerLearningTopic.COMPOSE,
      message: 'Docker Composeは複数のコンテナを定義・実行するためのツールです。サービス、ネットワーク、ボリュームを設定できます。',
      commands: ['docker compose']
    }
  ];

  /**
   * コンストラクタ
   * @param initialState 初期Docker状態
   * @param level 初期難易度レベル
   */
  constructor(initialState?: DockerState, level: DifficultyLevel = DifficultyLevel.BEGINNER) {
    this.simulator = new DockerSimulator(initialState, level);
  }

  /**
   * コマンド実行
   * @param command 実行するコマンド文字列
   * @returns コマンド実行結果
   */
  executeCommand(command: string): CommandResult {
    // 実行前の状態を保存
    const previousState = this.simulator.getState();
    
    // シミュレータでコマンドを実行
    const result = this.simulator.executeCommand(command);
    
    // 実行後の状態を取得
    const currentState = this.simulator.getState();
    
    // コマンドイベント発行
    const commandEvent: DockerCommandEvent = {
      command,
      result,
      previousState,
      currentState,
      timestamp: Date.now()
    };
    
    // コマンドリスナーに通知
    this.notifyCommandListeners(commandEvent);
    
    // 学習進捗をチェック
    this.checkLearningProgress(command, result);
    
    return result;
  }

  /**
   * コマンドリスナー追加
   * @param listener コマンドイベントリスナー
   */
  addCommandListener(listener: DockerCommandListener): void {
    this.commandListeners.push(listener);
  }

  /**
   * コマンドリスナー削除
   * @param listener 削除するリスナー
   */
  removeCommandListener(listener: DockerCommandListener): void {
    this.commandListeners = this.commandListeners.filter(l => l !== listener);
  }

  /**
   * 学習リスナー追加
   * @param listener 学習イベントリスナー
   */
  addLearningListener(listener: DockerLearningListener): void {
    this.learningListeners.push(listener);
  }

  /**
   * 学習リスナー削除
   * @param listener 削除するリスナー
   */
  removeLearningListener(listener: DockerLearningListener): void {
    this.learningListeners = this.learningListeners.filter(l => l !== listener);
  }

  /**
   * コマンドリスナーに通知
   * @param event コマンドイベント
   */
  private notifyCommandListeners(event: DockerCommandEvent): void {
    this.commandListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in command listener:', error);
      }
    });
  }

  /**
   * 学習リスナーに通知
   * @param event 学習イベント
   */
  private notifyLearningListeners(event: DockerLearningEvent): void {
    this.learningListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in learning listener:', error);
      }
    });
  }

  /**
   * 学習進捗をチェック
   * @param command 実行されたコマンド
   * @param result コマンド実行結果
   */
  private checkLearningProgress(command: string, result: CommandResult): void {
    if (!result.success) return; // 失敗したコマンドは学習に含めない
    
    // 学習ヒントをチェック
    for (const hint of this.learningHints) {
      // この学習トピックが未完了で、このコマンドがトピックに関連する場合
      if (!this.learningProgress[hint.topic] && this.isCommandRelatedToTopic(command, hint.commands)) {
        // 学習完了としてマーク
        this.learningProgress[hint.topic] = true;
        
        // 学習イベント発行
        const learningEvent: DockerLearningEvent = {
          topic: hint.topic,
          command,
          level: this.simulator.getDifficultyLevel(),
          completed: true,
          timestamp: Date.now()
        };
        
        // 学習リスナーに通知
        this.notifyLearningListeners(learningEvent);
        
        // 関連する学習ヒントを取得
        const learningHint = hint.message;
        
        // 実行結果にヒントを追加（別のプロパティとして）
        (result as any).learningHint = learningHint;
        
        break;
      }
    }
  }

  /**
   * コマンドが特定の学習トピックに関連しているか確認
   * @param command 実行されたコマンド
   * @param relatedCommands トピックに関連するコマンドリスト
   * @returns 関連がある場合true
   */
  private isCommandRelatedToTopic(command: string, relatedCommands: string[]): boolean {
    return relatedCommands.some(relatedCmd => command.startsWith(relatedCmd));
  }

  /**
   * 難易度レベル設定
   * @param level 新しい難易度レベル
   */
  setDifficultyLevel(level: DifficultyLevel): void {
    this.simulator.setDifficultyLevel(level);
  }

  /**
   * 現在の難易度レベル取得
   * @returns 現在の難易度レベル
   */
  getDifficultyLevel(): DifficultyLevel {
    return this.simulator.getDifficultyLevel();
  }

  /**
   * 現在のDocker状態取得
   * @returns 現在のDocker状態
   */
  getState(): DockerState {
    return this.simulator.getState();
  }

  /**
   * Docker状態の設定
   * @param newState 新しいDocker状態
   */
  setState(newState: DockerState): void {
    this.simulator.setState(newState);
  }

  /**
   * 学習トピック情報を取得
   * @param topic 学習トピック
   * @returns トピックに関する情報とヒント
   */
  getLearningTopicInfo(topic: DockerLearningTopic): DockerLearningHint | null {
    return this.learningHints.find(hint => hint.topic === topic) || null;
  }

  /**
   * すべての学習トピックと進捗状況を取得
   * @returns トピックと進捗状況のマップ
   */
  getLearningProgress(): Record<DockerLearningTopic, boolean> {
    return {...this.learningProgress};
  }

  /**
   * 学習トピックに関連するコマンド例を取得
   * @param topic 学習トピック
   * @returns 関連するコマンド例
   */
  getRelatedCommandsForTopic(topic: DockerLearningTopic): string[] {
    const hint = this.learningHints.find(h => h.topic === topic);
    return hint ? [...hint.commands] : [];
  }

  /**
   * コマンド例から学習ヒントを生成
   * @param command コマンド文字列
   * @returns 関連する学習ヒント（ない場合はnull）
   */
  getHintForCommand(command: string): string | null {
    for (const hint of this.learningHints) {
      if (this.isCommandRelatedToTopic(command, hint.commands)) {
        return hint.message;
      }
    }
    return null;
  }
}