import React, { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [username, setUsername] = useState('');
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ marginBottom: '1rem' }}>
        Git<span style={{ color: '#0070f3' }}>Playground</span>
      </h1>
      
      <p style={{ marginBottom: '2rem', textAlign: 'center' }}>
        チーム開発でのGit操作を楽しく学べるインタラクティブサイト
      </p>

      <div style={{ 
        padding: '1.5rem', 
        border: '1px solid #eaeaea', 
        borderRadius: '10px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        width: '80%',
        maxWidth: '500px'
      }}>
        <h2>Gitを学ぼう！</h2>
        <p>ファイルの追加、変更、削除などのGit操作を実際に体験できます。</p>
        <p>チーム開発のシミュレーションで他のメンバーとの協力作業も学べます。</p>
        
        <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '0.5rem' }}>あなたの名前:</label>
          <input 
            id="username"
            type="text" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)}
            placeholder="名前を入力してください"
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ccc',
              marginBottom: '1rem'
            }}
          />
        </div>
        
        <Link href={`/playground${username ? `?username=${encodeURIComponent(username)}` : ''}`}>
          <a style={{
            backgroundColor: '#0070f3',
            color: 'white',
            padding: '0.75rem 1rem',
            borderRadius: '4px',
            textDecoration: 'none',
            display: 'inline-block',
            fontWeight: 'bold'
          }}>
            遊び方を学ぶ
          </a>
        </Link>
      </div>

      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '1rem',
        marginTop: '2rem',
        width: '80%',
        maxWidth: '800px'
      }}>
        <div style={{ 
          flex: '1 1 200px', 
          padding: '1rem', 
          border: '1px solid #eaeaea', 
          borderRadius: '5px' 
        }}>
          <h3>ファイル操作</h3>
          <p>ファイルの追加、変更、削除操作を体験</p>
        </div>
        <div style={{ 
          flex: '1 1 200px', 
          padding: '1rem', 
          border: '1px solid #eaeaea', 
          borderRadius: '5px' 
        }}>
          <h3>コミット</h3>
          <p>変更をコミットして記録する方法を学ぶ</p>
        </div>
        <div style={{ 
          flex: '1 1 200px', 
          padding: '1rem', 
          border: '1px solid #eaeaea', 
          borderRadius: '5px' 
        }}>
          <h3>ブランチ</h3>
          <p>ブランチを使ったチーム開発のワークフロー</p>
        </div>
        <div style={{ 
          flex: '1 1 200px', 
          padding: '1rem', 
          border: '1px solid #eaeaea', 
          borderRadius: '5px' 
        }}>
          <h3>コンフリクト解決</h3>
          <p>競合の発生と解決方法を理解する</p>
        </div>
      </div>
    </div>
  );
}