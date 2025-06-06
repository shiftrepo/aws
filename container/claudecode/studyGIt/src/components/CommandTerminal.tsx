"use client";

import { useState } from 'react';
import styles from './CommandTerminal.module.css';

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

interface CommandTerminalProps {
  repository: Repository;
  onCommit: (message: string) => void;
}

export default function CommandTerminal({ repository, onCommit }: CommandTerminalProps) {
  const [commitMessage, setCommitMessage] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([
    '$ git status',
    'On branch main',
    'Changes not staged for commit:',
    '  (use "git add <file>..." to update what will be committed)',
    '  (use "git restore <file>..." to discard changes in working directory)',
  ]);
  const [showStaged, setShowStaged] = useState(false);
  
  const handleCommand = (command: string) => {
    // コマンド履歴を追加
    setCommandHistory(prev => [...prev, `$ ${command}`]);
    
    // コマンドの解析と実行
    const parts = command.split(' ');
    const mainCommand = parts[0];
    
    if (mainCommand === 'git') {
      const gitCommand = parts[1];
      
      switch (gitCommand) {
        case 'status':
          handleGitStatus();
          break;
        case 'add':
          handleGitAdd(parts.slice(2));
          break;
        case 'commit':
          if (parts[2] === '-m' && parts[3]) {
            handleGitCommit(parts.slice(3).join(' ').replace(/"/g, ''));
          } else {
            setCommandHistory(prev => [...prev, 'Error: コミットメッセージを指定してください。例: git commit -m "メッセージ"']);
          }
          break;
        case 'log':
          handleGitLog();
          break;
        case 'branch':
          handleGitBranch();
          break;
        default:
          setCommandHistory(prev => [...prev, `Error: git ${gitCommand} は未実装のコマンドです。`]);
      }
    } else {
      setCommandHistory(prev => [...prev, `Error: ${mainCommand} はサポートされていないコマンドです。`]);
    }
  };
  
  const handleGitStatus = () => {
    const output = [
      `On branch ${repository.currentBranch}`,
      '',
    ];
    
    // 最新のコミットと現在のファイル状態を比較して変更を検出
    const lastCommit = repository.commits.length > 0 ? repository.commits[repository.commits.length - 1] : null;
    const lastCommitFiles = lastCommit ? lastCommit.files : {};
    
    // 変更されたファイルを検出
    const changedFiles = [];
    const newFiles = [];
    const deletedFiles = [];
    
    // 現在のファイルが追加または変更されているか確認
    for (const file in repository.files) {
      if (!lastCommitFiles[file]) {
        newFiles.push(file);
      } else if (lastCommitFiles[file] !== repository.files[file]) {
        changedFiles.push(file);
      }
    }
    
    // 削除されたファイルを検出
    for (const file in lastCommitFiles) {
      if (!repository.files[file]) {
        deletedFiles.push(file);
      }
    }
    
    const hasChanges = newFiles.length > 0 || changedFiles.length > 0 || deletedFiles.length > 0;
    
    if (!hasChanges && lastCommit) {
      output.push('Nothing to commit, working tree clean');
    } else {
      if (showStaged) {
        output.push('Changes to be committed:');
        output.push('  (use "git restore --staged <file>..." to unstage)');
        newFiles.forEach(file => {
          output.push(`\t新規ファイル: ${file}`);
        });
        changedFiles.forEach(file => {
          output.push(`\t変更: ${file}`);
        });
        deletedFiles.forEach(file => {
          output.push(`\t削除: ${file}`);
        });
      } else {
        output.push('Changes not staged for commit:');
        output.push('  (use "git add <file>..." to update what will be committed)');
        output.push('  (use "git restore <file>..." to discard changes in working directory)');
        newFiles.forEach(file => {
          output.push(`\t新規ファイル: ${file}`);
        });
        changedFiles.forEach(file => {
          output.push(`\t変更: ${file}`);
        });
        deletedFiles.forEach(file => {
          output.push(`\t削除: ${file}`);
        });
      }
    }
    
    setCommandHistory(prev => [...prev, ...output]);
  };
  
  const handleGitAdd = (files: string[]) => {
    if (files.length === 0 || files[0] === '.') {
      // すべてのファイルをステージング
      setShowStaged(true);
      setCommandHistory(prev => [...prev, 'すべてのファイルをステージングしました。']);
    } else {
      // 特定のファイルをステージング
      const validFiles = files.filter(file => repository.files[file]);
      if (validFiles.length === 0) {
        setCommandHistory(prev => [...prev, 'Error: 指定されたファイルは存在しません。']);
      } else {
        setShowStaged(true);
        setCommandHistory(prev => [...prev, `${validFiles.join(', ')} をステージングしました。`]);
      }
    }
  };
  
  const handleGitCommit = (message: string) => {
    if (!showStaged) {
      setCommandHistory(prev => [...prev, 'Error: コミットするためにはファイルをステージングする必要があります。git add . を実行してください。']);
      return;
    }
    
    if (!message) {
      setCommandHistory(prev => [...prev, 'Error: コミットメッセージを指定してください。']);
      return;
    }
    
    // 最新のコミットと現在のファイル状態を比較して変更を検出
    const lastCommit = repository.commits.length > 0 ? repository.commits[repository.commits.length - 1] : null;
    const lastCommitFiles = lastCommit ? lastCommit.files : {};
    
    // 変更されたファイルをカウント
    let changedFilesCount = 0;
    
    // 現在のファイルが追加または変更されているか確認
    for (const file in repository.files) {
      if (!lastCommitFiles[file] || lastCommitFiles[file] !== repository.files[file]) {
        changedFilesCount++;
      }
    }
    
    // 削除されたファイルをカウント
    for (const file in lastCommitFiles) {
      if (!repository.files[file]) {
        changedFilesCount++;
      }
    }
    
    // コミット実行
    onCommit(message);
    setShowStaged(false);
    setCommandHistory(prev => [...prev, `[${repository.currentBranch} ${repository.commits.length}] ${message}`]);
    setCommandHistory(prev => [...prev, `${changedFilesCount} ファイルが変更されました。`]);
  };
  
  const handleGitLog = () => {
    if (repository.commits.length === 0) {
      setCommandHistory(prev => [...prev, 'コミット履歴がありません。']);
      return;
    }
    
    const output: string[] = [];
    
    // 最新のコミットから表示
    [...repository.commits].reverse().forEach((commit, index) => {
      output.push(`commit ${commit.id}`);
      output.push(`Author: ${commit.author}`);
      output.push(`Date: ${new Date(commit.timestamp).toLocaleString()}`);
      output.push('');
      output.push(`    ${commit.message}`);
      output.push('');
    });
    
    setCommandHistory(prev => [...prev, ...output]);
  };
  
  const handleGitBranch = () => {
    const output = repository.branches.map(branch => 
      branch === repository.currentBranch ? `* ${branch}` : `  ${branch}`
    );
    
    setCommandHistory(prev => [...prev, ...output]);
  };
  
  // 入力フォーム送信時の処理
  const handleSubmitCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (commitMessage.trim() === '') return;
    
    handleCommand(commitMessage);
    setCommitMessage('');
  };
  
  // クイックアクションボタン
  const handleQuickAction = (command: string) => {
    handleCommand(command);
  };
  
  return (
    <div className={styles.terminal}>
      <div className={styles.header}>
        <div className={styles.dots}>
          <div className={styles.dot} style={{ backgroundColor: '#ff5f56' }}></div>
          <div className={styles.dot} style={{ backgroundColor: '#ffbd2e' }}></div>
          <div className={styles.dot} style={{ backgroundColor: '#27c93f' }}></div>
        </div>
        <div className={styles.title}>Git Terminal</div>
      </div>
      
      <div className={styles.terminalBody}>
        <div className={styles.output}>
          {commandHistory.map((line, index) => (
            <div key={index} className={line.startsWith('$') ? styles.command : styles.response}>
              {line}
            </div>
          ))}
        </div>
        
        <form className={styles.inputForm} onSubmit={handleSubmitCommand}>
          <div className={styles.prompt}>$</div>
          <input
            type="text"
            value={commitMessage}
            onChange={(e) => setCommitMessage(e.target.value)}
            className={styles.input}
            placeholder="git コマンドを入力してください..."
            autoFocus
          />
        </form>
      </div>
      
      <div className={styles.quickActions}>
        <button onClick={() => handleQuickAction('git status')}>git status</button>
        <button onClick={() => handleQuickAction('git add .')}>git add .</button>
        <button onClick={() => setCommitMessage('git commit -m "')}>git commit</button>
        <button onClick={() => handleQuickAction('git log')}>git log</button>
      </div>
      
      <div className={styles.help}>
        <h3>使えるコマンド</h3>
        <ul>
          <li><code>git status</code> - ワーキングディレクトリの状態を確認</li>
          <li><code>git add .</code> - すべての変更をステージング</li>
          <li><code>git commit -m "メッセージ"</code> - 変更をコミット</li>
          <li><code>git log</code> - コミット履歴を表示</li>
          <li><code>git branch</code> - ブランチ一覧を表示</li>
        </ul>
      </div>
    </div>
  );
}