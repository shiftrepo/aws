"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { DifficultyLevel } from './DockerSimulator';

// 学習トピック
export interface LearningTopic {
  id: string;
  title: string;
  description: string;
  difficultyLevel: DifficultyLevel;
  isCompleted: boolean;
  isLocked: boolean;
  requiredTopics?: string[];  // この前に完了すべきトピックID
}

// 学習進行状態
export interface LearningProgress {
  userId: string;
  completedTopics: string[];
  lastStudiedTopic: string | null;
  difficultyLevel: DifficultyLevel;
  completedChallenges: string[];
  badges: string[];
  language: 'ja' | 'en';
}

// コンテキスト型定義
interface DockerLearningContextType {
  // 学習トピックとステート
  topics: LearningTopic[];
  currentTopicId: string | null;
  progress: LearningProgress;
  
  // 教育モード
  educationalMode: boolean;
  educationalTipsEnabled: boolean;

  // メソッド
  setCurrentTopic: (topicId: string) => void;
  completeCurrentTopic: () => void;
  completeTopic: (topicId: string) => void;
  completeChallenge: (challengeId: string) => void;
  getNextRecommendedTopic: () => string | null;
  setDifficultyLevel: (level: DifficultyLevel) => void;
  toggleEducationalMode: () => void;
  toggleEducationalTips: () => void;
  setLanguage: (language: 'ja' | 'en') => void;
  resetProgress: () => void;
}

// デフォルトコンテキスト値
const defaultContext: DockerLearningContextType = {
  topics: [],
  currentTopicId: null,
  progress: {
    userId: 'guest',
    completedTopics: [],
    lastStudiedTopic: null,
    difficultyLevel: DifficultyLevel.BEGINNER,
    completedChallenges: [],
    badges: [],
    language: 'ja'
  },
  educationalMode: true,
  educationalTipsEnabled: true,
  
  setCurrentTopic: () => {},
  completeCurrentTopic: () => {},
  completeTopic: () => {},
  completeChallenge: () => {},
  getNextRecommendedTopic: () => null,
  setDifficultyLevel: () => {},
  toggleEducationalMode: () => {},
  toggleEducationalTips: () => {},
  setLanguage: () => {},
  resetProgress: () => {}
};

// コンテキスト作成
const DockerLearningContext = createContext<DockerLearningContextType>(defaultContext);

// 初期トピックデータ
const initialTopics: LearningTopic[] = [
  // 初心者レベル (Beginner)
  {
    id: 'docker-intro',
    title: 'Dockerとは何か',
    description: 'Dockerの基本概念と仮想化との違い',
    difficultyLevel: DifficultyLevel.BEGINNER,
    isCompleted: false,
    isLocked: false
  },
  {
    id: 'container-vs-vm',
    title: 'コンテナとVMの違い',
    description: 'コンテナと仮想マシンの違いと特徴',
    difficultyLevel: DifficultyLevel.BEGINNER,
    isCompleted: false,
    isLocked: false,
    requiredTopics: ['docker-intro']
  },
  {
    id: 'docker-basic-commands',
    title: 'Docker基本コマンド',
    description: 'Dockerの基本的なコマンドと使い方',
    difficultyLevel: DifficultyLevel.BEGINNER,
    isCompleted: false,
    isLocked: false,
    requiredTopics: ['docker-intro']
  },

  // 基本レベル (Basic)
  {
    id: 'dockerfile',
    title: 'Dockerfile作成',
    description: 'Dockerfileの書き方と構成方法',
    difficultyLevel: DifficultyLevel.BASIC,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['docker-basic-commands']
  },
  {
    id: 'docker-images',
    title: 'Dockerイメージ管理',
    description: 'イメージの作成、管理、配布方法',
    difficultyLevel: DifficultyLevel.BASIC,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['dockerfile']
  },

  // 中級レベル (Intermediate)
  {
    id: 'docker-compose',
    title: 'Docker Compose',
    description: '複数コンテナの設定と管理',
    difficultyLevel: DifficultyLevel.INTERMEDIATE,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['docker-images']
  },
  {
    id: 'docker-networks',
    title: 'Dockerネットワーク',
    description: 'コンテナ間通信とネットワーク設定',
    difficultyLevel: DifficultyLevel.INTERMEDIATE,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['docker-compose']
  },
  {
    id: 'docker-volumes',
    title: 'Dockerボリューム',
    description: 'データの永続化と共有',
    difficultyLevel: DifficultyLevel.INTERMEDIATE,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['docker-compose']
  },

  // 上級レベル (Advanced)
  {
    id: 'docker-best-practices',
    title: 'Dockerベストプラクティス',
    description: 'Docker利用の最適化とセキュリティ',
    difficultyLevel: DifficultyLevel.ADVANCED,
    isCompleted: false,
    isLocked: true,
    requiredTopics: ['docker-networks', 'docker-volumes']
  }
];

