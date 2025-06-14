import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styles from './TeamGitFlow.module.css';
import ConflictResolver from './ConflictResolver';

const TeamGitFlow = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedScenario, setSelectedScenario] = useState('basic'); // 'basic' or 'conflict'
  const [viewMode, setViewMode] = useState('animation'); // 'animation' or 'details'
  const [showConflictResolver, setShowConflictResolver] = useState(false);
  const [currentConflict, setCurrentConflict] = useState(null);
  
  const basicScenarioSteps = [
    {
      title: "イシューの作成",
      description: "チームメンバーAがイシューを作成します",
      gitCommand: "# GitHubのUIでイシューを作成",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
          </div>
          <motion.div 
            className={styles.issue}
            initial={{ opacity: 0, x: '20%', y: '30%' }}
            animate={{ opacity: 1, x: '50%', y: '30%' }}
            transition={{ duration: 1 }}
          >
            <div className={styles.issueTitle}>イシュー #1: ユーザープロフィール表示機能</div>
            <div className={styles.issueDescription}>ユーザーのプロフィール情報を表示する画面を実装する</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
          </div>
        </div>
      )
    },
    {
      title: "イシューのアサイン",
      description: "チームメンバーBがイシューにアサインされます",
      gitCommand: "# GitHubのUIでイシューにアサイン",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
          </div>
          <motion.div 
            className={styles.issue}
            initial={{ x: '50%', y: '30%' }}
            animate={{ x: '80%', y: '30%' }}
            transition={{ duration: 1 }}
          >
            <div className={styles.issueTitle}>イシュー #1: ユーザープロフィール表示機能</div>
            <div className={styles.issueDescription}>ユーザーのプロフィール情報を表示する画面を実装する</div>
            <div className={styles.assignee}>担当: チームメンバーB</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
          </div>
        </div>
      )
    },
    {
      title: "ブランチの作成",
      description: "チームメンバーBが作業ブランチを作成します",
      gitCommand: "git checkout -b feature/user-profile main",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.terminal}>
              <code>$ git checkout -b feature/user-profile main</code>
            </div>
          </div>
          <div className={styles.issue} style={{ left: '80%', top: '30%' }}>
            <div className={styles.issueTitle}>イシュー #1: ユーザープロフィール表示機能</div>
            <div className={styles.issueStatus}>ステータス: 進行中</div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <motion.div 
              className={`${styles.branch} ${styles.featureBranch}`}
              initial={{ opacity: 0, left: '0%' }}
              animate={{ opacity: 1, left: '20%' }}
              transition={{ duration: 0.8 }}
            >
              feature/user-profile
            </motion.div>
          </div>
        </div>
      )
    },
    {
      title: "コードの実装",
      description: "チームメンバーBが機能を実装します",
      gitCommand: "# ファイルを編集しコード実装",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <motion.div 
              className={styles.code}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <pre>{`function UserProfile() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUserData().then(data => setUser(data));
  }, []);
  
  return (
    <div className="profile">
      {user && (
        <>
          <h2>{user.name}</h2>
          <p>{user.bio}</p>
        </>
      )}
    </div>
  );
}`}</pre>
            </motion.div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranch}`} style={{ left: '20%' }}>
              feature/user-profile*
            </div>
          </div>
        </div>
      )
    },
    {
      title: "コミット & プッシュ",
      description: "チームメンバーBが変更をコミットしてプッシュします",
      gitCommand: "git add .\ngit commit -m 'Add user profile component'\ngit push origin feature/user-profile",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.terminal}>
              <code>$ git add .</code>
              <code>$ git commit -m 'Add user profile component'</code>
              <code>$ git push origin feature/user-profile</code>
            </div>
          </div>
          <motion.div 
            className={styles.commit}
            initial={{ opacity: 0, x: '80%', y: '40%' }}
            animate={{ opacity: 1, x: '50%', y: '40%' }}
            transition={{ duration: 1 }}
          >
            <div className={styles.commitHash}>a7e3d21</div>
            <div className={styles.commitMessage}>Add user profile component</div>
            <div className={styles.commitAuthor}>Author: チームメンバーB</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranch}`} style={{ left: '20%' }}>
              feature/user-profile
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "プルリクエストの作成",
      description: "チームメンバーBがプルリクエストを作成します",
      gitCommand: "# GitHubのUIでプルリクエストを作成",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
          </div>
          <motion.div 
            className={styles.pullRequest}
            initial={{ opacity: 0, x: '80%', y: '30%' }}
            animate={{ opacity: 1, x: '50%', y: '30%' }}
            transition={{ duration: 1 }}
          >
            <div className={styles.prTitle}>PR #2: ユーザープロフィール表示機能の実装</div>
            <div className={styles.prDescription}>イシュー #1 の対応として、ユーザープロフィール表示コンポーネントを追加しました。</div>
            <div className={styles.prBranches}>feature/user-profile → main</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranch}`} style={{ left: '20%' }}>
              feature/user-profile
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
            <motion.div 
              className={styles.prArrow}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1 }}
            ></motion.div>
          </div>
        </div>
      )
    },
    {
      title: "コードレビュー",
      description: "チームメンバーAがコードをレビューします",
      gitCommand: "# GitHubのUIでレビュー実施",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
            <motion.div 
              className={styles.reviewComment}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7 }}
            >
              <div className={styles.reviewTitle}>レビューコメント</div>
              <div className={styles.comment}>"エラーハンドリングを追加した方が良いと思います。"</div>
            </motion.div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <motion.div 
              className={styles.reviewResponse}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7, delay: 1 }}
            >
              <div className={styles.responseTitle}>返答</div>
              <div className={styles.comment}>"ご指摘ありがとうございます。エラーハンドリングを追加します。"</div>
            </motion.div>
          </div>
          <div className={styles.pullRequest} style={{ left: '50%', top: '30%' }}>
            <div className={styles.prTitle}>PR #2: ユーザープロフィール表示機能の実装</div>
            <div className={styles.prStatus}>ステータス: レビュー中</div>
          </div>
        </div>
      )
    },
    {
      title: "フィードバックに基づく修正",
      description: "チームメンバーBがフィードバックに基づいて修正します",
      gitCommand: "# コードを修正\ngit add .\ngit commit -m 'Add error handling to user profile'\ngit push origin feature/user-profile",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <motion.div 
              className={styles.code}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.7 }}
            >
              <pre>{`function UserProfile() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchUserData()
      .then(data => setUser(data))
      .catch(err => setError(err.message));
  }, []);
  
  if (error) {
    return <div className="error">{error}</div>;
  }
  
  return (
    <div className="profile">
      {user && (
        <>
          <h2>{user.name}</h2>
          <p>{user.bio}</p>
        </>
      )}
    </div>
  );
}`}</pre>
            </motion.div>
            <motion.div 
              className={styles.terminal}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.5 }}
            >
              <code>$ git add .</code>
              <code>$ git commit -m 'Add error handling'</code>
              <code>$ git push origin feature/user-profile</code>
            </motion.div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranch}`} style={{ left: '20%' }}>
              feature/user-profile
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
              <motion.div 
                className={styles.commitDot} 
                style={{ top: '-10px', left: '70%' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 2 }}
              ></motion.div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "マージ完了",
      description: "プルリクエストがマージされます",
      gitCommand: "# GitHubのUIでマージ\ngit checkout main\ngit pull origin main",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
            <div className={styles.action}>
              <div className={styles.actionLabel}>マージを承認</div>
            </div>
          </div>
          <motion.div 
            className={`${styles.pullRequest} ${styles.merged}`}
            initial={{ x: '50%', y: '30%' }}
            animate={{ x: '50%', y: '30%', backgroundColor: '#e6f4ea' }}
            transition={{ duration: 0.7 }}
          >
            <div className={styles.prTitle}>PR #2: ユーザープロフィール表示機能の実装</div>
            <div className={styles.prStatus}>ステータス: マージ済み ✓</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <motion.div 
              className={styles.commitDot}
              initial={{ opacity: 0, top: '-10px', left: '0%' }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 1 }}
            ></motion.div>
            <div className={`${styles.branch} ${styles.featureBranch}`} style={{ left: '20%', opacity: 0.5 }}>
              feature/user-profile
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
              <div className={styles.commitDot} style={{ top: '-10px', left: '70%' }}></div>
            </div>
            <motion.div 
              className={styles.mergeArrow}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
            ></motion.div>
          </div>
          <motion.div 
            className={styles.issue}
            initial={{ opacity: 0, x: '50%', y: '80%' }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 2 }}
          >
            <div className={styles.issueTitle}>イシュー #1: ユーザープロフィール表示機能</div>
            <div className={styles.issueStatus}>ステータス: 完了 ✓</div>
          </motion.div>
        </div>
      )
    }
  ];
  
  const conflictScenarioSteps = [
    {
      title: "同時開発の開始",
      description: "チームメンバーAとBが異なるイシューに取り組みます",
      gitCommand: "# チームメンバーA\ngit checkout -b feature/notifications main\n\n# チームメンバーB\ngit checkout -b feature/theme-settings main",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
            <div className={styles.issue}>
              <div className={styles.issueTitle}>イシュー #2: 通知機能</div>
            </div>
            <div className={styles.terminal}>
              <code>$ git checkout -b feature/notifications main</code>
            </div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.issue}>
              <div className={styles.issueTitle}>イシュー #3: テーマ設定</div>
            </div>
            <div className={styles.terminal}>
              <code>$ git checkout -b feature/theme-settings main</code>
            </div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <motion.div 
              className={`${styles.branch} ${styles.featureBranchA}`}
              initial={{ opacity: 0, left: '-20%' }}
              animate={{ opacity: 1, left: '-20%' }}
              transition={{ duration: 0.8 }}
            >
              feature/notifications
            </motion.div>
            <motion.div 
              className={`${styles.branch} ${styles.featureBranchB}`}
              initial={{ opacity: 0, left: '20%' }}
              animate={{ opacity: 1, left: '20%' }}
              transition={{ duration: 0.8 }}
            >
              feature/theme-settings
            </motion.div>
          </div>
        </div>
      )
    },
    {
      title: "同一ファイルの編集",
      description: "両方のメンバーが同じファイルを編集します",
      gitCommand: "# 両方が同じファイル (AppContext.js) を編集",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
            <div className={styles.code}>
              <div className={styles.filename}>AppContext.js</div>
              <pre>{`const AppContext = createContext({
  user: null,
  // 通知機能を追加
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {}
});`}</pre>
            </div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.code}>
              <div className={styles.filename}>AppContext.js</div>
              <pre>{`const AppContext = createContext({
  user: null,
  // テーマ設定機能を追加
  theme: 'light',
  toggleTheme: () => {}
});`}</pre>
            </div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranchA}`} style={{ left: '-20%' }}>
              feature/notifications*
            </div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings*
            </div>
          </div>
        </div>
      )
    },
    {
      title: "変更のコミットとプッシュ",
      description: "両方のメンバーが変更をコミットしプッシュします",
      gitCommand: "# チームメンバーA\ngit add .\ngit commit -m 'Add notification context'\ngit push origin feature/notifications\n\n# チームメンバーB\ngit add .\ngit commit -m 'Add theme context'\ngit push origin feature/theme-settings",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '20%' }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.label}>チームメンバーA</div>
            <div className={styles.terminal}>
              <code>$ git add .</code>
              <code>$ git commit -m 'Add notification context'</code>
              <code>$ git push origin feature/notifications</code>
            </div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.terminal}>
              <code>$ git add .</code>
              <code>$ git commit -m 'Add theme context'</code>
              <code>$ git push origin feature/theme-settings</code>
            </div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranchA}`} style={{ left: '-20%' }}>
              feature/notifications
              <motion.div 
                className={styles.commitDot}
                initial={{ opacity: 0, top: '-10px' }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 0.5 }}
              ></motion.div>
            </div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings
              <motion.div 
                className={styles.commitDot}
                initial={{ opacity: 0, top: '-10px' }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 1 }}
              ></motion.div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "プルリクエスト作成",
      description: "両方のメンバーがプルリクエストを作成します",
      gitCommand: "# 両方がGitHubのUIでプルリクエストを作成",
      animation: (
        <div className={styles.animationContainer}>
          <motion.div 
            className={`${styles.pullRequest} ${styles.prA}`}
            initial={{ opacity: 0, x: '20%', y: '30%' }}
            animate={{ opacity: 1, x: '20%', y: '30%' }}
            transition={{ duration: 0.7 }}
          >
            <div className={styles.prTitle}>PR #4: 通知機能の追加</div>
            <div className={styles.prBranches}>feature/notifications → main</div>
          </motion.div>
          <motion.div 
            className={`${styles.pullRequest} ${styles.prB}`}
            initial={{ opacity: 0, x: '80%', y: '30%' }}
            animate={{ opacity: 1, x: '80%', y: '30%' }}
            transition={{ duration: 0.7, delay: 0.5 }}
          >
            <div className={styles.prTitle}>PR #5: テーマ設定機能の追加</div>
            <div className={styles.prBranches}>feature/theme-settings → main</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={`${styles.branch} ${styles.featureBranchA}`} style={{ left: '-20%' }}>
              feature/notifications
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "最初のPRがマージ",
      description: "チームメンバーAのプルリクエストが先にマージされます",
      gitCommand: "# GitHubのUIで最初のPRをマージ",
      animation: (
        <div className={styles.animationContainer}>
          <motion.div 
            className={`${styles.pullRequest} ${styles.prA} ${styles.merged}`}
            initial={{ x: '20%', y: '30%' }}
            animate={{ x: '20%', y: '30%', backgroundColor: '#e6f4ea' }}
            transition={{ duration: 0.7 }}
          >
            <div className={styles.prTitle}>PR #4: 通知機能の追加</div>
            <div className={styles.prStatus}>ステータス: マージ済み ✓</div>
          </motion.div>
          <div className={`${styles.pullRequest} ${styles.prB}`} style={{ left: '80%', top: '30%' }}>
            <div className={styles.prTitle}>PR #5: テーマ設定機能の追加</div>
            <div className={styles.prBranches}>feature/theme-settings → main</div>
          </div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <motion.div 
              className={styles.commitDot}
              initial={{ opacity: 0, top: '-10px', left: '0%' }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.5 }}
            ></motion.div>
            <div className={`${styles.branch} ${styles.featureBranchA}`} style={{ left: '-20%', opacity: 0.5 }}>
              feature/notifications
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
            <motion.div 
              className={styles.mergeArrowA}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
            ></motion.div>
          </div>
        </div>
      )
    },
    {
      title: "コンフリクトの発生",
      description: "チームメンバーBのPRでコンフリクトが発生します",
      gitCommand: "# GitHubのUI上でコンフリクトが表示される",
      animation: (
        <div className={styles.animationContainer}>
          <div className={`${styles.pullRequest} ${styles.prA} ${styles.merged}`} style={{ left: '20%', top: '30%', backgroundColor: '#e6f4ea' }}>
            <div className={styles.prTitle}>PR #4: 通知機能の追加</div>
            <div className={styles.prStatus}>ステータス: マージ済み ✓</div>
          </div>
          <motion.div 
            className={`${styles.pullRequest} ${styles.prB} ${styles.conflict}`}
            initial={{ x: '80%', y: '30%' }}
            animate={{ x: '80%', y: '30%', backgroundColor: '#ffeef0' }}
            transition={{ duration: 0.7 }}
          >
            <div className={styles.prTitle}>PR #5: テーマ設定機能の追加</div>
            <div className={styles.prStatus}>ステータス: コンフリクト発生 ⚠</div>
            <div className={styles.conflictFile}>AppContext.js にコンフリクトがあります</div>
            <motion.button 
              className={styles.viewConflictButton}
              onClick={() => {
                setCurrentConflict({
                  filename: 'AppContext.js',
                  content: `<<<<<<< HEAD
const AppContext = createContext({
  user: null,
  // 通知機能
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {}
});
=======
const AppContext = createContext({
  user: null,
  // テーマ設定機能
  theme: 'light',
  toggleTheme: () => {}
});
>>>>>>> feature/theme-settings`,
                  localChanges: `const AppContext = createContext({
  user: null,
  // 通知機能
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {}
});`,
                  incomingChanges: `const AppContext = createContext({
  user: null,
  // テーマ設定機能
  theme: 'light',
  toggleTheme: () => {}
});`,
                  localLines: [2, 3, 4, 5, 6],
                  incomingLines: [9, 10, 11, 12, 13]
                });
                setShowConflictResolver(true);
              }}
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              コンフリクトを確認
            </motion.button>
          </motion.div>
          
          {showConflictResolver && (
            <motion.div 
              className={styles.resolverWrapper}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              style={{ position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%, -50%)', width: '90%', zIndex: 10 }}
            >
              <ConflictResolver 
                conflict={currentConflict} 
                onResolve={(resolvedContent) => {
                  setShowConflictResolver(false);
                  // ここで解決されたコードを使って何か処理することも可能
                }}
              />
              <button 
                className={styles.closeButton} 
                onClick={() => setShowConflictResolver(false)}
              >
                閉じる
              </button>
            </motion.div>
          )}
          
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={styles.commitDot} style={{ top: '-10px', left: '0%' }}></div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
            </div>
            <motion.div 
              className={`${styles.conflictMarker}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              !
            </motion.div>
          </div>
        </div>
      )
    },
    {
      title: "コンフリクト解決",
      description: "チームメンバーBはコンフリクトを解決します",
      gitCommand: "# チームメンバーB\ngit checkout feature/theme-settings\ngit pull origin main\n# コンフリクト解決\ngit add .\ngit commit -m 'Merge main and resolve conflicts'\ngit push origin feature/theme-settings",
      animation: (
        <div className={styles.animationContainer}>
          <div className={styles.teamMember} style={{ left: '80%' }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.label}>チームメンバーB</div>
            <div className={styles.terminal}>
              <code>$ git checkout feature/theme-settings</code>
              <code>$ git pull origin main</code>
              <code>$ vim AppContext.js # コンフリクト解決</code>
              <code>$ git add .</code>
              <code>$ git commit -m 'Merge main and resolve conflicts'</code>
              <code>$ git push origin feature/theme-settings</code>
            </div>
          </div>
          
          {!showConflictResolver ? (
            <motion.div 
              className={styles.code} 
              style={{ left: '50%', top: '30%' }}
              initial={{ opacity: 1 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className={styles.filename}>AppContext.js (解決後)</div>
              <pre>{`const AppContext = createContext({
  user: null,
  // 通知機能
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {},
  // テーマ設定機能
  theme: 'light',
  toggleTheme: () => {}
});`}</pre>
              <motion.button 
                className={styles.detailButton}
                onClick={() => {
                  setCurrentConflict({
                    filename: 'AppContext.js',
                    content: `<<<<<<< HEAD
const AppContext = createContext({
  user: null,
  // 通知機能
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {}
});
=======
const AppContext = createContext({
  user: null,
  // テーマ設定機能
  theme: 'light',
  toggleTheme: () => {}
});
>>>>>>> feature/theme-settings`,
                    localChanges: `const AppContext = createContext({
  user: null,
  // 通知機能
  notifications: [],
  addNotification: () => {},
  markAsRead: () => {}
});`,
                    incomingChanges: `const AppContext = createContext({
  user: null,
  // テーマ設定機能
  theme: 'light',
  toggleTheme: () => {}
});`,
                    localLines: [2, 3, 4, 5, 6],
                    incomingLines: [9, 10, 11, 12, 13]
                  });
                  setShowConflictResolver(true);
                }}
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                コンフリクト解決の詳細を見る
              </motion.button>
            </motion.div>
          ) : (
            <motion.div 
              className={styles.resolverWrapper}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <ConflictResolver 
                conflict={currentConflict} 
                onResolve={(resolvedContent) => {
                  setShowConflictResolver(false);
                  // ここで解決されたコードを使って何か処理することも可能
                }}
              />
              <button 
                className={styles.closeButton} 
                onClick={() => setShowConflictResolver(false)}
              >
                閉じる
              </button>
            </motion.div>
          )}

          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={styles.commitDot} style={{ top: '-10px', left: '0%' }}></div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%' }}>
              feature/theme-settings
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
              <motion.div 
                className={styles.commitDot}
                initial={{ opacity: 0, top: '-10px', left: '70%' }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3, delay: 2 }}
              ></motion.div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "コンフリクト解決後のマージ",
      description: "コンフリクトが解決され、PRがマージされます",
      gitCommand: "# GitHubのUIで2つ目のPRをマージ",
      animation: (
        <div className={styles.animationContainer}>
          <div className={`${styles.pullRequest} ${styles.prA} ${styles.merged}`} style={{ left: '20%', top: '30%', backgroundColor: '#e6f4ea', opacity: 0.7 }}>
            <div className={styles.prTitle}>PR #4: 通知機能の追加</div>
            <div className={styles.prStatus}>ステータス: マージ済み ✓</div>
          </div>
          <motion.div 
            className={`${styles.pullRequest} ${styles.prB}`}
            initial={{ backgroundColor: '#ffeef0', x: '80%', y: '30%' }}
            animate={{ backgroundColor: '#e6f4ea', x: '80%', y: '30%' }}
            transition={{ duration: 1 }}
          >
            <div className={styles.prTitle}>PR #5: テーマ設定機能の追加</div>
            <div className={styles.prStatus}>ステータス: マージ済み ✓</div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={styles.commitDot} style={{ top: '-10px', left: '0%' }}></div>
            <motion.div 
              className={styles.commitDot}
              initial={{ opacity: 0, top: '-10px', left: '40%' }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 1 }}
            ></motion.div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%', opacity: 0.5 }}>
              feature/theme-settings
              <div className={styles.commitDot} style={{ top: '-10px' }}></div>
              <div className={styles.commitDot} style={{ top: '-10px', left: '70%' }}></div>
            </div>
            <motion.div 
              className={styles.mergeArrowB}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
            ></motion.div>
          </div>
        </div>
      )
    },
    {
      title: "完了状態",
      description: "両方の機能が統合され、イシューが完了します",
      gitCommand: "git checkout main\ngit pull origin main",
      animation: (
        <div className={styles.animationContainer}>
          <motion.div 
            className={styles.completion}
            initial={{ opacity: 0, y: '40%' }}
            animate={{ opacity: 1, y: '40%' }}
            transition={{ duration: 0.7 }}
          >
            <h3>開発完了 ✓</h3>
            <div className={styles.completionDetails}>
              <div>✓ 通知機能の追加 (イシュー #2)</div>
              <div>✓ テーマ設定機能の追加 (イシュー #3)</div>
              <div>✓ コンフリクトの解決</div>
            </div>
          </motion.div>
          <div className={styles.repository} style={{ right: '20%', top: '70%' }}>
            <div className={styles.repoLabel}>GitHubリポジトリ</div>
            <div className={styles.branch}>main</div>
            <div className={styles.commitDot} style={{ top: '-10px', left: '0%' }}></div>
            <div className={styles.commitDot} style={{ top: '-10px', left: '40%' }}></div>
            <div className={`${styles.branch} ${styles.featureBranchA}`} style={{ left: '-20%', opacity: 0.3 }}>
              feature/notifications (削除済み)
            </div>
            <div className={`${styles.branch} ${styles.featureBranchB}`} style={{ left: '20%', opacity: 0.3 }}>
              feature/theme-settings (削除済み)
            </div>
          </div>
          <div className={styles.teamMember} style={{ left: '20%', opacity: 0.7 }}>
            <div className={styles.avatar}>A</div>
            <div className={styles.terminal}>
              <code>$ git checkout main</code>
              <code>$ git pull origin main</code>
              <code>$ git branch -d feature/notifications</code>
            </div>
          </div>
          <div className={styles.teamMember} style={{ left: '80%', opacity: 0.7 }}>
            <div className={styles.avatar}>B</div>
            <div className={styles.terminal}>
              <code>$ git checkout main</code>
              <code>$ git pull origin main</code>
              <code>$ git branch -d feature/theme-settings</code>
            </div>
          </div>
        </div>
      )
    }
  ];

  const steps = selectedScenario === 'basic' ? basicScenarioSteps : conflictScenarioSteps;
  
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className={styles.teamGitFlow}>
      <h2 className={styles.title}>チーム開発のGitフロー</h2>
      
      <div className={styles.scenarioSelector}>
        <button 
          className={`${styles.scenarioButton} ${selectedScenario === 'basic' ? styles.active : ''}`}
          onClick={() => { setSelectedScenario('basic'); setCurrentStep(0); }}
        >
          基本シナリオ: 機能実装フロー
        </button>
        <button 
          className={`${styles.scenarioButton} ${selectedScenario === 'conflict' ? styles.active : ''}`}
          onClick={() => { setSelectedScenario('conflict'); setCurrentStep(0); }}
        >
          応用シナリオ: コンフリクト解決
        </button>
      </div>
      
      <div className={styles.viewToggle}>
        <button 
          className={`${styles.viewButton} ${viewMode === 'animation' ? styles.active : ''}`}
          onClick={() => setViewMode('animation')}
        >
          アニメーション表示
        </button>
        <button 
          className={`${styles.viewButton} ${viewMode === 'details' ? styles.active : ''}`}
          onClick={() => setViewMode('details')}
        >
          詳細表示
        </button>
      </div>
      
      <div className={styles.progressBar}>
        {steps.map((step, index) => (
          <div 
            key={index}
            className={`${styles.progressStep} ${index <= currentStep ? styles.completed : ''} ${index === currentStep ? styles.active : ''}`}
            onClick={() => setCurrentStep(index)}
          >
            <span className={styles.stepNumber}>{index + 1}</span>
            <span className={styles.stepTitle}>{step.title}</span>
          </div>
        ))}
      </div>
      
      <div className={styles.contentBox}>
        <h3 className={styles.stepTitle}>{steps[currentStep].title}</h3>
        <p className={styles.description}>{steps[currentStep].description}</p>
        
        {viewMode === 'animation' ? (
          <div className={styles.animationWrapper}>
            {steps[currentStep].animation}
          </div>
        ) : (
          <div className={styles.detailsWrapper}>
            <div className={styles.gitCommandBlock}>
              <h4>Git コマンド</h4>
              <pre>{steps[currentStep].gitCommand}</pre>
            </div>
            <div className={styles.explanationBlock}>
              <h4>ポイント</h4>
              <ul>
                <li>このステップでは、{steps[currentStep].description.toLowerCase()}</li>
                <li>各メンバーは自分の作業内容を常に他のメンバーと共有することが重要です</li>
                <li>コミットメッセージは具体的に書き、何を変更したかが分かるようにしましょう</li>
              </ul>
            </div>
          </div>
        )}
      </div>
      
      <div className={styles.navigation}>
        <button 
          className={styles.navButton} 
          onClick={prevStep} 
          disabled={currentStep === 0}
        >
          前へ
        </button>
        <div className={styles.stepCounter}>
          ステップ {currentStep + 1} / {steps.length}
        </div>
        <button 
          className={styles.navButton} 
          onClick={nextStep} 
          disabled={currentStep === steps.length - 1}
        >
          次へ
        </button>
      </div>
    </div>
  );
};

export default TeamGitFlow;