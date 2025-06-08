import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ConflictResolver.module.css';

/**
 * ConflictResolver コンポーネント
 * コンフリクトの詳細表示と解決プロセスのビジュアル化を行う
 */
const ConflictResolver = ({ conflict, onResolve }) => {
  const [resolveStep, setResolveStep] = useState(0);
  const [resolvedContent, setResolvedContent] = useState('');
  const [showDiff, setShowDiff] = useState(true);
  
  // コンフリクト情報がない場合は何も表示しない
  if (!conflict) return null;
  
  const { filename, content, localChanges, incomingChanges } = conflict;
  
  // コンフリクト部分のハイライト表示
  const highlightConflict = (content) => {
    return content.split('\n').map((line, index) => {
      if (line.startsWith('<<<<<<<')) {
        return (
          <div key={`conflict-start-${index}`} className={styles.conflictMarkerStart}>
            {line}
          </div>
        );
      } else if (line.startsWith('=======')) {
        return (
          <div key={`conflict-middle-${index}`} className={styles.conflictMarkerMiddle}>
            {line}
          </div>
        );
      } else if (line.startsWith('>>>>>>>')) {
        return (
          <div key={`conflict-end-${index}`} className={styles.conflictMarkerEnd}>
            {line}
          </div>
        );
      } else if (conflict.localLines?.includes(index)) {
        return (
          <div key={`local-${index}`} className={styles.localChange}>
            {line}
          </div>
        );
      } else if (conflict.incomingLines?.includes(index)) {
        return (
          <div key={`incoming-${index}`} className={styles.incomingChange}>
            {line}
          </div>
        );
      } else {
        return (
          <div key={`normal-${index}`} className={styles.normalLine}>
            {line}
          </div>
        );
      }
    });
  };
  
  // コンフリクト解決のステップ
  const resolveSteps = [
    {
      title: "コンフリクトの確認",
      description: "マージしようとしているブランチで同じファイルの同じ箇所が変更されています。",
      content: (
        <div className={styles.stepContent}>
          <div className={styles.conflictFile}>
            <div className={styles.filename}>{filename}</div>
            <pre className={styles.codeBlock}>
              {highlightConflict(content)}
            </pre>
          </div>
          <div className={styles.instructionBox}>
            <h4>コンフリクトマーカーの意味</h4>
            <ul>
              <li><code>{'<<<<<<< HEAD'}</code> - 現在のブランチ（あなたの変更）</li>
              <li><code>{'======='}</code> - 区切り線</li>
              <li><code>{'>>>>>>> feature-branch'}</code> - マージしようとしているブランチ（他の人の変更）</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "変更の比較",
      description: "両方の変更を並べて比較し、どのように解決するかを検討します。",
      content: (
        <div className={styles.stepContent}>
          <div className={styles.diffView}>
            <div className={styles.diffPanel}>
              <div className={styles.panelHeader}>
                <div className={styles.headerBadge}>現在のブランチ (HEAD)</div>
                <div className={styles.filename}>{filename}</div>
              </div>
              <pre className={`${styles.codeBlock} ${styles.localCode}`}>
                {localChanges.split('\n').map((line, i) => (
                  <div key={`local-${i}`} className={styles.codeLine}>
                    {line}
                  </div>
                ))}
              </pre>
            </div>
            <div className={styles.diffPanel}>
              <div className={styles.panelHeader}>
                <div className={styles.headerBadge}>マージするブランチ</div>
                <div className={styles.filename}>{filename}</div>
              </div>
              <pre className={`${styles.codeBlock} ${styles.incomingCode}`}>
                {incomingChanges.split('\n').map((line, i) => (
                  <div key={`incoming-${i}`} className={styles.codeLine}>
                    {line}
                  </div>
                ))}
              </pre>
            </div>
          </div>
          <div className={styles.instructionBox}>
            <h4>解決方法の選択</h4>
            <p>以下の方法から選択できます:</p>
            <ul>
              <li>現在のブランチの変更を採用</li>
              <li>マージするブランチの変更を採用</li>
              <li>両方の変更を統合して新しいコードを作成</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "コンフリクトの解決",
      description: "コンフリクトマーカーを取り除き、統合されたコードを作成します。",
      content: (
        <div className={styles.stepContent}>
          <div className={styles.resolveEditor}>
            <div className={styles.editorHeader}>
              <div className={styles.filename}>{filename}</div>
              <div className={styles.editorControls}>
                <button 
                  className={`${styles.controlButton} ${styles.useLocal}`}
                  onClick={() => setResolvedContent(localChanges)}
                >
                  現在のブランチを採用
                </button>
                <button 
                  className={`${styles.controlButton} ${styles.useIncoming}`}
                  onClick={() => setResolvedContent(incomingChanges)}
                >
                  マージするブランチを採用
                </button>
                <button 
                  className={`${styles.controlButton} ${styles.useBoth}`}
                  onClick={() => setResolvedContent(`${localChanges}\n\n${incomingChanges}`)}
                >
                  両方を採用
                </button>
              </div>
            </div>
            <textarea
              className={styles.resolveTextarea}
              value={resolvedContent}
              onChange={(e) => setResolvedContent(e.target.value)}
              placeholder="ここに解決後のコードを入力してください..."
            />
          </div>
          <div className={styles.instructionBox}>
            <h4>注意点</h4>
            <ul>
              <li>すべてのコンフリクトマーカー (<code>{'<<<<<<< HEAD'}</code>, <code>{'======='}</code>, <code>{'>>>>>>> feature-branch'}</code>) を削除してください</li>
              <li>コードが正しく統合されていることを確認してください</li>
              <li>必要に応じて、コードをテストしてください</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "解決の確定",
      description: "コンフリクト解決後の変更をコミットします。",
      content: (
        <div className={styles.stepContent}>
          <div className={styles.commitPreview}>
            <div className={styles.previewHeader}>
              <div className={styles.filename}>{filename} (解決後)</div>
            </div>
            <pre className={styles.codeBlock}>
              {resolvedContent.split('\n').map((line, i) => (
                <div key={`resolved-${i}`} className={styles.resolvedLine}>
                  {line}
                </div>
              ))}
            </pre>
          </div>
          <div className={styles.commitBox}>
            <div className={styles.commitMessage}>
              <label htmlFor="commitMessage">コミットメッセージ:</label>
              <input
                id="commitMessage"
                type="text"
                defaultValue="Merge branches and resolve conflicts"
                className={styles.messageInput}
              />
            </div>
            <div className={styles.commitCommands}>
              <pre className={styles.commandBlock}>
                <code>$ git add {filename}</code>
                <code>$ git commit -m "Merge branches and resolve conflicts"</code>
                <code>$ git push origin your-branch-name</code>
              </pre>
            </div>
          </div>
        </div>
      )
    }
  ];

  // 次のステップに進む
  const nextStep = () => {
    if (resolveStep < resolveSteps.length - 1) {
      setResolveStep(resolveStep + 1);
    } else {
      // 最終ステップの場合、解決完了としてコールバックを呼び出す
      onResolve && onResolve(resolvedContent);
    }
  };

  // 前のステップに戻る
  const prevStep = () => {
    if (resolveStep > 0) {
      setResolveStep(resolveStep - 1);
    }
  };

  return (
    <div className={styles.conflictResolver}>
      <h3 className={styles.title}>コンフリクト解決ウィザード</h3>
      
      <div className={styles.stepProgress}>
        {resolveSteps.map((step, index) => (
          <div 
            key={index}
            className={`${styles.step} ${index === resolveStep ? styles.active : ''} ${index < resolveStep ? styles.completed : ''}`}
            onClick={() => setResolveStep(index)}
          >
            <div className={styles.stepNumber}>{index + 1}</div>
            <div className={styles.stepLabel}>{step.title}</div>
          </div>
        ))}
      </div>

      <div className={styles.viewToggle}>
        {resolveStep === 1 && (
          <button
            className={`${styles.viewButton} ${showDiff ? styles.active : ''}`}
            onClick={() => setShowDiff(!showDiff)}
          >
            {showDiff ? "統合ビュー" : "差分ビュー"}
          </button>
        )}
      </div>
      
      <div className={styles.resolveContent}>
        <h4 className={styles.stepTitle}>{resolveSteps[resolveStep].title}</h4>
        <p className={styles.stepDescription}>{resolveSteps[resolveStep].description}</p>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={resolveStep}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {resolveSteps[resolveStep].content}
          </motion.div>
        </AnimatePresence>
      </div>
      
      <div className={styles.navigation}>
        <button 
          className={styles.navButton}
          onClick={prevStep}
          disabled={resolveStep === 0}
        >
          前へ
        </button>
        <div className={styles.stepInfo}>
          ステップ {resolveStep + 1} / {resolveSteps.length}
        </div>
        <button 
          className={styles.navButton}
          onClick={nextStep}
        >
          {resolveStep === resolveSteps.length - 1 ? "完了" : "次へ"}
        </button>
      </div>
    </div>
  );
};

export default ConflictResolver;