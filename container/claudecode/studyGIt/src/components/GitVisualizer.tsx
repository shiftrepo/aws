"use client";

import { useEffect, useRef } from 'react';
import styles from './GitVisualizer.module.css';
import DEFAULT_FILES from '@/components/DefaultFiles';

interface Commit {
  id: string;
  message: string;
  author: string;
  timestamp: string;
  branch: string;
  files: Record<string, string>;
  hasConflict?: boolean;
  resolvedConflict?: boolean;
}

interface Repository {
  files: Record<string, string>;
  commits: Commit[];
  branches: string[];
  currentBranch: string;
}

interface GitVisualizerProps {
  repository: Repository;
}

export default function GitVisualizer({ repository }: GitVisualizerProps) {
  // 初期ロード時にデフォルトコミットがない場合は追加する処理
  useEffect(() => {
    if (repository.commits && repository.commits.length === 0) {
      // 初期化用に別の処理を追加することがあればここに記述
    }
  }, [repository.commits]);
  const canvasRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    // 既存の要素をクリア
    while (canvasRef.current.firstChild) {
      canvasRef.current.removeChild(canvasRef.current.firstChild);
    }
    
    // コミットがない場合は初期メッセージを表示
    if (repository.commits.length === 0) {
      const emptyMsg = document.createElement('div');
      emptyMsg.className = styles.emptyState;
      emptyMsg.innerHTML = `
        <div class="${styles.emptyIcon}">🌱</div>
        <h3>まだコミットはありません</h3>
        <p>ファイルを作成・編集し、コミットすると履歴が可視化されます。</p>
      `;
      canvasRef.current.appendChild(emptyMsg);
      return;
    }
    
    // コミット履歴の構築
    const timeline = document.createElement('div');
    timeline.className = styles.timeline;
    
    repository.commits.forEach((commit, index) => {
      const commitEl = document.createElement('div');
      commitEl.className = styles.commit;
      
      // コミットノード
      const commitNode = document.createElement('div');
      commitNode.className = `${styles.commitNode} ${commit.hasConflict ? styles.conflictCommit : ''} ${commit.resolvedConflict ? styles.resolvedCommit : ''}`;
      
      // コミット情報
      const commitInfo = document.createElement('div');
      commitInfo.className = styles.commitInfo;
      
      // 短いコミットID
      const shortId = commit.id.substring(0, 7);
      
      // コミットの内容
      commitInfo.innerHTML = `
        <div class="${styles.commitHeader}">
          <div class="${styles.commitId}">${shortId}</div>
          <div class="${styles.commitDate}">${new Date(commit.timestamp).toLocaleString()}</div>
          ${commit.resolvedConflict ? `<div class="${styles.conflictResolved}">コンフリクト解決済み</div>` : ''}
          ${commit.hasConflict && !commit.resolvedConflict ? `<div class="${styles.conflictDetected}">コンフリクト発生中</div>` : ''}
        </div>
        <div class="${styles.commitMessage}">${commit.message}</div>
        <div class="${styles.commitAuthor}">Author: ${commit.author}</div>
        <div class="${styles.commitFiles}">
          <span>変更されたファイル:</span>
          ${Object.keys(commit.files).map(file => `<div class="${styles.fileTag}">${file}</div>`).join('')}
        </div>
      `;
      
      // ブランチラベル（現在のブランチのみ表示）
      if (index === repository.commits.length - 1 && repository.currentBranch === commit.branch) {
        const branchLabel = document.createElement('div');
        branchLabel.className = styles.branchLabel;
        branchLabel.textContent = commit.branch;
        commitEl.appendChild(branchLabel);
      }
      
      // 線を追加（最初のコミットを除く）
      if (index > 0) {
        const line = document.createElement('div');
        line.className = styles.commitLine;
        commitEl.appendChild(line);
      }
      
      commitEl.appendChild(commitNode);
      commitEl.appendChild(commitInfo);
      timeline.appendChild(commitEl);
    });
    
    // HEAD表示 - 現在のブランチの最新コミットに追加
    const head = document.createElement('div');
    head.className = styles.head;
    head.textContent = 'HEAD';
    
    // 現在のブランチの最新コミットを探す
    // timeline内の子要素（commitEl）は古い順に追加されているため、逆順でループ
    const timelineChildren = Array.from(timeline.children);
    let headAdded = false;
    
    for (let i = timelineChildren.length - 1; i >= 0; i--) {
      const commitIndex = timelineChildren.length - 1 - i;
      const commit = repository.commits[commitIndex];
      
      // 現在のブランチに属するコミットか確認
      if (commit.branch === repository.currentBranch) {
        // そのコミットにHEADを追加
        timelineChildren[i].appendChild(head);
        headAdded = true;
        break;
      }
    }
    
    // 万が一一致するコミットが見つからなかった場合は、最新コミットにHEADを追加
    if (!headAdded && timeline.lastChild) {
      timeline.lastChild.appendChild(head);
    }
    
    canvasRef.current.appendChild(timeline);
  }, [repository]);
  
  return (
    <div className={styles.visualizer}>
      <h2>Gitの履歴可視化</h2>
      <div className={styles.description}>
        コミット履歴をビジュアル化して確認できます。コミットノードをクリックすると詳細が表示されます。
      </div>
      
      <div className={styles.canvas} ref={canvasRef}></div>
      
      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.commitNodeLegend}`}></div>
          <span>コミット</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.branchLabelLegend}`}></div>
          <span>ブランチ</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.headLegend}`}></div>
          <span>HEAD（現在の位置）</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.conflictLegend}`}></div>
          <span>コンフリクト発生</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.resolvedLegend}`}></div>
          <span>コンフリクト解決済</span>
        </div>
      </div>
    </div>
  );
}