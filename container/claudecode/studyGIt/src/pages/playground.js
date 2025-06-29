import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DEFAULT_FILES from '../components/DefaultFiles';
import FileExplorer from '../components/FileExplorer';
import GitVisualizer from '../components/GitVisualizer';
import CommandTerminal from '../components/CommandTerminal';
import TeamSimulator from '../components/TeamSimulator';
import GitFlowGuide from '../components/GitFlowGuide';
import TeamGitFlow from '../components/TeamGitFlow';

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
  
  // スタイル
  const containerStyle = {
    fontFamily: 'Arial, sans-serif',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '1rem'
  };
  
  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
    padding: '0.5rem',
    backgroundColor: '#f0f0f0',
    borderRadius: '8px'
  };
  
  const tutorialStyle = {
    backgroundColor: '#e6f7ff',
    border: '1px solid #91d5ff',
    borderRadius: '8px',
    padding: '1rem',
    marginBottom: '1rem'
  };
  
  const progressStyle = {
    display: 'flex',
    justifyContent: 'center',
    marginTop: '0.5rem'
  };
  
  const progressDotStyle = {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    backgroundColor: '#d9d9d9',
    margin: '0 5px'
  };
  
  const activeDotStyle = {
    ...progressDotStyle,
    backgroundColor: '#1890ff'
  };
  
  const tabsStyle = {
    display: 'flex',
    marginBottom: '1rem',
    borderBottom: '1px solid #d9d9d9'
  };
  
  const tabStyle = {
    padding: '0.5rem 1rem',
    cursor: 'pointer',
    backgroundColor: '#f9f9f9',
    border: '1px solid #d9d9d9',
    borderBottom: 'none',
    borderRadius: '4px 4px 0 0',
    marginRight: '0.5rem'
  };
  
  const activeTabStyle = {
    ...tabStyle,
    backgroundColor: '#fff',
    borderBottom: '1px solid #fff',
    marginBottom: '-1px',
    fontWeight: 'bold'
  };
  
  const contentStyle = {
    border: '1px solid #d9d9d9',
    borderRadius: '0 4px 4px 4px',
    padding: '1rem',
    minHeight: '500px'
  };
  
  if (!router.isReady) {
    return <div style={containerStyle}>Loading...</div>;
  }
  
  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <h1>GitPlayground</h1>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ marginRight: '0.5rem' }}>👤</span>
          <span>{username || 'ユーザー'}</span>
        </div>
      </header>
      
      {tutorial.active && (
        <div style={tutorialStyle}>
          <div>
            <h3>チュートリアル</h3>
            <p>{tutorial.steps[tutorial.step]}</p>
            {tutorial.step === tutorial.steps.length - 1 && (
              <button 
                onClick={() => setTutorial(prev => ({ ...prev, active: false }))}
                style={{
                  backgroundColor: '#1890ff',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                チュートリアルを終了
              </button>
            )}
          </div>
          <div style={progressStyle}>
            {tutorial.steps.map((_, idx) => (
              <div 
                key={idx} 
                style={idx <= tutorial.step ? activeDotStyle : progressDotStyle}
              />
            ))}
          </div>
        </div>
      )}
      
      <div style={tabsStyle}>
        <button 
          style={activeTab === 'files' ? activeTabStyle : tabStyle}
          onClick={() => handleTabChange('files')}
        >
          ファイル操作
        </button>
        <button 
          style={activeTab === 'commit' ? activeTabStyle : tabStyle}
          onClick={() => handleTabChange('commit')}
        >
          コミット
        </button>
        <button 
          style={activeTab === 'team' ? activeTabStyle : tabStyle}
          onClick={() => handleTabChange('team')}
        >
          チーム
        </button>
        <button 
          style={activeTab === 'visualize' ? activeTabStyle : tabStyle}
          onClick={() => handleTabChange('visualize')}
        >
          可視化
        </button>
        <button 
          style={activeTab === 'gitflow' ? activeTabStyle : tabStyle}
          onClick={() => handleTabChange('gitflow')}
        >
          Git Flow
        </button>
      </div>
      
      <div style={contentStyle}>
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
          <div>
            <div style={{ marginBottom: '1rem' }}>
              <button 
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: gitFlowView === 'standard' ? '#1890ff' : '#f0f0f0',
                  color: gitFlowView === 'standard' ? 'white' : 'black',
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px',
                  marginRight: '0.5rem',
                  cursor: 'pointer'
                }}
                onClick={() => setGitFlowView('standard')}
              >
                標準 Git Flow
              </button>
              <button 
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: gitFlowView === 'team' ? '#1890ff' : '#f0f0f0',
                  color: gitFlowView === 'team' ? 'white' : 'black',
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
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