// 初期進行状態
const initialProgress: LearningProgress = {
  userId: 'guest',
  completedTopics: [],
  lastStudiedTopic: null,
  difficultyLevel: DifficultyLevel.BEGINNER,
  completedChallenges: [],
  badges: [],
  language: 'ja'
};

// プロバイダーコンポーネント
export const DockerLearningProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  // 状態管理
  const [topics, setTopics] = useState<LearningTopic[]>(initialTopics);
  const [progress, setProgress] = useState<LearningProgress>(initialProgress);
  const [currentTopicId, setCurrentTopicId] = useState<string | null>('docker-intro');
  const [educationalMode, setEducationalMode] = useState(true);
  const [educationalTipsEnabled, setEducationalTipsEnabled] = useState(true);
  
  // LocalStorageからの状態復元
  useEffect(() => {
    const savedProgress = localStorage.getItem('docker-learning-progress');
    if (savedProgress) {
      try {
        const parsedProgress = JSON.parse(savedProgress);
        setProgress(parsedProgress);
        
        // トピックのロック状態を更新
        updateTopicsLockStatus(parsedProgress.completedTopics);
      } catch (error) {
        console.error('Failed to parse saved progress', error);
      }
    }
    
    // 学習設定の復元
    const savedEducationalMode = localStorage.getItem('docker-educational-mode');
    if (savedEducationalMode) {
      setEducationalMode(savedEducationalMode === 'true');
    }
    
    const savedTipsEnabled = localStorage.getItem('docker-tips-enabled');
    if (savedTipsEnabled) {
      setEducationalTipsEnabled(savedTipsEnabled === 'true');
    }
  }, []);
  
  // 状態変更時にLocalStorageに保存
  useEffect(() => {
    localStorage.setItem('docker-learning-progress', JSON.stringify(progress));
  }, [progress]);
  
  useEffect(() => {
    localStorage.setItem('docker-educational-mode', educationalMode.toString());
  }, [educationalMode]);
  
  useEffect(() => {
    localStorage.setItem('docker-tips-enabled', educationalTipsEnabled.toString());
  }, [educationalTipsEnabled]);
  
  // トピックのロック状態を更新
  const updateTopicsLockStatus = (completedTopicIds: string[]) => {
    setTopics(prevTopics => {
      return prevTopics.map(topic => {
        // 基本的にレベルに基づいたロック状態を設定
        let isLocked = topic.difficultyLevel > progress.difficultyLevel;
        
        // 必要なトピックが完了していない場合はロック
        if (topic.requiredTopics && topic.requiredTopics.length > 0) {
          const allRequiredCompleted = topic.requiredTopics.every(
            requiredId => completedTopicIds.includes(requiredId)
          );
          isLocked = isLocked || !allRequiredCompleted;
        }
        
        return {
          ...topic,
          isCompleted: completedTopicIds.includes(topic.id),
          isLocked: isLocked
        };
      });
    });
  };
  
  // 現在のトピックを設定
  const setCurrentTopic = (topicId: string) => {
    const topic = topics.find(t => t.id === topicId);
    if (topic && !topic.isLocked) {
      setCurrentTopicId(topicId);
      setProgress(prev => ({
        ...prev,
        lastStudiedTopic: topicId
      }));
    }
  };
  
  // 現在のトピックを完了としてマーク
  const completeCurrentTopic = () => {
    if (currentTopicId) {
      completeTopic(currentTopicId);
    }
  };
  
  // 指定したトピックを完了としてマーク
  const completeTopic = (topicId: string) => {
    if (!progress.completedTopics.includes(topicId)) {
      const newCompletedTopics = [...progress.completedTopics, topicId];
      
      setProgress(prev => ({
        ...prev,
        completedTopics: newCompletedTopics
      }));
      
      // トピックのロック状態を更新
      updateTopicsLockStatus(newCompletedTopics);
      
      // バッジの更新
      checkAndUpdateBadges(newCompletedTopics);
    }
  };
  
  // チャレンジを完了としてマーク
  const completeChallenge = (challengeId: string) => {
    if (!progress.completedChallenges.includes(challengeId)) {
      const newCompletedChallenges = [...progress.completedChallenges, challengeId];
      
      setProgress(prev => ({
        ...prev,
        completedChallenges: newCompletedChallenges
      }));
      
      // バッジの更新
      checkAndUpdateBadges(progress.completedTopics, newCompletedChallenges);
    }
  };
  
  // バッジの条件チェックと更新
  const checkAndUpdateBadges = (completedTopics: string[] = progress.completedTopics, completedChallenges: string[] = progress.completedChallenges) => {
    const newBadges = [...progress.badges];
    
    // 初心者レベルのバッジ
    if (completedTopics.includes('docker-intro') && 
        completedTopics.includes('container-vs-vm') && 
        !newBadges.includes('beginner-scholar')) {
      newBadges.push('beginner-scholar');
    }
    
    // コマンド達成バッジ
    if (completedChallenges.length >= 3 && !newBadges.includes('command-novice')) {
      newBadges.push('command-novice');
    }
    
    // 中級者バッジ
    if (completedTopics.includes('docker-compose') && 
        completedTopics.includes('docker-networks') &&
        !newBadges.includes('docker-architect')) {
      newBadges.push('docker-architect');
    }
    
    // バッジが増えた場合のみ更新
    if (newBadges.length > progress.badges.length) {
      setProgress(prev => ({
        ...prev,
        badges: newBadges
      }));
    }
  };
  
  // 次に推奨するトピックを取得
  const getNextRecommendedTopic = (): string | null => {
    // まだ完了していないロックされていないトピックを探す
    const nextTopic = topics.find(topic => 
      !topic.isCompleted && !topic.isLocked && 
      topic.difficultyLevel <= progress.difficultyLevel
    );
    
    return nextTopic ? nextTopic.id : null;
  };
  
  // 難易度レベル設定
  const setDifficultyLevel = (level: DifficultyLevel) => {
    setProgress(prev => ({
      ...prev,
      difficultyLevel: level
    }));
    
    // トピックのロック状態を更新
    updateTopicsLockStatus(progress.completedTopics);
  };
  
  // 教育モード切り替え
  const toggleEducationalMode = () => {
    setEducationalMode(prev => !prev);
  };
  
  // 教育用ヒント表示切り替え
  const toggleEducationalTips = () => {
    setEducationalTipsEnabled(prev => !prev);
  };
  
  // 言語設定
  const setLanguage = (language: 'ja' | 'en') => {
    setProgress(prev => ({
      ...prev,
      language
    }));
  };
  
  // 進捗リセット
  const resetProgress = () => {
    setProgress(initialProgress);
    updateTopicsLockStatus([]);
    setCurrentTopicId('docker-intro');
  };
  
  // コンテキスト値
  const contextValue: DockerLearningContextType = {
    topics,
    currentTopicId,
    progress,
    educationalMode,
    educationalTipsEnabled,
    
    setCurrentTopic,
    completeCurrentTopic,
    completeTopic,
    completeChallenge,
    getNextRecommendedTopic,
    setDifficultyLevel,
    toggleEducationalMode,
    toggleEducationalTips,
    setLanguage,
    resetProgress
  };
  
  return (
    <DockerLearningContext.Provider value={contextValue}>
      {children}
    </DockerLearningContext.Provider>
  );
};

// カスタムフック
export const useDockerLearning = () => useContext(DockerLearningContext);

export default DockerLearningContext;