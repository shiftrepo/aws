"use client";

import { useState, useEffect } from 'react';
import styles from './CommandTerminal.module.css'; // 共通のスタイルを使用
import { DockerState, DifficultyLevel } from './DockerTypes';
import { DockerCommandInterpreter, DockerCommandEvent, DockerLearningEvent } from './DockerCommandInterpreter';

interface DockerTerminalProps {
  dockerState: DockerState;
  onDockerStateChange: (newState: DockerState) => void;
}

export default function DockerTerminal({ dockerState, onDockerStateChange }: DockerTerminalProps) {
  const [commandInput, setCommandInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([
    '$ docker --help',
    'Docker コマンドシミュレーション ヘルプ',
    '現在の難易度レベル: 初心者 (Level 1)',
    '',
    '利用可能なコマンド:',
    '  docker ps',
    '  docker run',
    '  docker images',
    '  docker stop',
    '  docker start',
    '  docker help',
    '',
    '各コマンドの詳細なヘルプは \'docker <コマンド> --help\' で確認できます。',
    '',
    'レベルアップすると、より高度なコマンドが利用可能になります。',
  ]);
  
  const [interpreter] = useState(() => new DockerCommandInterpreter(dockerState, DifficultyLevel.BEGINNER));
  const [difficultyLevel, setDifficultyLevel] = useState<DifficultyLevel>(DifficultyLevel.BEGINNER);
  const [learningHint, setLearningHint] = useState<string | null>(null);

  // 難易度レベルの変更時に処理
  useEffect(() => {
    interpreter.setDifficultyLevel(difficultyLevel);
  }, [difficultyLevel, interpreter]);

  // Dockerの状態が外部から変更された場合の処理
  useEffect(() => {
    interpreter.setState(dockerState);
  }, [dockerState, interpreter]);
  
  // コマンドイベントリスナーの設定
  useEffect(() => {
    const commandListener = (event: DockerCommandEvent) => {
      // コマンド実行結果に学習ヒントがあれば表示
      if ((event.result as any).learningHint) {
        setLearningHint((event.result as any).learningHint);
        // 5秒後に非表示
        setTimeout(() => setLearningHint(null), 5000);
      }
      
      // 状態変更を親コンポーネントに通知
      onDockerStateChange(event.currentState);
    };
    
    interpreter.addCommandListener(commandListener);
    
    return () => {
      interpreter.removeCommandListener(commandListener);
    };
  }, [interpreter, onDockerStateChange]);

  /**
   * コマンド実行処理
   * @param command 実行するコマンド文字列
   */
  const handleCommand = (command: string) => {
    // コマンド履歴に追加
    setCommandHistory(prev => [...prev, `$ ${command}`]);
    
    // コマンドの最初の部分だけを取得
    const parts = command.split(' ');
    const mainCommand = parts[0];
    
    if (mainCommand === 'docker' || mainCommand === 'docker-compose') {
      // dockerコマンドの実行
      const result = interpreter.executeCommand(command);
      
      // 結果メッセージを履歴に追加
      const messageLines = result.message.split('\n');
      setCommandHistory(prev => [...prev, ...messageLines]);
      
      // interpreter経由の状態更新は、コマンドイベントリスナーを通じて処理される
      // onDockerStateChangeは自動的に呼び出される
    } else if (command === 'clear') {
      // クリアコマンド
      setCommandHistory([]);
    } else if (command.startsWith('level ')) {
      // レベル変更コマンド（デバッグ用）
      const level = parseInt(command.split(' ')[1], 10);
      if (!isNaN(level) && level >= 1 && level <= 4) {
        setDifficultyLevel(level as DifficultyLevel);
        setCommandHistory(prev => [...prev, `難易度レベルを変更しました: ${getLevelName(level as DifficultyLevel)}`]);
      } else {
        setCommandHistory(prev => [...prev, 'エラー: 有効なレベルを指定してください（1-4）']);
      }
    } else {
      // サポートされていないコマンド
      setCommandHistory(prev => [...prev, `エラー: '${mainCommand}' はサポートされていないコマンドです。'docker'で始まるコマンドを使用してください。`]);
    }
  };

  /**
   * 入力フォーム送信時の処理
   */
  const handleSubmitCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (commandInput.trim() === '') return;
    
    handleCommand(commandInput);
    setCommandInput('');
  };

  /**
   * クイックアクションボタンの処理
   */
  const handleQuickAction = (command: string) => {
    handleCommand(command);
  };

  /**
   * 難易度レベル名の取得
   */
  const getLevelName = (level: DifficultyLevel): string => {
    switch (level) {
      case DifficultyLevel.BEGINNER:
        return '初心者 (Level 1)';
      case DifficultyLevel.BASIC:
        return '基本 (Level 2)';
      case DifficultyLevel.INTERMEDIATE:
        return '中級 (Level 3)';
      case DifficultyLevel.ADVANCED:
        return '上級 (Level 4)';
      default:
        return '不明';
    }
  };

  /**
   * レベルアップボタンの処理
   */
  const handleLevelUp = () => {
    if (difficultyLevel < DifficultyLevel.ADVANCED) {
      const newLevel = difficultyLevel + 1 as DifficultyLevel;
      setDifficultyLevel(newLevel);
      setCommandHistory(prev => [...prev, `難易度レベルがアップしました！: ${getLevelName(newLevel)}`]);
      setCommandHistory(prev => [...prev, '新しいコマンドが利用可能になりました。「docker help」で確認できます。']);
    } else {
      setCommandHistory(prev => [...prev, 'すでに最高レベルです。']);
    }
  };

  /**
   * レベルに応じたクイックアクションボタン表示
   */
  const renderQuickActionButtons = () => {
    // 基本コマンド (Level 1)
    const basicCommands = [
      { command: 'docker ps', label: 'docker ps' },
      { command: 'docker images', label: 'docker images' },
      { command: 'docker help', label: 'docker help' }
    ];

    // Level 2 以上で利用可能
    const level2Commands = difficultyLevel >= DifficultyLevel.BASIC ? [
      { command: 'docker pull nginx', label: 'docker pull' },
      { command: 'docker logs', label: 'docker logs' }
    ] : [];

    // Level 3 以上で利用可能
    const level3Commands = difficultyLevel >= DifficultyLevel.INTERMEDIATE ? [
      { command: 'docker network ls', label: 'docker network' },
      { command: 'docker volume ls', label: 'docker volume' }
    ] : [];

    // Level 4 で利用可能
    const level4Commands = difficultyLevel >= DifficultyLevel.ADVANCED ? [
      { command: 'docker compose', label: 'docker compose' }
    ] : [];

    const allCommands = [...basicCommands, ...level2Commands, ...level3Commands, ...level4Commands];

    return (
      <div className={styles.quickActions}>
        {allCommands.map((cmd, index) => (
          <button key={index} onClick={() => handleQuickAction(cmd.command)}>
            {cmd.label}
          </button>
        ))}
        <button className={styles.levelUpButton} onClick={handleLevelUp}>
          レベルアップ
        </button>
      </div>
    );
  };

  /**
   * レベルに応じたヘルプ情報表示
   */
  const renderHelpInfo = () => {
    // レベルに応じて表示するヘルプを変更
    const helpCommands = [];
    
    // Level 1 (BEGINNER)
    helpCommands.push(
      { command: 'docker ps', description: 'コンテナ一覧表示' },
      { command: 'docker run', description: 'コンテナ作成・起動' },
      { command: 'docker images', description: 'イメージ一覧表示' },
      { command: 'docker start/stop', description: 'コンテナ起動/停止' }
    );
    
    // Level 2 (BASIC)
    if (difficultyLevel >= DifficultyLevel.BASIC) {
      helpCommands.push(
        { command: 'docker pull', description: 'イメージ取得' },
        { command: 'docker rm/rmi', description: 'コンテナ/イメージ削除' },
        { command: 'docker logs', description: 'コンテナログ表示' }
      );
    }
    
    // Level 3 (INTERMEDIATE)
    if (difficultyLevel >= DifficultyLevel.INTERMEDIATE) {
      helpCommands.push(
        { command: 'docker build', description: 'イメージビルド' },
        { command: 'docker network', description: 'ネットワーク管理' },
        { command: 'docker volume', description: 'ボリューム管理' },
        { command: 'docker exec', description: 'コンテナでコマンド実行' }
      );
    }
    
    // Level 4 (ADVANCED)
    if (difficultyLevel >= DifficultyLevel.ADVANCED) {
      helpCommands.push(
        { command: 'docker compose', description: '複数コンテナの管理' }
      );
    }
    
    return (
      <div className={styles.help}>
        <h3>使えるコマンド (レベル: {getLevelName(difficultyLevel)})</h3>
        <ul>
          {helpCommands.map((cmd, index) => (
            <li key={index}><code>{cmd.command}</code> - {cmd.description}</li>
          ))}
        </ul>
        {difficultyLevel < DifficultyLevel.ADVANCED && (
          <div className={styles.levelUpHint}>
            <p>ヒント: <strong>レベルアップ</strong>ボタンをクリックすると新しいコマンドが解放されます。</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={styles.terminal}>
      <div className={styles.header}>
        <div className={styles.dots}>
          <div className={styles.dot} style={{ backgroundColor: '#ff5f56' }}></div>
          <div className={styles.dot} style={{ backgroundColor: '#ffbd2e' }}></div>
          <div className={styles.dot} style={{ backgroundColor: '#27c93f' }}></div>
        </div>
        <div className={styles.title}>Docker Terminal</div>
      </div>
      
      <div className={styles.terminalBody}>
        <div className={styles.output}>
          {commandHistory.map((line, index) => (
            <div key={index} className={line.startsWith('$') ? styles.command : styles.response}>
              {line}
            </div>
          ))}
        </div>
        
        <form className={styles.inputForm} onSubmit={handleSubmitCommand}>
          <div className={styles.prompt}>$</div>
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            className={styles.input}
            placeholder="docker コマンドを入力してください..."
            autoFocus
          />
        </form>
      </div>
      
      {learningHint && (
        <div className={styles.learningHint}>
          <div className={styles.learningHintHeader}>
            <span role="img" aria-label="lightbulb">💡</span> Docker学習ポイント
          </div>
          <div className={styles.learningHintContent}>
            {learningHint}
          </div>
        </div>
      )}
      
      {renderQuickActionButtons()}
      {renderHelpInfo()}
    </div>
  );
}