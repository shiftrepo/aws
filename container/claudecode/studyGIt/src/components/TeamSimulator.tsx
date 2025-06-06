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
  onConflictStateChange?: (conflictState: {active: boolean, resolved: boolean, file: string | null}) => void;
}

export default function TeamSimulator(props: TeamSimulatorProps) {
  const { members, repository, username } = props;
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>(members);
  const [messages, setMessages] = useState<{ id: number; sender: string; content: string; timestamp: Date }[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [sharedContent, setSharedContent] = useState<string>('');
  const [conflictMode, setConflictMode] = useState(false);
  const [resolutionStep, setResolutionStep] = useState(0);
  const [resolvedContent, setResolvedContent] = useState('');
  const [userEditableContent, setUserEditableContent] = useState('');
  const [teamMemberVersion, setTeamMemberVersion] = useState('');
  const [myVersion, setMyVersion] = useState('');
  const [conflictMarkers, setConflictMarkers] = useState(false);
  
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
    
    // 自分のバージョンを保存
    const myCurrentVersion = repository.files[selectedFile];
    setMyVersion(myCurrentVersion);
    
    setConflictMode(true);
    setSharedContent(myCurrentVersion);
    setUserEditableContent(myCurrentVersion);
    
    // コンフリクト状態を親コンポーネントに通知
    if (props.onConflictStateChange) {
      props.onConflictStateChange({
        active: true,
        resolved: false,
        file: selectedFile
      });
    }
    
    // メンバーからのメッセージ
    setMessages(prev => [...prev, {
      id: Date.now(),
      sender: teamMembers[0].name,
      content: `あ、${selectedFile}ファイルに変更を加えたから確認してください！`,
      timestamp: new Date()
    }]);
    
    // 3秒後にメンバーが変更
    setTimeout(() => {
      if (!selectedFile) return;
      
      // チームメンバーの変更を作成
      let teamVersion = '';
      const lines = myCurrentVersion.split('\n');
      
      if (lines.length > 2) {
        // ファイルの3行目を変更
        const modifiedLines = [...lines];
        modifiedLines[2] = `// ${teamMembers[0].name}による変更: 重要な機能を追加しました ${new Date().toLocaleString()}`;
        teamVersion = modifiedLines.join('\n');
      } else {
        // ファイルに行を追加
        teamVersion = myCurrentVersion + `\n// ${teamMembers[0].name}による変更: 重要な機能を追加しました ${new Date().toLocaleString()}`;
      }
      
      setTeamMemberVersion(teamVersion);
      
      // メッセージを表示
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: teamMembers[0].name,
        content: `あ、同じファイルを変更してた！プルしたらコンフリクトが発生するかも、確認してくれる?`,
        timestamp: new Date()
      }]);
      
      // 2秒後に自分も変更したことを伝える
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: username,
          content: `あれ、私もそのファイル修正してたんだけど...`,
          timestamp: new Date()
        }]);
      }, 2000);
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
  
  // 次のステップへ進む
  const nextResolutionStep = () => {
    if (!selectedFile) return;
    
    // 次の解決ステップに進む
    if (resolutionStep === 0) {
      // コンフリクトの表示
      setResolutionStep(1);
      setConflictMarkers(true);
      
      // コンフリクトを表現するマーカー付きの内容を生成
      const conflictContent = generateConflictContent();
      setUserEditableContent(conflictContent);
      
      // チームメンバーからのメッセージ
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: teamMembers[0].name,
        content: `あ、コンフリクトが発生してるね。私の変更と君の変更をマージする必要があるよ。渡したコンフリクトマーカーを編集して、必要な部分を残すか統合してくれる？`,
        timestamp: new Date()
      }]);
      
      // システムからのメッセージ
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'システム',
        content: 'コンフリクトが発生しました。<<<<<<< HEADから>>>>>>> feature-branchまでのマーカーの間にある内容を編集してコンフリクトを解決してください。',
        timestamp: new Date()
      }]);
    } 
    else if (resolutionStep === 1) {
      // ユーザーが編集した内容でコンフリクトを解決
      setResolutionStep(2);
      
      // コンフリクトマーカーがまだ残っていないかチェック
      if (userEditableContent.includes('<<<<<<<') || 
          userEditableContent.includes('=======') || 
          userEditableContent.includes('>>>>>>>')) {
        
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: 'システム',
          content: 'コンフリクトマーカー (<<<<<<<, =======, >>>>>>>) がまだ残っています。これらを全て削除してコンフリクトを解決してください。',
          timestamp: new Date()
        }]);
        
        setResolutionStep(1); // ステップを戻す
        return;
      }
      
      // 解決された内容を保存
      setResolvedContent(userEditableContent);
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: username,
        content: 'コンフリクトを解決しました。確認してもらえますか？',
        timestamp: new Date()
      }]);
      
      // チームメンバーからのメッセージ
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: teamMembers[0].name,
          content: 'うん、問題なさそうだね！コミットしてマージしてください！',
          timestamp: new Date()
        }]);
      }, 1500);
    } 
    else if (resolutionStep === 2) {
      // 全ステップ完了
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: 'システム',
        content: 'コンフリクトが解決されました。コミットを作成してマージを完了してください。',
        timestamp: new Date()
      }]);
      
      // コンフリクト解決状態を親コンポーネントに通知
      if (props.onConflictStateChange && selectedFile) {
        props.onConflictStateChange({
          active: true,
          resolved: true,
          file: selectedFile
        });
      }
      
      // 数秒後にチームメンバーからのメッセージ
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: teamMembers[0].name,
          content: 'ありがとう！これでプロジェクトを進められるよ。コンフリクトの解決お疲れ様！',
          timestamp: new Date()
        }]);
        
        // リセット
        setConflictMode(false);
        setSelectedFile(null);
        setResolutionStep(0);
      }, 2000);
    }
  };
  
  // コンフリクト内容生成関数
  const generateConflictContent = () => {
    // コンフリクト部分を特定
    const myLines = myVersion.split('\n');
    const teamLines = teamMemberVersion.split('\n');
    
    // コンフリクトがある行を探す
    let conflictLines = [];
    
    for (let i = 0; i < Math.max(myLines.length, teamLines.length); i++) {
      if (i < myLines.length && i < teamLines.length && myLines[i] !== teamLines[i]) {
        // 同じ行番号で内容が異なる
        conflictLines.push(i);
      }
    }
    
    // コンフリクトがない場合は強制的に作成
    if (conflictLines.length === 0) {
      if (teamLines.length > myLines.length) {
        // チームメンバーが行を追加した場合
        conflictLines.push(myLines.length);
      } else {
        // 自分が行を追加した場合や、その他の場合
        conflictLines.push(Math.min(2, myLines.length - 1));
      }
    }
    
    // コンフリクトマーカーを置く行
    const conflictLineIdx = conflictLines[0];
    
    // コンフリクトマーカー付きのコンテンツを生成
    const result = [];
    
    for (let i = 0; i < Math.max(myLines.length, teamLines.length); i++) {
      if (i === conflictLineIdx) {
        // コンフリクト部分の表示
        result.push('<<<<<<< HEAD');
        if (i < myLines.length) {
          result.push(myLines[i]); // 自分の変更
        }
        result.push('=======');
        if (i < teamLines.length) {
          result.push(teamLines[i]); // 相手の変更
        }
        result.push('>>>>>>> feature-branch');
      } else {
        // コンフリクトがない行
        if (i < myLines.length) {
          result.push(myLines[i]);
        } else if (i < teamLines.length) {
          result.push(teamLines[i]);
        }
      }
    }
    
    return result.join('\n');
  };
  
  // シミュレーションの解決ボタンハンドラー
  const resolveConflict = () => {
    nextResolutionStep();
  };
  
  // ユーザーが編集した内容の更新
  const handleEditableContentChange = (e) => {
    setUserEditableContent(e.target.value);
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
              {resolutionStep === 0 ? (
                // 初期状態: 現在の内容を表示
                <pre>{sharedContent}</pre>
              ) : resolutionStep === 1 ? (
                // 編集モード: コンフリクトマーカー付きの内容を編集可能
                <textarea 
                  className={styles.conflictEditor}
                  value={userEditableContent}
                  onChange={handleEditableContentChange}
                  spellCheck="false"
                />
              ) : (
                // 解決後: 解決された内容を表示
                <pre>{resolvedContent}</pre>
              )}
            </div>
            
            <div className={styles.conflictResolution}>
              <p>コンフリクトを解決するには:</p>
              <ol>
                <li className={resolutionStep >= 0 ? styles.activeStep : ''}>
                  コンフリクトの特定と変更内容の確認
                  {resolutionStep === 0 && <span className={styles.currentStep}> ← 現在のステップ</span>}
                </li>
                <li className={resolutionStep >= 1 ? styles.activeStep : ''}>
                  変更の選択と統合
                  {resolutionStep === 1 && <span className={styles.currentStep}> ← 現在のステップ</span>}
                  {resolutionStep === 1 && (
                    <div className={styles.conflictGuide}>
                      <h4>コンフリクト解決手順:</h4>
                      <ol>
                        <li>コンフリクトマーカーを確認します: <code>{'<<<<<<< HEAD'}</code> から <code>{'>>>>>>> feature-branch'}</code> まで</li>
                        <li><code>{'<<<<<<< HEAD'}</code> から <code>{'======='}</code> まではあなたの変更内容です</li>
                        <li><code>{'======='}</code> から <code>{'>>>>>>> feature-branch'}</code> まではチームメンバーの変更内容です</li>
                        <li>コンフリクトを以下のいずれかの方法で解決します:</li>
                        <ul>
                          <li>あなたの変更を選択: チームメンバーの変更を削除します</li>
                          <li>チームメンバーの変更を選択: あなたの変更を削除します</li>
                          <li>両方の変更を統合: コンフリクト部分を新しい内容に置き換えます</li>
                        </ul>
                        <li><strong>重要</strong>: すべてのコンフリクトマーカー (<code>{'<<<<<<< HEAD'}</code>, <code>{'======='}</code>, <code>{'>>>>>>> feature-branch'}</code>) を必ず削除してください</li>
                      </ol>
                    </div>
                  )}
                </li>
                <li className={resolutionStep >= 2 ? styles.activeStep : ''}>
                  統合内容の確認
                  {resolutionStep === 2 && <span className={styles.currentStep}> ← 現在のステップ</span>}
                </li>
                <li className={resolutionStep >= 3 ? styles.activeStep : ''}>
                  コミットの作成
                  {resolutionStep === 3 && <span className={styles.currentStep}> ← 現在のステップ</span>}
                </li>
              </ol>
              
              <button 
                className={styles.resolveButton}
                onClick={resolveConflict}
              >
                {resolutionStep === 0 
                  ? 'コンフリクトを確認する' 
                  : resolutionStep === 1 
                    ? '解決内容を確定する' 
                    : 'コンフリクト解決完了'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}