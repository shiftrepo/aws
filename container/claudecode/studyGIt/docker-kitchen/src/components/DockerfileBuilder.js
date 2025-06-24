import React, { useState } from 'react';
import './DockerfileBuilder.css';

// Dockerfileビルダーコンポーネント (worker1 担当)
const DockerfileBuilder = ({ onGenerate }) => {
  // 選択可能なベースイメージのリスト
  const baseImages = [
    'ubuntu:20.04',
    'alpine:latest',
    'node:14',
    'python:3.9',
    'nginx:latest'
  ];
  
  // 選択可能なDockerコマンドのリスト
  const dockerCommands = [
    'RUN',
    'COPY',
    'ADD',
    'ENV',
    'EXPOSE',
    'CMD',
    'WORKDIR'
  ];
  
  // 各コマンドに対応する一般的なコマンド例
  const commandExamples = {
    'RUN': [
      'apt-get update && apt-get install -y nginx',
      'pip install -r requirements.txt',
      'npm install',
      'mkdir -p /app/data'
    ],
    'COPY': [
      './app /var/www/html',
      'package.json /app/',
      './src /app/src',
      './config.json /etc/myapp/'
    ],
    'ADD': [
      'https://example.com/file.tar.gz /app/',
      './files /destination',
      './package.json /app/'
    ],
    'ENV': [
      'NODE_ENV=production',
      'PATH=/usr/local/bin:$PATH',
      'DEBUG=false',
      'APP_HOME=/var/www'
    ],
    'EXPOSE': [
      '80',
      '8080',
      '3000',
      '443'
    ],
    'CMD': [
      '["nginx", "-g", "daemon off;"]',
      '["npm", "start"]',
      '["python", "app.py"]',
      '["java", "-jar", "app.jar"]'
    ],
    'WORKDIR': [
      '/app',
      '/var/www',
      '/usr/src/app',
      '/home/node/app'
    ]
  };
  
  // ステート管理
  const [baseImage, setBaseImage] = useState(baseImages[0]);
  const [dockerfile, setDockerfile] = useState([
    { command: 'FROM', value: baseImages[0] }
  ]);
  const [selectedCommand, setSelectedCommand] = useState(dockerCommands[0]);
  const [commandValue, setCommandValue] = useState(commandExamples[dockerCommands[0]][0]);
  
  // ベースイメージ変更ハンドラー
  const handleBaseImageChange = (e) => {
    const newBaseImage = e.target.value;
    setBaseImage(newBaseImage);
    
    // Dockerfileの最初の行（FROM命令）を更新
    const newDockerfile = [...dockerfile];
    newDockerfile[0] = { command: 'FROM', value: newBaseImage };
    setDockerfile(newDockerfile);
  };
  
  // コマンド変更ハンドラー
  const handleCommandChange = (e) => {
    const newCommand = e.target.value;
    setSelectedCommand(newCommand);
    setCommandValue(commandExamples[newCommand][0]);
  };
  
  // コマンド値変更ハンドラー
  const handleCommandValueChange = (e) => {
    setCommandValue(e.target.value);
  };
  
  // コマンド追加ハンドラー
  const handleAddCommand = () => {
    const newDockerfile = [...dockerfile, { command: selectedCommand, value: commandValue }];
    setDockerfile(newDockerfile);
  };
  
  // Dockerfile生成ハンドラー
  const handleGenerate = () => {
    const generatedDockerfile = dockerfile
      .map(item => `${item.command} ${item.value}`)
      .join('\n');
    
    onGenerate(generatedDockerfile);
  };
  
  // Dockerfileクリアハンドラー
  const handleClear = () => {
    setDockerfile([{ command: 'FROM', value: baseImage }]);
  };
  
  return (
    <div className="dockerfile-builder">
      <h2>Dockerfileビルダー</h2>
      
      <div className="builder-content">
        <div className="base-image-selector">
          <label htmlFor="base-image">ベースイメージ:</label>
          <select
            id="base-image"
            value={baseImage}
            onChange={handleBaseImageChange}
          >
            {baseImages.map(image => (
              <option key={image} value={image}>{image}</option>
            ))}
          </select>
        </div>
        
        <div className="command-adder">
          <h3>コマンド追加:</h3>
          <div className="command-inputs">
            <select
              value={selectedCommand}
              onChange={handleCommandChange}
            >
              {dockerCommands.map(command => (
                <option key={command} value={command}>{command}</option>
              ))}
            </select>
            
            <select
              value={commandValue}
              onChange={handleCommandValueChange}
            >
              {commandExamples[selectedCommand].map(example => (
                <option key={example} value={example}>{example}</option>
              ))}
            </select>
            
            <button onClick={handleAddCommand}>追加</button>
          </div>
        </div>
        
        <div className="dockerfile-preview">
          <h3>Dockerfile プレビュー:</h3>
          <pre className="preview-content">
            {dockerfile.map((item, index) => (
              <code key={index}>{item.command} {item.value}</code>
            ))}
          </pre>
        </div>
        
        <div className="builder-actions">
          <button onClick={handleClear}>クリア</button>
          <button onClick={() => navigator.clipboard.writeText(
            dockerfile.map(item => `${item.command} ${item.value}`).join('\n')
          )}>コピー</button>
          <button onClick={handleGenerate}>生成</button>
        </div>
      </div>
      
      <div className="tutorial-section">
        <h3>Dockerfile 基本ガイド:</h3>
        <ul>
          <li><strong>FROM</strong>: ベースイメージを指定します（例: ubuntu:20.04）</li>
          <li><strong>RUN</strong>: コマンドを実行します（例: apt-get install -y nginx）</li>
          <li><strong>COPY</strong>: ファイルをコンテナにコピーします（例: ./app /var/www/html）</li>
          <li><strong>EXPOSE</strong>: コンテナがリッスンするポートを指定します（例: 80）</li>
          <li><strong>CMD</strong>: コンテナ起動時のデフォルトコマンドを指定します（例: ["nginx", "-g", "daemon off;"]）</li>
        </ul>
      </div>
    </div>
  );
};

export default DockerfileBuilder;