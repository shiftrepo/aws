import React, { useState } from 'react';
import './ContainerManager.css';

// コンテナ管理シミュレーターコンポーネント (worker3 担当)
const ContainerManager = ({ containers, selectedContainerId, onContainerAction }) => {
  // 選択されているコンテナ情報を取得
  const selectedContainer = containers.find(container => container.id === selectedContainerId) || containers[0];
  
  // ログ情報のモックデータ
  const [containerLogs, setContainerLogs] = useState({
    'nginx-app': [
      '2025-06-24 05:58:32 Starting nginx...',
      '2025-06-24 05:58:33 nginx started successfully'
    ],
    'redis-cache': [
      '2025-06-24 05:57:12 Starting redis...',
      '2025-06-24 05:57:13 Redis server stopped'
    ],
    'mysql-db': [
      '2025-06-24 05:59:01 Starting MySQL...',
      '2025-06-24 05:59:05 MySQL database system is ready for connections'
    ]
  });

  // コンテナ選択ハンドラー
  const handleContainerSelect = (containerId) => {
    onContainerAction(containerId, 'select');
  };

  // コンテナアクションハンドラー
  const handleAction = (action) => {
    if (selectedContainer) {
      onContainerAction(selectedContainer.id, action);
      
      // ログにアクション記録を追加
      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
      const newLog = `${timestamp} ${action === 'start' ? 'Starting' : action === 'stop' ? 'Stopping' : 'Restarting'} ${selectedContainer.name}...`;
      
      setContainerLogs(prevLogs => ({
        ...prevLogs,
        [selectedContainer.id]: [newLog, ...(prevLogs[selectedContainer.id] || [])]
      }));
    }
  };

  return (
    <div className="container-manager">
      <h2>コンテナ管理シミュレーター</h2>
      
      <div className="container-manager-content">
        {/* コンテナ操作パネル */}
        <div className="container-operations">
          <h3>コンテナ操作</h3>
          <ul className="container-list">
            {containers.map(container => (
              <li 
                key={container.id}
                className={`container-item ${container.status} ${selectedContainer && container.id === selectedContainer.id ? 'selected' : ''}`}
                onClick={() => handleContainerSelect(container.id)}
              >
                <span className="status-icon">
                  {container.status === 'running' ? '✅' : '⏹'}
                </span>
                <span className="container-name">{container.name}</span>
              </li>
            ))}
          </ul>
          
          <button className="new-container-btn">新規作成</button>
        </div>
        
        {/* コンテナ詳細情報 */}
        {selectedContainer && (
          <div className="container-details">
            <h3>コンテナ詳細</h3>
            <div className="detail-item">
              <span className="detail-label">ID:</span>
              <span className="detail-value">{selectedContainer.id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">イメージ:</span>
              <span className="detail-value">{selectedContainer.image}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">ステータス:</span>
              <span className="detail-value">{selectedContainer.status === 'running' ? '実行中' : '停止中'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">CPU:</span>
              <span className="detail-value">{selectedContainer.cpu}%</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">メモリ:</span>
              <span className="detail-value">{selectedContainer.memory}MB</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">ポート:</span>
              <span className="detail-value">{selectedContainer.id === 'nginx-app' ? '80:80' : selectedContainer.id === 'redis-cache' ? '6379:6379' : '3306:3306'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">ネットワーク:</span>
              <span className="detail-value">bridge</span>
            </div>
          </div>
        )}
      </div>
      
      {/* アクションボタン */}
      <div className="action-buttons">
        <h3>アクション:</h3>
        <div className="button-group">
          <button 
            className="action-btn start" 
            onClick={() => handleAction('start')}
            disabled={selectedContainer && selectedContainer.status === 'running'}
          >
            起動
          </button>
          <button 
            className="action-btn stop" 
            onClick={() => handleAction('stop')}
            disabled={selectedContainer && selectedContainer.status === 'stopped'}
          >
            停止
          </button>
          <button 
            className="action-btn restart" 
            onClick={() => handleAction('restart')}
            disabled={selectedContainer && selectedContainer.status === 'stopped'}
          >
            再起動
          </button>
          <button className="action-btn delete">削除</button>
        </div>
      </div>
      
      {/* ログ表示 */}
      {selectedContainer && (
        <div className="container-logs">
          <h3>ログ表示:</h3>
          <div className="logs-content">
            {(containerLogs[selectedContainer.id] || []).map((log, index) => (
              <div key={index} className="log-line">{log}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContainerManager;