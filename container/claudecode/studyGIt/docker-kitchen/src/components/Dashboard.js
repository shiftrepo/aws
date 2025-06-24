import React from 'react';
import './Dashboard.css';

// リソース可視化ダッシュボードコンポーネント (worker2 担当)
const Dashboard = ({ resourceData, containers, onContainerSelect }) => {
  // 実行中のコンテナ数を計算
  const runningContainers = containers.filter(container => container.status === 'running').length;
  
  return (
    <div className="dashboard">
      <h2>リソース可視化ダッシュボード</h2>
      
      <div className="dashboard-content">
        {/* リソース使用量の表示 */}
        <div className="resource-usage">
          <h3>リソース使用量</h3>
          
          <div className="resource-bar">
            <span className="resource-label">CPU:</span>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${resourceData.cpu}%`}}></div>
            </div>
            <span className="resource-value">{resourceData.cpu}%</span>
          </div>
          
          <div className="resource-bar">
            <span className="resource-label">メモリ:</span>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${resourceData.memory}%`}}></div>
            </div>
            <span className="resource-value">{resourceData.memory}%</span>
          </div>
          
          <div className="resource-bar">
            <span className="resource-label">ディスク:</span>
            <div className="progress-bar">
              <div className="progress-fill" style={{width: `${resourceData.disk}%`}}></div>
            </div>
            <span className="resource-value">{resourceData.disk}%</span>
          </div>
        </div>
        
        {/* アクティブコンテナリストの表示 */}
        <div className="container-list">
          <h3>アクティブコンテナ</h3>
          <ul>
            {containers.map(container => (
              <li
                key={container.id}
                className={`container-item ${container.status}`}
                onClick={() => onContainerSelect(container.id)}
              >
                <span className="status-icon">
                  {container.status === 'running' ? '✅' : '⏹'}
                </span>
                <span className="container-name">{container.name}</span>
                <span className="container-status">({container.status === 'running' ? '実行中' : '停止中'})</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* コンテナvs VM比較 */}
      <div className="comparison-section">
        <h3>コンテナ vs VM 比較</h3>
        <table className="comparison-table">
          <thead>
            <tr>
              <th>項目</th>
              <th>コンテナ (フードトラック)</th>
              <th>VM (レストラン)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>起動時間</td>
              <td>1秒</td>
              <td>30-60秒</td>
            </tr>
            <tr>
              <td>メモリ消費</td>
              <td>50MB</td>
              <td>500MB+</td>
            </tr>
            <tr>
              <td>イメージサイズ</td>
              <td>100MB</td>
              <td>10GB+</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div className="container-stats">
        <p>コンテナ統計: {runningContainers}実行中 / {containers.length - runningContainers}停止中 / 合計{containers.length}</p>
      </div>
    </div>
  );
};

export default Dashboard;