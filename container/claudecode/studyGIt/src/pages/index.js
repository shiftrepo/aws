import React, { useState } from 'react';
import Link from 'next/link';
import styles from './index.module.css';

export default function Home() {
  const [username, setUsername] = useState('');
  
  return (
    <div className={styles.main}>
      <h1 className={styles.title}>
        Git<span className={styles.highlight}>Playground</span>
      </h1>
      
      <p className={styles.description}>
        チーム開発でのGit操作を楽しく学べるインタラクティブサイト
      </p>

      <div className={styles.card}>
        <h2>Gitを学ぼう！</h2>
        <p>ファイルの追加、変更、削除などのGit操作を実際に体験できます。</p>
        <p>チーム開発のシミュレーションで他のメンバーとの協力作業も学べます。</p>
        
        <div className={styles.inputGroup}>
          <label htmlFor="username">あなたの名前:</label>
          <input 
            id="username"
            type="text" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)}
            placeholder="名前を入力してください"
          />
        </div>
        
        <Link href={`/playground${username ? `?username=${encodeURIComponent(username)}` : ''}`}>
          <a className={styles.button}>
            遊び方を学ぶ
          </a>
        </Link>
      </div>

      <div className={styles.features}>
        <div className={styles.featureCard}>
          <h3>ファイル操作</h3>
          <p>ファイルの追加、変更、削除操作を体験</p>
        </div>
        <div className={styles.featureCard}>
          <h3>コミット</h3>
          <p>変更をコミットして記録する方法を学ぶ</p>
        </div>
        <div className={styles.featureCard}>
          <h3>ブランチ</h3>
          <p>ブランチを使ったチーム開発のワークフロー</p>
        </div>
        <div className={styles.featureCard}>
          <h3>コンフリクト解決</h3>
          <p>競合の発生と解決方法を理解する</p>
        </div>
      </div>
    </div>
  );
}