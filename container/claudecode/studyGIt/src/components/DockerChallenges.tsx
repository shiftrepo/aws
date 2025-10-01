"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styles from './DockerGuide.module.css';
import { DifficultyLevel } from './DockerSimulator';

export interface Challenge {
  id: string;
  title: string;
  description: string;
  difficultyLevel: DifficultyLevel;
  hint: string;
  solution: string;
  expectedCommand: string | RegExp;
  isCompleted: boolean;
  testFn?: (cmd: string) => boolean;
}

export interface DockerChallengesProps {
  currentLevel: DifficultyLevel;
  onChallengeComplete: (challengeId: string) => void;
  onCommandExecute?: (command: string) => void;
}

const DockerChallenges: React.FC<DockerChallengesProps> = ({ 
  currentLevel, 
  onChallengeComplete,
  onCommandExecute
}) => {
  const [challenges, setChallenges] = useState<Challenge[]>([
    // レベル1: 初心者向けチャレンジ
    {
      id: 'basic-1',
      title: 'コンテナリスト表示',
      description: '実行中のコンテナの一覧を表示するコマンドを実行してください。',
      difficultyLevel: DifficultyLevel.BEGINNER,
      hint: 'docker psコマンドを使います。',
      solution: 'docker ps',
      expectedCommand: 'docker ps',
      isCompleted: false
    },
    {
      id: 'basic-2',
      title: 'イメージ一覧表示',
      description: '利用可能なDockerイメージの一覧を表示するコマンドを実行してください。',
      difficultyLevel: DifficultyLevel.BEGINNER,
      hint: 'docker imagesコマンドを使います。',
      solution: 'docker images',
      expectedCommand: 'docker images',
      isCompleted: false
    },
    {
      id: 'basic-3',
      title: 'Nginxコンテナの実行',
      description: 'Nginxイメージを使用して、バックグラウンドで実行され、ホストの8080ポートをコンテナの80ポートにマッピングするコンテナを起動してください。',
      difficultyLevel: DifficultyLevel.BEGINNER,
      hint: 'docker runコマンドを使い、-dフラグでバックグラウンド実行、-pフラグでポートマッピングを指定します。',
      solution: 'docker run -d -p 8080:80 nginx',
      expectedCommand: /docker run .*-d.*-p.*8080:80.*nginx|docker run .*-p.*8080:80.*-d.*nginx/,
      isCompleted: false
    },

    // レベル2: 基本的なチャレンジ
    {
      id: 'intermediate-1',
      title: 'イメージのプル',
      description: 'Redis最新バージョンのイメージをプルしてください。',
      difficultyLevel: DifficultyLevel.BASIC,
      hint: 'docker pullコマンドを使います。',
      solution: 'docker pull redis',
      expectedCommand: /docker pull redis(:latest)?/,
      isCompleted: false
    },
    {
      id: 'intermediate-2',
      title: 'コンテナのログ確認',
      description: 'my-containerという名前のコンテナのログを表示してください。',
      difficultyLevel: DifficultyLevel.BASIC,
      hint: 'docker logsコマンドを使います。',
      solution: 'docker logs my-container',
      expectedCommand: 'docker logs my-container',
      isCompleted: false
    },
    {
      id: 'intermediate-3',
      title: 'コンテナの削除',
      description: '停止中のコンテナmy-containerを削除してください。',
      difficultyLevel: DifficultyLevel.BASIC,
      hint: 'docker rmコマンドを使います。',
      solution: 'docker rm my-container',
      expectedCommand: 'docker rm my-container',
      isCompleted: false
    },

    // レベル3: 中級者向けチャレンジ
    {
      id: 'advanced-1',
      title: 'ネットワーク作成',
      description: 'my-networkという名前の新しいDockerネットワークを作成してください。',
      difficultyLevel: DifficultyLevel.INTERMEDIATE,
      hint: 'docker network createコマンドを使います。',
      solution: 'docker network create my-network',
      expectedCommand: 'docker network create my-network',
      isCompleted: false
    },
    {
      id: 'advanced-2',
      title: 'ボリューム作成',
      description: 'my-dataという名前の新しいDockerボリュームを作成してください。',
      difficultyLevel: DifficultyLevel.INTERMEDIATE,
      hint: 'docker volume createコマンドを使います。',
      solution: 'docker volume create my-data',
      expectedCommand: 'docker volume create my-data',
      isCompleted: false
    },
    {
      id: 'advanced-3',
      title: 'コンテナ内でのコマンド実行',
      description: 'my-containerという名前のコンテナ内でlsコマンドを実行してください。',
      difficultyLevel: DifficultyLevel.INTERMEDIATE,
      hint: 'docker execコマンドを使います。',
      solution: 'docker exec my-container ls',
      expectedCommand: /docker exec my-container ls.*/,
      isCompleted: false
    },

    // レベル4: 上級者向けチャレンジ
    {
      id: 'expert-1',
      title: 'Docker Compose起動',
      description: 'Docker Composeを使用して、バックグラウンドでサービスを起動してください。',
      difficultyLevel: DifficultyLevel.ADVANCED,
      hint: 'docker compose upコマンドと-dフラグを使います。',
      solution: 'docker compose up -d',
      expectedCommand: /docker compose up -d|docker-compose up -d/,
      isCompleted: false
    },
    {
      id: 'expert-2',
      title: 'Docker Compose停止',
      description: 'Docker Composeを使用して、すべてのサービスを停止し、コンテナとネットワークを削除してください。',
      difficultyLevel: DifficultyLevel.ADVANCED,
      hint: 'docker compose downコマンドを使います。',
      solution: 'docker compose down',
      expectedCommand: /docker compose down|docker-compose down/,
      isCompleted: false
    }
  ]);

  // ユーザーのレベルに応じたチャレンジのみ表示
  const availableChallenges = challenges.filter(
    challenge => challenge.difficultyLevel <= currentLevel
  );

  // チャレンジの進捗状況を計算
  const completedCount = availableChallenges.filter(c => c.isCompleted).length;
  const progressPercentage = availableChallenges.length > 0 
    ? (completedCount / availableChallenges.length) * 100
    : 0;

  // コマンド検証のハンドラー
  const checkCommand = (command: string, challenge: Challenge) => {
    let isCorrect = false;
    
    if (challenge.testFn) {
      // カスタムテスト関数がある場合はそれを使用
      isCorrect = challenge.testFn(command);
    } else if (challenge.expectedCommand instanceof RegExp) {
      // 正規表現の場合
      isCorrect = challenge.expectedCommand.test(command);
    } else {
      // 文字列の完全一致
      isCorrect = command === challenge.expectedCommand;
    }
    
    if (isCorrect && !challenge.isCompleted) {
      // チャレンジ成功を記録
      const updatedChallenges = challenges.map(c => 
        c.id === challenge.id ? { ...c, isCompleted: true } : c
      );
      setChallenges(updatedChallenges);
      
      // 親コンポーネントに通知
      onChallengeComplete(challenge.id);
    }
    
    return isCorrect;
  };

  // 初期状態をLocalStorageから復元
  useEffect(() => {
    const savedChallenges = localStorage.getItem('docker-challenges');
    if (savedChallenges) {
      try {
        const parsedChallenges = JSON.parse(savedChallenges);
        setChallenges(prevChallenges => 
          prevChallenges.map(c => {
            const savedChallenge = parsedChallenges.find((saved: Challenge) => saved.id === c.id);
            return savedChallenge ? { ...c, isCompleted: savedChallenge.isCompleted } : c;
          })
        );
      } catch (error) {
        console.error('Failed to parse saved challenges', error);
      }
    }
  }, []);

  // チャレンジの状態変更をLocalStorageに保存
  useEffect(() => {
    localStorage.setItem('docker-challenges', JSON.stringify(challenges.map(c => ({
      id: c.id,
      isCompleted: c.isCompleted
    }))));
  }, [challenges]);

  // コマンド実行をDockerTerminalに伝播
  const handleTryCommand = (command: string) => {
    if (onCommandExecute) {
      onCommandExecute(command);
    }
  };

  return (
    <motion.div 
      className={styles.dockerChallenges}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <h2>Dockerチャレンジ</h2>
      
      <div className={styles.challengeProgress}>
        <div className={styles.progressText}>
          進捗状況: {completedCount} / {availableChallenges.length} チャレンジ完了
        </div>
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill}
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>
      
      <div className={styles.challengeList}>
        {availableChallenges.map((challenge) => (
          <motion.div 
            key={challenge.id}
            className={`${styles.challengeCard} ${challenge.isCompleted ? styles.completed : ''}`}
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className={styles.challengeHeader}>
              <h3>{challenge.title}</h3>
              {challenge.isCompleted && (
                <span className={styles.completedBadge}>
                  ✓ 完了
                </span>
              )}
            </div>
            
            <p className={styles.challengeDescription}>{challenge.description}</p>
            
            <div className={styles.challengeActions}>
              <div className={styles.hintSection}>
                <details>
                  <summary>ヒントを見る</summary>
                  <p className={styles.hint}>{challenge.hint}</p>
                </details>
              </div>
              
              <div className={styles.solutionSection}>
                <details>
                  <summary>解答を見る</summary>
                  <div className={styles.solution}>
                    <div className={styles.solutionCommand}>{challenge.solution}</div>
                    <button 
                      className={styles.tryButton}
                      onClick={() => handleTryCommand(challenge.solution)}
                    >
                      試してみる
                    </button>
                  </div>
                </details>
              </div>
            </div>
            
            <div className={styles.difficultyBadge}>
              {getDifficultyLabel(challenge.difficultyLevel)}
            </div>
          </motion.div>
        ))}
      </div>
      
      {availableChallenges.length === 0 && (
        <div className={styles.noChallenge}>
          <p>現在のレベルで利用可能なチャレンジはありません。レベルアップするとチャレンジが解放されます。</p>
        </div>
      )}
      
      {currentLevel < DifficultyLevel.ADVANCED && (
        <div className={styles.levelUpInfo}>
          <p>「レベルアップ」ボタンをクリックすると、より高度なチャレンジが解放されます。</p>
        </div>
      )}
    </motion.div>
  );
};

// 難易度レベルのラベル取得
function getDifficultyLabel(level: DifficultyLevel): string {
  switch (level) {
    case DifficultyLevel.BEGINNER:
      return '初級';
    case DifficultyLevel.BASIC:
      return '基本';
    case DifficultyLevel.INTERMEDIATE:
      return '中級';
    case DifficultyLevel.ADVANCED:
      return '上級';
    default:
      return '不明';
  }
}

export default DockerChallenges;