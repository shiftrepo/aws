"use client";

import { useState, useEffect } from 'react';
import styles from './TeamSimulator.module.css';

// Next.jsの動的インポートを使用してガイドをロード
import dynamic from 'next/dynamic';
const ConflictGuide = dynamic(() => import('./ConflictGuide'), {
  ssr: false,
  loading: () => <p>ガイドをロード中...</p>
});

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
  const [initialFilesCreated, setInitialFilesCreated] = useState(false);
  
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
  
  // 初期化コードを設定
  useEffect(() => {
    // すでに初期化済みの場合は何もしない
    if (initialFilesCreated || Object.keys(repository.files).length === 0) {
      return;
    }
    
    setInitialFilesCreated(true);
    
    // システム通知はチャットではなく別の通知エリアに表示
  }, [repository.files, initialFilesCreated]);

  // 競合シミュレーションの開始
  const startConflictSimulation = () => {
    // 既存のコミットからファイルをロードしてシミュレーション
    if (repository.commits && repository.commits.length > 0 && !conflictMode) {
      // 初期コミットが存在する場合、チームメンバーからの自然なメッセージを追加
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: teamMembers[0].name,
        content: `おはよう、${username}さん！今日はfeature-branchで新機能の実装を進めてるんだ。このファイルもいくつか変更したから、同じファイルを触る時は注意してね！`,
        timestamp: new Date()
      }]);
    }
    
    // 「tutorial-file.js」ファイルがあれば自動的に選択
    let targetFile = selectedFile;
    Object.keys(repository.files).forEach(file => {
      if (file === 'tutorial-file.js') {
        targetFile = file;
      }
    });
    
    if (!targetFile || !repository.files[targetFile]) return;
    
    // チュートリアル用ファイルが選択されていた場合は特別な処理
    const isTutorialFile = targetFile === 'tutorial-file.js';
    
    // 現在のシミュレーション用のコマンド履歴を表示
    const commandHistory = [
      { command: 'git checkout feature-branch', description: '機能追加ブランチに切り替え' },
      { command: 'git add ' + targetFile, description: 'ファイルを変更してコミット' },
      { command: 'git commit -m "ファイルを更新"', description: '変更をコミット' },
      { command: 'git checkout main', description: 'メインブランチに戻る' },
      // ユーザーの変更を反映
      { command: `git add ${targetFile}`, description: 'メインブランチでも変更を加える' },
      { command: `git commit -m "同じファイルを別の方法で更新"`, description: 'メインブランチでの変更をコミット' },
      { command: 'git merge feature-branch', description: 'feature-branchをマージしようとすると...' },
      { command: '🚫 CONFLICT!', description: 'コンフリクトが発生' },
    ];
    
    // コマンド履歴をチャットに表示
    commandHistory.forEach((cmd, index) => {
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now() + index,
          sender: 'Git',
          content: `${cmd.command} ← ${cmd.description}`,
          timestamp: new Date()
        }]);
      }, index * 800);
    });

    // 自分のバージョンを保存
    const myCurrentVersion = repository.files[targetFile];
    setMyVersion(myCurrentVersion);
    
    setConflictMode(true);
    setSharedContent(myCurrentVersion);
    setUserEditableContent(myCurrentVersion);
    setSelectedFile(targetFile);
    
    // コンフリクト状態を親コンポーネントに通知
    if (props.onConflictStateChange) {
      props.onConflictStateChange({
        active: true,
        resolved: false,
        file: targetFile
      });
    }
    
    // 最後のメンバーからのメッセージはコマンド履歴の表示後に表示
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 100,
        sender: teamMembers[0].name,
        content: `あ、${targetFile}ファイルに変更を加えたから確認してください！`,
        timestamp: new Date()
      }]);
    }, commandHistory.length * 800 + 500);
    
    // メンバーからのメッセージ後にさらに遅延させる
    setTimeout(() => {
      if (!targetFile) return;
      
      // チームメンバーの変更を作成
      let teamVersion = '';
      const lines = myCurrentVersion.split('\n');
      
      if (isTutorialFile) {
        // チュートリアル用ファイルの場合は特定の行を変更
        const modifiedLines = [...lines];
        // CONFIGオブジェクトの部分を変更
        for (let i = 0; i < modifiedLines.length; i++) {
          if (modifiedLines[i].includes('const CONFIG = {')) {
            modifiedLines[i+1] = '  darkMode: true, // ダークモードをデフォルトに変更';
            modifiedLines[i+3] = '  notifications: false, // 通知をデフォルトでオフに変更';
            break;
          }
        }
        teamVersion = modifiedLines.join('\n');
      } else if (contentAnalysis.type === 'javascript') {
        // JavaScriptファイルの場合は関数や変数に基づいた変更
        const modifiedLines = [...lines];
        
        // プロパティや値の変更を探す
        for (let i = 0; i < modifiedLines.length; i++) {
          // 値の変更などを探す
          if (modifiedLines[i].includes('const') || modifiedLines[i].includes('let') || modifiedLines[i].includes('var')) {
            if (modifiedLines[i].includes('true') || modifiedLines[i].includes('false')) {
              // 真偽値を反転
              modifiedLines[i] = modifiedLines[i].replace('true', 'false').replace('false', 'true');
              teamVersion = modifiedLines.join('\n');
              break;
            } else if (modifiedLines[i].includes('=')) {
              // 数値などを変更
              const match = modifiedLines[i].match(/(=\s*)(\d+|"[^"]*"|'[^']*')/); 
              if (match) {
                // 値を変更、数値なら増加、文字列なら別の文字列に
                if (match[2].startsWith('"') || match[2].startsWith('\'')) {
                  const newValue = match[2].startsWith('"') ? '"Team version"' : '\'Team version\'';
                  modifiedLines[i] = modifiedLines[i].replace(match[0], `${match[1]}${newValue}`);
                } else if (!isNaN(match[2])) {
                  const newValue = parseInt(match[2]) + 100;
                  modifiedLines[i] = modifiedLines[i].replace(match[0], `${match[1]}${newValue}`);
                }
                teamVersion = modifiedLines.join('\n');
                break;
              }
            }
          }
        }
        
        // 変更が見つからなかった場合はコメントを追加
        if (teamVersion === '') {
          const lineToModify = Math.min(2, lines.length - 1);
          modifiedLines[lineToModify] = `// ${teamMembers[0].name}による変更: 重要な機能を追加しました ${new Date().toLocaleString()}\n` + modifiedLines[lineToModify];
          teamVersion = modifiedLines.join('\n');
        }
      } else if (contentAnalysis.type === 'config') {
        // 設定ファイルの場合は値を変更
        const modifiedLines = [...lines];
        for (let i = 0; i < modifiedLines.length; i++) {
          if (modifiedLines[i].includes(':') && (modifiedLines[i].includes('true') || modifiedLines[i].includes('false'))) {
            modifiedLines[i] = modifiedLines[i].replace('true', 'false').replace('false', 'true');
            teamVersion = modifiedLines.join('\n');
            break;
          }
        }
        
        if (teamVersion === '') {
          // 変更点が見つからない場合は適当な行を追加
          const lineToModify = Math.min(lines.length - 2, 5);
          modifiedLines.splice(lineToModify, 0, `  "teamSetting": "added by ${teamMembers[0].name}",`);
          teamVersion = modifiedLines.join('\n');
        }
      } else {
        // ファイルに行を追加
        teamVersion = myCurrentVersion + `\n// ${teamMembers[0].name}による変更: 重要な機能を追加しました ${new Date().toLocaleString()}`;
      }
      
      setTeamMemberVersion(teamVersion);
      
      // メッセージを表示
      setMessages(prev => [...prev, {
        id: Date.now() + 200,
        sender: teamMembers[0].name,
        content: `あ、同じファイルを変更してた！プルしたらコンフリクトが発生するかも、確認してくれる?`,
        timestamp: new Date()
      }]);
      
      // 自分も変更したことを伝える
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now() + 300,
          sender: username,
          content: `あれ、私もそのファイル修正してたんだけど...`,
          timestamp: new Date()
        }]);
      }, 2000);
    }, commandHistory.length * 800 + 3000);
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
      
      // システム通知はチャットではなく、チームメンバーからのメッセージとして表示する
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender: teamMembers[0].name,
        content: 'あ、このファイルにコンフリクトが発生してるね。<<<<<<< HEADから>>>>>>> feature-branchまでのマーカーを見て、両方の変更を上手くマージしてみて！',
        timestamp: new Date()
      });
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
  
  // 編集内容を読み取り、コンフリクトを生成する
  const analyzeContent = (content) => {
    // ファイルの種類によって適切な変更を手配
    if (content.includes('class') && content.includes('function')) {
      // JavaScriptクラスや関数を含むファイル
      return {
        type: 'javascript',
        targets: {
          // クラスや関数のプロパティ名、値を変更候補として検知
          properties: content.match(/(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*([^;]+)/g) || [],
          functions: content.match(/function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\([^)]*\)/g) || [],
          comments: content.match(/\/\/\s*(.*)/g) || []
        }
      };
    } else if (content.includes('{')){      
      // JSONや設定ファイル
      return {
        type: 'config',
        targets: {
          properties: content.match(/"([^"]+)"\s*:\s*([^,\n}]+)/g) || []
        }
      };
    } else {
      // テキストなどのファイル
      return {
        type: 'text',
        targets: {
          lines: content.split('\n').filter(line => line.trim() !== '')
        }
      };
    }
  };
  
  // コンフリクト内容生成関数
  const generateConflictContent = () => {
    // チュートリアルファイルかどうかチェック
    const isTutorialFile = selectedFile === 'tutorial-file.js';
    
    // コンフリクト部分を特定
    const myLines = myVersion.split('\n');
    const teamLines = teamMemberVersion.split('\n');
    
    // 編集されている内容を分析
    const contentAnalysis = analyzeContent(myVersion);
    const teamContentAnalysis = analyzeContent(teamMemberVersion);
    
    // チュートリアルファイルの場合は分かりやすくコンフリクトを生成
    if (isTutorialFile) {
      const result = [];
      let inConfigSection = false;
      let conflictAdded = false;
      
      // 元のファイルをスキャンし、CONFIG部分にコンフリクトを挿入
      for (let i = 0; i < myLines.length; i++) {
        const line = myLines[i];
        
        if (line.includes('const CONFIG = {')) {
          // CONFIGセクションの開始を見つけた
          result.push(line);
          inConfigSection = true;
        }
        else if (inConfigSection && line.includes('darkMode:')) {
          // ダークモード設定行を見つけた場合はコンフリクトを挿入
          result.push('<<<<<<< HEAD');
          result.push(line); // 自分の変更を追加 (darkMode: false)
          result.push('=======');
          result.push('  darkMode: true, // ダークモードをデフォルトに変更'); // チームメンバーの変更
          result.push('>>>>>>> feature-branch');
          conflictAdded = true;
        }
        else if (inConfigSection && line.includes('notifications:') && !conflictAdded) {
          // もしダークモード設定が見つからなかった場合は、notifications設定でコンフリクトを発生させる
          result.push('<<<<<<< HEAD');
          result.push(line); // 自分の変更 (notifications: true)
          result.push('=======');
          result.push('  notifications: false, // 通知をデフォルトでオフに変更'); // チームメンバーの変更
          result.push('>>>>>>> feature-branch');
          conflictAdded = true;
        } 
        else {
          // それ以外の行はそのまま追加
          result.push(line);
        }
        
        // CONFIGセクションの終了を検出
        if (inConfigSection && line.includes('};')) {
          inConfigSection = false;
        }
      }
      
      // どこにもコンフリクトを追加できなかった場合は、ファイルの最後に追加
      if (!conflictAdded) {
        result.push('');
        result.push('<<<<<<< HEAD');
        result.push('// あなたの追加コメント');
        result.push('=======');
        result.push('// チームメンバーの追加コメント');
        result.push('>>>>>>> feature-branch');
      }
      
      // 完成したコンフリクト内容を返す
      return result.join('\n');
    } 
    
    // 通常ファイルの場合はこれまでの機能を使用
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
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{
                backgroundColor: '#f44336',
                color: 'white',
                padding: '0.25rem 0.75rem',
                borderRadius: '4px',
                fontWeight: 'bold',
                marginRight: '1rem',
                display: 'flex',
                alignItems: 'center'
              }}>
                <span style={{ marginRight: '6px' }}>⚠️</span>
                コンフリクト発生
              </div>
              <p style={{ margin: 0, fontStyle: 'italic', color: '#666' }}>チームメンバーが同じファイルを編集しています</p>
            </div>

            <div style={{
              border: '1px solid #ddd',
              borderRadius: '6px',
              padding: '0.75rem',
              marginBottom: '1rem',
              backgroundColor: '#f9f9f9'
            }}>
              <p><strong>シミュレーション:</strong> 同じファイルの同じ部分をあなたとチームメンバーが同時に編集したため、
              Gitはどちらの変更を採用すべきか判断できません。<br />コンフリクトを解消するために、ファイルを編集してください。</p>
            </div>

            <p>コンフリクトが発生しているファイルの内容:</p>
            
            <div className={styles.codeEditor} style={{ maxHeight: '800px' }}>
              {resolutionStep === 0 ? (
                // 初期状態: 現在の内容を表示
                <pre style={{ 
                  maxHeight: '700px', 
                  overflow: 'auto', 
                  fontSize: '1.2rem',
                  lineHeight: '1.8',
                  padding: '20px',
                  fontFamily: '"Consolas", "Monaco", "Courier New", monospace',
                  backgroundColor: '#1e1e1e',
                  color: '#f8f8f8',
                  borderRadius: '8px',
                  border: '1px solid #444'
                }}>{sharedContent}</pre>
              ) : resolutionStep === 1 ? (
                // 編集モード: コンフリクトマーカー付きの内容を編集可能
                <div style={{ position: 'relative' }}>
                  <div style={{
                    position: 'absolute',
                    top: '10px',
                    left: '10px',
                    background: '#444',
                    color: '#eee',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    zIndex: 10
                  }}>コンフリクト解決中: {selectedFile}</div>
                  <textarea 
                    className={styles.conflictEditor}
                    value={userEditableContent}
                    onChange={handleEditableContentChange}
                    spellCheck="false"
                    style={{ 
                      height: '700px',
                      fontSize: '1.2rem',
                      lineHeight: '1.8',
                      padding: '20px 20px 20px 40px',
                      fontFamily: '"Consolas", "Monaco", "Courier New", monospace',
                      backgroundColor: '#1e1e1e',
                      color: '#f8f8f8',
                      border: '1px solid #666',
                      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
                      borderRadius: '8px',
                      marginTop: '10px'
                    }}
                  />
                </div>
              ) : (
                // 解決後: 解決された内容を表示
                <pre style={{ 
                  maxHeight: '700px', 
                  overflow: 'auto',
                  fontSize: '1.2rem',
                  lineHeight: '1.8',
                  padding: '20px',
                  fontFamily: '"Consolas", "Monaco", "Courier New", monospace',
                  backgroundColor: '#1e1e1e',
                  color: '#f8f8f8',
                  borderRadius: '8px',
                  border: '1px solid #444',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                }}>{resolvedContent}</pre>
              )}
            </div>
            
            <div className={styles.conflictResolution}>
              {/* 詳細なコマンド履歴と解説 */}
              <div style={{
                backgroundColor: '#282c34',
                color: '#abb2bf',
                padding: '1rem',
                borderRadius: '6px',
                marginBottom: '1rem',
                overflowX: 'auto',
                fontSize: '1rem',
                lineHeight: '1.5',
                fontFamily: 'Consolas, Monaco, "Courier New", monospace',
              }}>
                <div style={{ marginBottom: '0.5rem', color: '#7cb7ff', fontWeight: 'bold' }}>$ git status</div>
                <div style={{ color: '#f0f0f0', marginLeft: '0.5rem', marginBottom: '0.75rem' }}>On branch main<br/>Your branch is up to date with 'origin/main'.</div>
                
                <div style={{ marginBottom: '0.5rem', color: '#7cb7ff', fontWeight: 'bold' }}>$ git checkout feature-branch</div>
                <div style={{ color: '#f0f0f0', marginLeft: '0.5rem', marginBottom: '0.75rem' }}>Switched to branch 'feature-branch'</div>

                <div style={{ marginBottom: '0.5rem', color: '#7cb7ff', fontWeight: 'bold' }}>$ git checkout main</div>
                <div style={{ color: '#f0f0f0', marginLeft: '0.5rem', marginBottom: '0.75rem' }}>Switched to branch 'main'</div>
                
                <div style={{ marginBottom: '0.5rem', color: '#7cb7ff', fontWeight: 'bold' }}>$ git merge feature-branch</div>
                <div style={{ color: '#f08080', marginLeft: '0.5rem', marginBottom: '0.75rem' }}>Auto-merging tutorial-file.js<br/>CONFLICT (content): Merge conflict in tutorial-file.js<br/>Automatic merge failed; fix conflicts and then commit the result.</div>
              </div>
              
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
                      <h4>🚨 コンフリクト解決ガイド 🚨</h4>
                      
                      <div className={styles.conflictTip}>
                        <span className={styles.tipIcon}>💡</span>
                        <span>Gitのコンフリクトは怖くない！チームでの協力作業で普通に起こることです</span>
                      </div>
                      
                      <ol>
                        <li>
                          <span className={styles.stepNumber}>1</span>
                          <span className={styles.stepTitle}>コンフリクトマーカーを理解しよう</span>
                          <div className={styles.stepDetail}>
                            <p>編集エリアに表示されている <code className={styles.codeMarker}>{'<<<<<<< HEAD'}</code> から <code className={styles.codeMarker}>{'>>>>>>> feature-branch'}</code> までがコンフリクト部分です</p>
                            <div style={{ display: 'flex', justifyContent: 'center', margin: '1rem 0', position: 'relative' }}>
                              <div style={{ textAlign: 'center', padding: '0.5rem', background: '#2d2d2d', borderRadius: '4px', width: '80%', position: 'relative' }}>
                                <div style={{ position: 'absolute', top: '-10px', left: '10px', background: '#444', padding: '0 0.5rem', borderRadius: '4px', fontSize: '0.8rem', color: '#aaa' }}>conflict.js</div>
                                <code style={{ whiteSpace: 'pre', fontFamily: 'monospace', color: '#eee', textAlign: 'left', display: 'block' }}>
                                  <span style={{ color: '#e06c75' }}>{'<<<<<<< HEAD'}</span>
                                  <br/><span style={{ color: '#98c379' }}>あなたのコード部分はここに表示されます</span>
                                  <br/><span style={{ color: '#e06c75' }}>{'======='}</span>
                                  <br/><span style={{ color: '#61afef' }}>チームメンバーのコード部分はここに表示されます</span>
                                  <br/><span style={{ color: '#e06c75' }}>{'>>>>>>> feature-branch'}</span>
                                </code>
                              </div>
                            </div>
                          </div>
                        </li>
                        
                        <li>
                          <span className={styles.stepNumber}>2</span>
                          <span className={styles.stepTitle}>両方の変更を確認しよう</span>
                          <div className={styles.stepDetail}>
                            <div className={styles.codeSection}>
                              <span className={styles.codeLabel}>👉 あなたの変更（現在のブランチ）:</span>
                              <code className={styles.codeSample}>{'<<<<<<< HEAD'}<br/>あなたのコード<br/>{'======='}</code>
                            </div>
                            <div className={styles.codeSection}>
                              <span className={styles.codeLabel}>👨‍💻 チームメンバーの変更（取り込むブランチ）:</span>
                              <code className={styles.codeSample}>{'======='}<br/>チームメンバーのコード<br/>{'>>>>>>> feature-branch'}</code>
                            </div>
                          </div>
                        </li>
                        
                        <li>
                          <span className={styles.stepNumber}>3</span>
                          <span className={styles.stepTitle}>どちらかを選ぶ or 統合する</span>
                          <div className={styles.stepDetail}>
                            <div className={styles.optionBox}>
                              <span className={styles.option}>選択肢1: あなたのコードを残す</span>
                              <code className={styles.codeSolution}>あなたのコード</code>
                              <span className={styles.optionInstruction}>チームメンバーの変更部分と全てのマーカーを削除</span>
                            </div>
                            
                            <div className={styles.optionBox}>
                              <span className={styles.option}>選択肢2: チームメンバーのコードを採用</span>
                              <code className={styles.codeSolution}>チームメンバーのコード</code>
                              <span className={styles.optionInstruction}>あなたの変更部分と全てのマーカーを削除</span>
                            </div>
                            
                                    <div className={styles.optionBox}>
                              <span className={styles.option}>選択肢3: 両方をうまく統合</span>
                              <code className={styles.codeSolution}>両方を活かした新しいコード</code>
                              <span className={styles.optionInstruction}>マーカーは全て削除し、両方の良いところを取り入れる</span>
                              <div className={styles.exampleResult} style={{ marginTop: '0.75rem', padding: '0.5rem', background: 'rgba(0,255,0,0.05)', borderRadius: '4px' }}>
                                <span style={{ fontSize: '0.8rem', color: '#aaa', display: 'block', marginBottom: '0.25rem' }}>例: 統合結果</span>
                                <code style={{ fontSize: '0.9rem', color: '#98c379' }}>// 両方の変更を活かした新しい機能</code>
                              </div>
                            </div>
                          </div>
                        </li>
                        
                        <li>
                          <span className={styles.stepNumber}>4</span>
                          <span className={styles.stepTitle}>最終確認</span>
                          <div className={styles.stepDetail}>
                            <div className={styles.warningBox}>
                              <span className={styles.warningIcon}>⚠️</span>
                              <span><strong>必ず確認:</strong> 全てのコンフリクトマーカー (<code className={styles.inlineCode}>{'<<<<<<< HEAD'}</code>, <code className={styles.inlineCode}>{'======='}</code>, <code className={styles.inlineCode}>{'>>>>>>> feature-branch'}</code>) が削除されているか確認してください！これらのマーカーが残っていると、コンフリクトは解決されません。</span>
                            </div>
                          </div>
                        </li>
                      </ol>
                      
                      <div className={styles.cheerMessage}>
                        <span className={styles.cheerIcon}>🎉</span>
                        <span>あなたならできる！コンフリクト解決は開発者としての重要なスキルです。一歩ずつ進めていきましょう！</span>
                      </div>
                    </div>
                  )}
                </li>
                <li className={resolutionStep >= 2 ? styles.activeStep : ''}>
                  統合内容の確認
                  {resolutionStep === 2 && <span className={styles.currentStep}> ← 現在のステップ</span>}
              {resolutionStep === 2 && (
                <div className={styles.stepDetail}>
                  <div className={styles.cheerMessage}>
                    <span className={styles.cheerIcon}>🎯</span>
                    <span>素晴らしい！コンフリクトを解決できました。</span>
                  </div>
                  <div className={styles.codeSection} style={{marginTop: '1rem'}}>
                    <span className={styles.codeLabel}>最終的なコード:</span>
                    <code className={styles.codeSample}>{resolvedContent}</code>
                  </div>
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '1rem', 
                    background: 'rgba(76, 175, 80, 0.1)', 
                    borderRadius: '8px', 
                    textAlign: 'center',
                    position: 'relative',
                    overflow: 'hidden'
                  }}>
                    <div style={{ 
                      position: 'absolute', 
                      top: '-20px', 
                      left: '-20px', 
                      width: '120%', 
                      height: '10px', 
                      background: 'linear-gradient(90deg, transparent, rgba(255,215,0,0.5), transparent)', 
                      animation: 'confetti 2s linear infinite',
                      transformOrigin: 'center',
                      transform: 'rotate(10deg)'
                    }}></div>
                    <div style={{ 
                      position: 'absolute', 
                      bottom: '-20px', 
                      right: '-20px', 
                      width: '120%', 
                      height: '10px', 
                      background: 'linear-gradient(90deg, transparent, rgba(124,252,0,0.5), transparent)', 
                      animation: 'confetti 1.5s linear infinite',
                      transformOrigin: 'center',
                      transform: 'rotate(-10deg)'
                    }}></div>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#4caf50' }}>コンフリクト解決技能アップ！</h4>
                    <p style={{ margin: '0', fontSize: '0.9rem' }}>あなたはチーム開発における重要なスキルを身につけました。この経験は今後の開発で役立ちます！</p>
                  </div>
                </div>
              )}
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
                  ? '👉 コンフリクトを確認する' 
                  : resolutionStep === 1 
                    ? '✅ 解決内容を確定する' 
                    : '🎉 コンフリクト解決完了'}
              </button>
              
              {resolutionStep === 1 && (
                <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666', padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', textAlign: 'center' }}>
                  <span style={{ fontWeight: 'bold' }}>ヒント:</span> エディタ内のコンフリクトマーカーを削除して、最終的なコードを作成してください。
                  必要な部分を残し、必要のない部分は削除します。
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}