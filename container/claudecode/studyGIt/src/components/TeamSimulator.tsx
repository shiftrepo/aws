"use client";

import { useState, useEffect } from 'react';
import styles from './TeamSimulator.module.css';

interface TeamMember {
  id: number;
  name: string;
  avatar: string;
  activity: string;
}

interface Commit {
  id: string;
  message: string;
  author: string;
  timestamp: string;
  branch: string;
  files: Record<string, string>;
}

interface Repository {
  files: Record<string, string>;
  commits: Commit[];
  branches: string[];
  currentBranch: string;
}

interface TeamSimulatorProps {
  members: TeamMember[];
  repository: Repository;
  username: string;
}

export default function TeamSimulator({ members, repository, username }: TeamSimulatorProps) {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>(members);
  const [messages, setMessages] = useState<{ id: number; sender: string; content: string; timestamp: Date }[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [sharedContent, setSharedContent] = useState<string>('');
  const [conflictMode, setConflictMode] = useState(false);
  
  // チームメンバーのアクティビティをランダムに更新
  useEffect(() => {
    const activities = ['コード中', 'コミット中', 'マージ中', '休憩中', 'プルリクエスト作成中'];
    
    const interval = setInterval(() => {
      setTeamMembers(prev => 
        prev.map(member => ({
          ...member,
          activity: Math.random() > 0.7 ? activities[Math.floor(Math.random() * activities.length)] : member.activity
        }))
      );
    }, 8000);
    
    return () => clearInterval(interval);
  }, []);
  
  // チームメンバーからの自動メッセージ
  useEffect(() => {
    const memberMessages = [
      'このファイルを修正してプッシュしておきました',
      'マージしてもらえますか？',
      'プルリクエストをレビューしてください',
      'コンフリクトが発生しました...',
      'どのブランチで作業すればいいですか？',
      'いまmainブランチをプルしました',
      'そのファイル触っちゃダメ！今作業中だよ～',
    ];
    
    const interval = setInterval(() => {
      if (Math.random() > 0.5 || messages.length === 0) {
        const randomMember = teamMembers[Math.floor(Math.random() * teamMembers.length)];
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: randomMember.name,
          content: memberMessages[Math.floor(Math.random() * memberMessages.length)],
          timestamp: new Date()
        }]);
      }
    }, 15000);
    
    return () => clearInterval(interval);
  }, [teamMembers, messages]);
  
  // 競合シミュレーションの開始
  const startConflictSimulation = () => {
    if (!selectedFile || !repository.files[selectedFile]) return;
    
    setConflictMode(true);
    setSharedContent(repository.files[selectedFile]);
    
    // メンバーからのメッセージ
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: teamMembers[0].name,
      content: `あ、${selectedFile}ファイルに変更を加えました！コミットしておいてね！`,
      timestamp: new Date()
    }]);
    
    // 3秒後にメンバーが変更
    setTimeout(() => {
      if (!selectedFile) return;
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'システム',
        content: `${teamMembers[0].name}が${selectedFile}を変更しました。コンフリクトが発生する可能性があります。`,
        timestamp: new Date()
      }]);
      
      const lines = sharedContent.split('\n');
      if (lines.length > 2) {
        // ファイルの3行目を変更
        lines[2] = `// ${teamMembers[0].name}による変更: ${new Date().toLocaleString()}`;
        setSharedContent(lines.join('\n'));
      } else {
        // ファイルに行を追加
        setSharedContent(sharedContent + `\n// ${teamMembers[0].name}による変更: ${new Date().toLocaleString()}`);
      }
    }, 3000);
  };
  
  // メッセージ送信
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;
    
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: username,
      content: newMessage,
      timestamp: new Date()
    }]);
    
    setNewMessage('');
  };
  
  // シミュレーションの解決
  const resolveConflict = () => {
    if (!selectedFile) return;
    
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: 'システム',
      content: 'コンフリクトが解決されました！',
      timestamp: new Date()
    }]);
    
    setConflictMode(false);
    setSelectedFile(null);
  };
  
  return (
    <div className={styles.teamSimulator}>
      <div className={styles.members}>
        <h2>チームメンバー</h2>
        <div className={styles.memberList}>
          {teamMembers.map((member) => (
            <div key={member.id} className={styles.member}>
              <div className={styles.avatar}>{member.avatar}</div>
              <div className={styles.memberInfo}>
                <div className={styles.name}>{member.name}</div>
                <div className={styles.activity}>{member.activity}</div>
              </div>
            </div>
          ))}
          <div className={styles.member}>
            <div className={styles.avatar}>👤</div>
            <div className={styles.memberInfo}>
              <div className={styles.name}>{username}</div>
              <div className={styles.activity}>オンライン</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className={styles.chat}>
        <h2>チャット</h2>
        <div className={styles.messages}>
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`${styles.message} ${message.sender === username ? styles.ownMessage : ''}`}
            >
              <div className={styles.messageSender}>{message.sender}</div>
              <div className={styles.messageContent}>{message.content}</div>
              <div className={styles.messageTime}>
                {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </div>
            </div>
          ))}
        </div>
        <form className={styles.messageForm} onSubmit={handleSendMessage}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="メッセージを入力..."
            className={styles.messageInput}
          />
          <button type="submit" className={styles.sendButton}>送信</button>
        </form>
      </div>
      
      <div className={styles.simulator}>
        <h2>コンフリクトシミュレーション</h2>
        <p>チームでの作業によって発生する競合を体験します。</p>
        
        {!conflictMode && !selectedFile && (
          <div className={styles.fileSelection}>
            <h3>ファイルを選択</h3>
            <div className={styles.fileList}>
              {Object.keys(repository.files).length === 0 ? (
                <p className={styles.emptyState}>まだファイルがありません。「ファイル操作」タブでファイルを作成してください。</p>
              ) : (
                Object.keys(repository.files).map((fileName) => (
                  <div 
                    key={fileName}
                    className={styles.fileItem}
                    onClick={() => setSelectedFile(fileName)}
                  >
                    {fileName}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
        
        {selectedFile && !conflictMode && (
          <div className={styles.conflictSetup}>
            <h3>{selectedFile}</h3>
            <p>このファイルを使用してコンフリクトの発生をシミュレーションしますか？</p>
            <p>（あなたとチームメンバーが同じファイルを同時に編集する状況を再現します）</p>
            <button 
              className={styles.simulateButton}
              onClick={startConflictSimulation}
            >
              シミュレーションを開始
            </button>
            <button 
              className={styles.cancelButton}
              onClick={() => setSelectedFile(null)}
            >
              キャンセル
            </button>
          </div>
        )}
        
        {conflictMode && selectedFile && (
          <div className={styles.conflictView}>
            <h3>コンフリクト発生！</h3>
            <p>チームメンバーが同じファイルを編集しました。現在の内容:</p>
            
            <div className={styles.codeEditor}>
              <pre>{sharedContent}</pre>
            </div>
            
            <div className={styles.conflictResolution}>
              <p>コンフリクトを解決するには:</p>
              <ol>
                <li>チームメンバーと相談</li>
                <li>どちらの変更を採用するか決定</li>
                <li>変更をマージ</li>
                <li>コミットを作成</li>
              </ol>
              
              <button 
                className={styles.resolveButton}
                onClick={resolveConflict}
              >
                コンフリクトを解決
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}