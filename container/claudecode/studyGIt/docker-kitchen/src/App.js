import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import DockerfileBuilder from './components/DockerfileBuilder';
import ContainerManager from './components/ContainerManager';

// Docker Kitchenのメインアプリケーションコンポーネント
function App() {
  // 現在のアクティブタブを管理するステート
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // 選択されたコンテナのIDを管理するステート
  const [selectedContainerId, setSelectedContainerId] = useState(null);
  
  // リソース使用量のモックデータ
  const [resourceData, setResourceData] = useState({
    cpu: 60,
    memory: 70,
    disk: 30
  });

  // コンテナのモックデータ
  const [containers, setContainers] = useState([
    { id: 'nginx-app', name: 'nginx-app', status: 'running', image: 'nginx:latest', cpu: 15, memory: 50 },
    { id: 'redis-cache', name: 'redis-cache', status: 'stopped', image: 'redis:alpine', cpu: 0, memory: 0 },
    { id: 'mysql-db', name: 'mysql-db', status: 'running', image: 'mysql:5.7', cpu: 35, memory: 400 }
  ]);

  // 起動・停止アクションのハンドラー
  const handleContainerAction = (containerId, action) => {
    const updatedContainers = containers.map(container => {
      if (container.id === containerId) {
        if (action === 'start') {
          return { ...container, status: 'running', cpu: 15, memory: container.id.includes('redis') ? 30 : 50 };
        } else if (action === 'stop') {
          return { ...container, status: 'stopped', cpu: 0, memory: 0 };
        }
      }
      return container;
    });
    setContainers(updatedContainers);
  };

  // タブ切り替えハンドラー
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // コンテナ選択ハンドラー（イベント連携の例）
  const handleContainerSelect = (containerId) => {
    setSelectedContainerId(containerId);
    // ダッシュボードからコンテナ管理タブへの自動切り替え（オプション）
    // setActiveTab('container');
  };

  // Dockerfileビルダーからの生成イベントハンドラー
  const handleDockerfileGenerate = (dockerfile) => {
    console.log("Generated Dockerfile:", dockerfile);
    // 実際の実装では、このイベントを他のコンポーネントにも通知する
  };

  return (
    <div className="docker-kitchen">
      <header className="app-header">
        <h1>Docker Kitchen - コンテナ技術を料理で学ぶ</h1>
        <nav className="main-nav">
          <ul>
            <li className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => handleTabChange('dashboard')}>
              ダッシュボード
            </li>
            <li className={activeTab === 'dockerfile' ? 'active' : ''} onClick={() => handleTabChange('dockerfile')}>
              Dockerfileビルダー
            </li>
            <li className={activeTab === 'container' ? 'active' : ''} onClick={() => handleTabChange('container')}>
              コンテナ管理
            </li>
          </ul>
        </nav>
      </header>
      
      <main className="app-content">
        {/* タブに応じてコンポーネントを条件付きレンダリング */}
        {activeTab === 'dashboard' && (
          <Dashboard 
            resourceData={resourceData} 
            containers={containers} 
            onContainerSelect={handleContainerSelect}
          />
        )}
        
        {activeTab === 'dockerfile' && (
          <DockerfileBuilder 
            onGenerate={handleDockerfileGenerate} 
          />
        )}
        
        {activeTab === 'container' && (
          <ContainerManager 
            containers={containers}
            selectedContainerId={selectedContainerId}
            onContainerAction={handleContainerAction}
          />
        )}
      </main>
      
      <footer className="app-footer">
        <p>Docker Kitchen プロトタイプ - ©2025 Cooking with Containers Project</p>
      </footer>
    </div>
  );
}

export default App;