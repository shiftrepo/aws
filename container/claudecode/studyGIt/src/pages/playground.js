import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DEFAULT_FILES from '../components/DefaultFiles';
import FileExplorer from '../components/FileExplorer';
import GitVisualizer from '../components/GitVisualizer';
import CommandTerminal from '../components/CommandTerminal';
import TeamSimulator from '../components/TeamSimulator';
import GitFlowGuide from '../components/GitFlowGuide';
import TeamGitFlow from '../components/TeamGitFlow';
import styles from './playground.module.css';

export default function Playground() {
  const router = useRouter();
  const { username } = router.query;
  const [activeTab, setActiveTab] = useState('files');
  const [gitFlowView, setGitFlowView] = useState('standard');
  
  // 初期コミット状態で開始するためのリポジトリ設定
  const [repository, setRepository] = useState({
    files: DEFAULT_FILES,
    commits: [
      {
        id: `commit-${Date.now()-10000}`,
        message: '初期ファイルのコミット',
        author: 'System',
        timestamp: new Date(Date.now()-10000).toISOString(),
        branch: 'main',
        files: DEFAULT_FILES,
        hasConflict: false,
        resolvedConflict: false,
      }
    ],
    branches: ['main', 'feature-branch'],
    currentBranch: 'main',
  });
  
  const [teamMembers, setTeamMembers] = useState([
    { id: 1, name: '田中さん', avatar: '👩‍💻', activity: '休憩中' },
    { id: 2, name: '鈴木さん', avatar: '👨‍💻', activity: 'コード中' },
  ]);
  
  const [tutorial, setTutorial] = useState({
    active: true,
    step: 0,
    steps: [
      'GitPlaygroundへようこそ！このサイトでは、実際のGit操作を体験できます。',
      'まずは、ファイルを作成してみましょう。「ファイル操作」タブをクリックしてください。',
      'ファイル名と内容を入力して「作成」ボタンをクリックすると、ファイルが作成されます。',
      '作成したファイルが表示されました。これでファイルの追加方法を学びました！',
      '次は、作成したファイルを変更してみましょう。ファイルをクリックして編集しましょう。',
      '変更が完了したら「コミット」タブに移動して、変更をコミットしましょう。',
    ],
  });
  
  const [conflictInfo, setConflictInfo] = useState({
    active: false,
    resolved: false,
    file: null,
  });
  
  const handleFileOperation = (operation, data) => {
    // ファイル操作の処理（追加、変更、削除）
    let updatedFiles = { ...repository.files };
    
    switch (operation) {
      case 'add':
        updatedFiles[data.name] = data.content;
        break;
      case 'modify':
        updatedFiles[data.name] = data.content;
        break;
      case 'delete':
        delete updatedFiles[data.name];
        break;
      default:
        break;
    }
    
    setRepository(prev => ({
      ...prev,
      files: updatedFiles,
    }));
    
    // チュートリアルの進行
    if (tutorial.active && 
        ((operation === 'add' && tutorial.step === 2) || 
         (operation === 'modify' && tutorial.step === 4))) {
      setTutorial(prev => ({ ...prev, step: prev.step + 1 }));
    }
  };
  
  const handleCommit = (message) => {
    const newCommit = {
      id: `commit-${Date.now()}`,
      message,
      author: username || 'ユーザー',
      timestamp: new Date().toISOString(),
      branch: repository.currentBranch,
      files: { ...repository.files },
      hasConflict: conflictInfo.active && !conflictInfo.resolved,
      resolvedConflict: conflictInfo.resolved,
    };
    
    setRepository(prev => ({
      ...prev,
      commits: [...prev.commits, newCommit],
    }));
    
    // コンフリクト情報をリセット
    if (conflictInfo.resolved) {
      setConflictInfo({
        active: false,
        resolved: false,
        file: null
      });
    }
    
    // チュートリアルの進行
    if (tutorial.active && tutorial.step === 5) {
      setTutorial(prev => ({ ...prev, step: prev.step + 1 }));
    }
  };
  
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // チュートリアルの進行
    if (tutorial.active && tab === 'files' && tutorial.step === 1) {
      setTutorial(prev => ({ ...prev, step: prev.step + 1 }));
    } else if (tutorial.active && tab === 'commit' && tutorial.step === 5) {
      // コミットタブに移動した時の処理
    }
  };
  
  if (!router.isReady) {
    return <div className={styles.playground}>Loading...</div>;
  }
  
  return (
    <div className={styles.playground}>
      <header className={styles.header}>
        <h1>GitPlayground</h1>
        <div className={styles.userInfo}>
          <span className={styles.avatar}>👤</span>
          <span>{username || 'ユーザー'}</span>
        </div>
      </header>
      
      {tutorial.active && (
        <div className={styles.tutorial}>
          <div className={styles.tutorialContent}>
            <h3>チュートリアル</h3>
            <p>{tutorial.steps[tutorial.step]}</p>
            {tutorial.step === tutorial.steps.length - 1 && (
              <button 
                onClick={() => setTutorial(prev => ({ ...prev, active: false }))}
                className={styles.tutorialButton}
              >
                チュートリアルを終了
              </button>
            )}
          </div>
          <div className={styles.progress}>
            {tutorial.steps.map((_, idx) => (
              <div 
                key={idx} 
                className={`${styles.progressDot} ${idx <= tutorial.step ? styles.active : ''}`}
              />
            ))}
          </div>
        </div>
      )}
      
      <div className={styles.tabs}>
        <button 
          className={`${styles.tab} ${activeTab === 'files' ? styles.active : ''}`}
          onClick={() => handleTabChange('files')}
        >
          ファイル操作
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'commit' ? styles.active : ''}`}
          onClick={() => handleTabChange('commit')}
        >
          コミット
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'team' ? styles.active : ''}`}
          onClick={() => handleTabChange('team')}
        >
          チーム
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'visualize' ? styles.active : ''}`}
          onClick={() => handleTabChange('visualize')}
        >
          可視化
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'gitflow' ? styles.active : ''}`}
          onClick={() => handleTabChange('gitflow')}
        >
          Git Flow
        </button>
      </div>
      
      <div className={styles.content}>
        {activeTab === 'files' && (
          <FileExplorer 
            files={repository.files}
            onFileOperation={handleFileOperation}
          />
        )}
        
        {activeTab === 'commit' && (
          <CommandTerminal 
            repository={repository}
            onCommit={handleCommit}
          />
        )}
        
        {activeTab === 'team' && (
          <TeamSimulator 
            members={teamMembers}
            repository={repository}
            username={username || 'ユーザー'}
            onConflictStateChange={(conflictState) => {
              setConflictInfo(conflictState);
            }}
          />
        )}
        
        {activeTab === 'visualize' && (
          <GitVisualizer 
            repository={repository}
          />
        )}
        
        {activeTab === 'gitflow' && (
          <div className={styles.gitFlowSelector}>
            <div className={styles.viewOptions}>
              <button 
                className={`${styles.viewOption} ${gitFlowView === 'standard' ? styles.active : ''}`}
                onClick={() => setGitFlowView('standard')}
              >
                標準 Git Flow
              </button>
              <button 
                className={`${styles.viewOption} ${gitFlowView === 'team' ? styles.active : ''}`}
                onClick={() => setGitFlowView('team')}
              >
                チーム Git Flow
              </button>
            </div>
            {gitFlowView === 'standard' ? <GitFlowGuide /> : <TeamGitFlow />}
          </div>
        )}
      </div>
    </div>
  );
}