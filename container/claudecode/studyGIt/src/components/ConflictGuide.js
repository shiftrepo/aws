import React from 'react';

/**
 * コンフリクト解決の詳細手順をまとめた説明コンポーネント
 * チュートリアル的な役割を果たし、初心者向けに各ステップを視覚的に説明します
 */
export default function ConflictGuide() {
  return (
    <div style={{
      backgroundColor: '#f8f9fa',
      padding: '1.5rem',
      borderRadius: '8px',
      marginTop: '2rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h2 style={{ color: '#333', borderBottom: '2px solid #6366f1', paddingBottom: '0.5rem' }}>
        Git コンフリクト解決ガイド 🛠️
      </h2>

      <p style={{ fontSize: '1.1rem', color: '#555' }}>
        Git を使っていると避けられないのが「コンフリクト（競合）」です。怖がる必要はありません！
        このガイドでは、コンフリクトの解決方法をステップバイステップで説明します。
      </p>

      <h3 style={{ color: '#4f46e5', marginTop: '1.5rem' }}>1. コンフリクトとは何か？</h3>
      <p>
        コンフリクトとは、同じファイルの同じ部分が2つの異なるブランチで変更された場合に発生する状況です。
        Git は自動的に変更をマージできないため、人間の判断が必要になります。
      </p>
      <div style={{ 
        backgroundColor: '#e0e7ff', 
        padding: '0.75rem', 
        borderRadius: '6px',
        borderLeft: '4px solid #6366f1',
        marginBottom: '1rem'
      }}>
        <strong>例:</strong> あなたと他の開発者が同時に同じファイルの同じ行を編集し、両方の変更をマージする場合
      </div>

      <h3 style={{ color: '#4f46e5', marginTop: '1.5rem' }}>2. コンフリクトの検出方法</h3>
      <p>
        コンフリクトは通常、<code>git merge</code> や <code>git pull</code> コマンドを実行したときに発生します。
        Git はコンフリクトを検出すると、次のようなメッセージを表示します：
      </p>
      <pre style={{ 
        backgroundColor: '#282c34', 
        color: '#abb2bf',
        padding: '1rem',
        borderRadius: '6px',
        overflowX: 'auto',
        fontSize: '0.9rem',
        lineHeight: '1.5'
      }}>
{`$ git pull origin main
Auto-merging sample.js
CONFLICT (content): Merge conflict in sample.js
Automatic merge failed; fix conflicts and then commit the result.`}
      </pre>

      <h3 style={{ color: '#4f46e5', marginTop: '1.5rem' }}>3. コンフリクトマーカーの理解</h3>
      <p>
        Git はコンフリクトが発生したファイルに特別なマーカーを挿入します：
      </p>
      <pre style={{ 
        backgroundColor: '#282c34', 
        color: '#abb2bf',
        padding: '1rem',
        borderRadius: '6px',
        overflowX: 'auto',
        fontSize: '0.9rem',
        lineHeight: '1.5'
      }}>
{`<<<<<<< HEAD
// あなたの変更（現在のブランチの内容）
const greeting = "こんにちは";
=======
// 他の開発者の変更（マージしようとしているブランチの内容）
const greeting = "Hello";
>>>>>>> feature-branch`}
      </pre>
      <p>
        マーカーの意味：
      </p>
      <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem' }}>
        <li><code>{'<<<<<<< HEAD'}</code> - コンフリクト開始位置、HEADはあなたの現在のブランチ</li>
        <li><code>{'======='}</code> - 変更の区切り</li>
        <li><code>{'>>>>>>> feature-branch'}</code> - コンフリクト終了位置、feature-branchは変更を取り込もうとしているブランチ</li>
      </ul>

      <h3 style={{ color: '#4f46e5', marginTop: '1.5rem' }}>4. コンフリクトの解決手順</h3>
      <ol style={{ paddingLeft: '1.5rem' }}>
        <li style={{ marginBottom: '1rem' }}>
          <strong>コンフリクトファイルの確認</strong> - <code>git status</code> で競合ファイルを確認
          <pre style={{ 
            backgroundColor: '#282c34', 
            color: '#abb2bf',
            padding: '0.75rem',
            borderRadius: '6px',
            overflowX: 'auto',
            fontSize: '0.9rem',
            marginTop: '0.5rem'
          }}>
{`$ git status
...
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   sample.js`}
          </pre>
        </li>
        <li style={{ marginBottom: '1rem' }}>
          <strong>ファイルを編集</strong> - コンフリクトマーカーを取り除き、最終的にどのコードを残すか決定
          <div style={{ 
            backgroundColor: '#ecfdf5', 
            padding: '0.75rem', 
            borderRadius: '6px',
            borderLeft: '4px solid #10b981',
            marginTop: '0.5rem'
          }}>
            <strong>ヒント:</strong> 3つの選択肢があります：
            <ol type="a" style={{ marginTop: '0.5rem', marginBottom: '0' }}>
              <li>あなたの変更を残す（HEADの内容）</li>
              <li>相手の変更を採用する（feature-branchの内容）</li>
              <li>両方の変更を統合して新しいコードを書く</li>
            </ol>
          </div>
        </li>
        <li style={{ marginBottom: '1rem' }}>
          <strong>マーカーを削除</strong> - すべてのコンフリクトマーカー（<code>{'<<<<<<< HEAD'}</code>, <code>{'======='}</code>, <code>{'>>>>>>> feature-branch'}</code>）を必ず削除
        </li>
        <li style={{ marginBottom: '1rem' }}>
          <strong>解決済みファイルを追加</strong> - <code>git add &lt;file&gt;</code> で解決したファイルをステージング
          <pre style={{ 
            backgroundColor: '#282c34', 
            color: '#abb2bf',
            padding: '0.75rem',
            borderRadius: '6px',
            overflowX: 'auto',
            fontSize: '0.9rem',
            marginTop: '0.5rem'
          }}>
{`$ git add sample.js`}
          </pre>
        </li>
        <li>
          <strong>コミットの作成</strong> - <code>git commit</code> でマージを完了
          <pre style={{ 
            backgroundColor: '#282c34', 
            color: '#abb2bf',
            padding: '0.75rem',
            borderRadius: '6px',
            overflowX: 'auto',
            fontSize: '0.9rem',
            marginTop: '0.5rem'
          }}>
{`$ git commit -m "Resolve merge conflict in sample.js"`}
          </pre>
        </li>
      </ol>

      <h3 style={{ color: '#4f46e5', marginTop: '1.5rem' }}>5. コンフリクト解決のコツ</h3>
      <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem' }}>
        <li>コードの意図を理解してから解決する</li>
        <li>不明な場合は、変更を加えた人に確認する</li>
        <li>複雑な場合は、マージツール（Visual Studio Code, GitKraken, SourceTreeなど）を使用する</li>
        <li>大きな変更を行う前に、最新の変更を取り込んでおくと競合を減らせる</li>
      </ul>

      <div style={{ 
        backgroundColor: '#fff9db', 
        padding: '1rem', 
        borderRadius: '6px',
        borderLeft: '4px solid #f59f00',
        marginTop: '2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem'
      }}>
        <span style={{ fontSize: '1.5rem' }}>💡</span>
        <div>
          <strong>チームリーダーメモ:</strong> コンフリクトは日常的に発生するものです。チーム開発では頻繁に起こりますが、腕を抜いて解決できるようになってください。困ったときは遠慮なく質問してくださいね。
        </div>
      </div>
    </div>
  );
}