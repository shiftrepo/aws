import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styles from './GitFlowGuide.module.css';

const GitFlowGuide = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [viewMode, setViewMode] = useState('graphic'); // 'ascii' または 'graphic'
  const [animationEnabled, setAnimationEnabled] = useState(true);
  
  const steps = [
    {
      title: "Git Flowとは",
      content: (
        <>
          <div className={styles.section}>
            <h3>Gitフローとは何か？</h3>
            <p>Git Flowは、ソフトウェア開発のためのブランチ戦略モデルです。このモデルでは、主に以下のブランチを使用します：</p>
            <ul>
              <li><strong className={styles.mainBranch}>main/master</strong>: 本番環境に対応するブランチ (本番B面)。リリースされたコードのみが存在します。</li>
              <li><strong className={styles.developBranch}>develop</strong>: 開発の基本となるブランチ (開発A面)。次のリリースに向けた開発が進行します。</li>
              <li><strong className={styles.featureBranch}>feature</strong>: 新機能開発用のブランチ。developから分岐し、完了したらdevelopにマージします。</li>
              <li><strong className={styles.releaseBranch}>release</strong>: リリース準備用のブランチ。developから分岐し、リリース準備完了後にmainとdevelopの両方にマージします。</li>
              <li><strong className={styles.hotfixBranch}>hotfix</strong>: 緊急修正用のブランチ。mainから分岐し、修正後はmainとdevelopの両方にマージします。</li>
            </ul>
          </div>
          <div className={styles.flowDiagram}>
            <img src="https://nvie.com/img/git-model@2x.png" alt="Git Flow Diagram" className={styles.diagram}/>
            <div className={styles.diagramCaption}>Git Flow モデル（Vincent Driessen氏による原典的な図）</div>
          </div>
        </>
      )
    },
    {
      title: "開発の開始 - developブランチ",
      development: "プロジェクト計画・基本設計",
      content: (
        <div className={styles.section}>
          <h3>開発の基盤 - developブランチ</h3>
          <p>プロジェクト開始時、最初にmainブランチからdevelopブランチを作成します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout -b develop main
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>ファイルの状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
function app() {
  console.log("アプリケーション起動");
  return true;
}

module.exports = app;`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                              ↓
  develop (開発A面)         o───────────────────────────────────
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '210px', top: '16px', height: '40px', width: '2px', backgroundColor: '#3498db', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', bottom: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: 'transparent transparent #3498db transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '180px', fontSize: '10px', color: '#666' }}>初期コミット</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "機能開発 - featureブランチ",
      development: "詳細設計・製造",
      content: (
        <div className={styles.section}>
          <h3>新機能の開発 - featureブランチ</h3>
          <p>新機能を開発する際は、developブランチからfeatureブランチを作成します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout -b feature/login-system develop
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>ファイルの変更：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
function app() {
  console.log("アプリケーション起動");
  `}<span className={styles.newCode}>{`initializeLogin(); // 新機能：ログイン初期化`}</span>{`
  return true;
}

`}<span className={styles.newCode}>{`// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}
`}</span>{`
module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>login.js（新規ファイル）</div>
              <pre>
                <code className={styles.newCode}>
                  {`// ログイン機能モジュール
function loginUser(username, password) {
  console.log("ユーザーログイン試行:", username);
  return username && password;
}

function logoutUser() {
  console.log("ユーザーログアウト");
  return true;
}

module.exports = {
  loginUser,
  logoutUser
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o───────────────────────────────────
                              ↓
  feature/                   o─────────────────
  login-system   
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '180px', fontSize: '10px', color: '#666' }}>初期化</div>
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '210px', top: '76px', height: '30px', width: '2px', backgroundColor: '#2ecc71' }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', bottom: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: 'transparent transparent #2ecc71 transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameFeature}>feature/<br/>login-system</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchFeature} style={{ width: '200px', left: '150px' }}>
                    <div className={styles.graphCommit} style={{ left: '50px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '30px', fontSize: '10px', color: '#666' }}>ログイン機能実装</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "featureブランチをdevelopにマージ",
      development: "単体試験・結合試験",
      content: (
        <div className={styles.section}>
          <h3>機能実装完了 - featureブランチのマージ</h3>
          <p>機能の開発とテストが完了したら、featureブランチをdevelopブランチにマージします。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`$ git checkout develop
$ git merge --no-ff feature/login-system
$ git branch -d feature/login-system`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>developブランチのファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
function app() {
  console.log("アプリケーション起動");
  `}<span className={styles.highlightedCode}>{`initializeLogin(); // 新機能：ログイン初期化`}</span>{`
  return true;
}

`}<span className={styles.highlightedCode}>{`// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}
`}</span>{`
module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>login.js</div>
              <pre>
                <code className={styles.highlightedCode}>
                  {`// ログイン機能モジュール
function loginUser(username, password) {
  console.log("ユーザーログイン試行:", username);
  return username && password;
}

function logoutUser() {
  console.log("ユーザーログアウト");
  return true;
}

module.exports = {
  loginUser,
  logoutUser
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o────────o──────────────────────────
                                    ↑
  feature/                     o─────┘
  login-system   
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '300px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '280px', fontSize: '10px', color: '#666' }}>feature/login-systemをマージ</div>
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameFeature}>feature/<br/>login-system</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchFeature} style={{ width: '110px', left: '180px' }}>
                    <div className={styles.graphCommit} style={{ left: '100px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '280px', top: '100px', height: '60px', width: '2px', transform: 'rotate(-45deg)', backgroundColor: '#2ecc71', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#2ecc71 transparent transparent transparent', transform: 'rotate(0deg)' }} />
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "別の機能開発 - 2つ目のfeatureブランチ",
      development: "詳細設計・製造 (並行開発)",
      content: (
        <div className={styles.section}>
          <h3>別の機能開発 - featureブランチを並行して作成</h3>
          <p>別の機能を並行して開発するために、新たなfeatureブランチを作成します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout -b feature/user-profile develop
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>ファイルの変更：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
function app() {
  console.log("アプリケーション起動");
  initializeLogin(); // 新機能：ログイン初期化
  `}<span className={styles.newCode}>{`initializeUserProfile(); // 新機能：ユーザープロファイル初期化`}</span>{`
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

`}<span className={styles.newCode}>{`// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}
`}</span>{`
module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>user-profile.js（新規ファイル）</div>
              <pre>
                <code className={styles.newCode}>
                  {`// ユーザープロファイル機能モジュール
function getUserProfile(userId) {
  console.log("ユーザープロファイル取得:", userId);
  return { userId, name: "サンプルユーザー", email: "user@example.com" };
}

function updateUserProfile(userId, profileData) {
  console.log("ユーザープロファイル更新:", userId);
  return true;
}

module.exports = {
  getUserProfile,
  updateUserProfile
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o────────o──────────────────────────
                                      ↓
  feature/                            o─────────────
  user-profile    
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '300px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '310px', top: '56px', height: '40px', width: '2px', backgroundColor: '#2ecc71', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', bottom: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: 'transparent transparent #2ecc71 transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameFeature}>feature/<br/>user-profile</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchFeature} style={{ width: '100px', left: '250px' }}>
                    <div className={styles.graphCommit} style={{ left: '50px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '30px', fontSize: '10px', color: '#666' }}>プロファイル機能実装</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "2つ目のfeatureブランチをdevelopにマージ",
      development: "単体試験・結合試験 (並行開発)",
      content: (
        <div className={styles.section}>
          <h3>2つ目の機能実装完了 - featureブランチのマージ</h3>
          <p>ユーザープロファイル機能の開発とテストが完了したら、featureブランチをdevelopブランチにマージします。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`$ git checkout develop
$ git merge --no-ff feature/user-profile
$ git branch -d feature/user-profile`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>developブランチのファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
function app() {
  console.log("アプリケーション起動");
  initializeLogin(); // 新機能：ログイン初期化
  `}<span className={styles.highlightedCode}>{`initializeUserProfile(); // 新機能：ユーザープロファイル初期化`}</span>{`
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

`}<span className={styles.highlightedCode}>{`// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}
`}</span>{`
module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>user-profile.js</div>
              <pre>
                <code className={styles.highlightedCode}>
                  {`// ユーザープロファイル機能モジュール
function getUserProfile(userId) {
  console.log("ユーザープロファイル取得:", userId);
  return { userId, name: "サンプルユーザー", email: "user@example.com" };
}

function updateUserProfile(userId, profileData) {
  console.log("ユーザープロファイル更新:", userId);
  return true;
}

module.exports = {
  getUserProfile,
  updateUserProfile
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o────────o───────o─────────────────
                                           ↑
  feature/                            o─────┘
  user-profile    
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameFeature}>feature/<br/>user-profile</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchFeature} style={{ width: '110px', left: '260px' }}>
                    <div className={styles.graphCommit} style={{ left: '100px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '360px', top: '100px', height: '60px', width: '2px', transform: 'rotate(-45deg)', backgroundColor: '#2ecc71', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', right: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#2ecc71 transparent transparent transparent', transform: 'rotate(45deg)' }} />
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "リリース準備 - releaseブランチの作成",
      development: "総合試験開始",
      content: (
        <div className={styles.section}>
          <h3>リリース準備 - releaseブランチ</h3>
          <p>機能開発が完了し、リリース準備を始める段階でreleaseブランチを作成します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout -b release/1.0.0 develop
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>releaseブランチでのファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
`}<span className={styles.newCode}>{`// バージョン 1.0.0`}</span>{`
function app() {
  console.log("アプリケーション起動");
  initializeLogin(); // 新機能：ログイン初期化
  initializeUserProfile(); // 新機能：ユーザープロファイル初期化
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}

module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>package.json（一部）</div>
              <pre>
                <code>
                  {`{
  "name": "sample-app",
  `}<span className={styles.oldCode}>{`"version": "0.9.0",`}</span>
                  <span className={styles.newCode}>{`"version": "1.0.0",`}</span>{`
  "description": "サンプルアプリケーション",
  ...
}`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o────────o───────o─────────────────
                                                 ↓
  release/                                      o────
  1.0.0  
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '390px', top: '56px', height: '40px', width: '2px', backgroundColor: '#f39c12', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', bottom: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: 'transparent transparent #f39c12 transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameRelease}>release/<br/>1.0.0</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchRelease} style={{ width: '50px', left: '360px' }}>
                    <div className={styles.graphCommit} style={{ left: '40px' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "バグ修正 - releaseブランチでの修正",
      development: "総合試験・修正",
      content: (
        <div className={styles.section}>
          <h3>リリース前バグ修正 - releaseブランチでの修正</h3>
          <p>リリース準備中に発見されたバグは、releaseブランチ上で修正します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# releaseブランチ上で修正
$ git commit -am "ログイン処理のバグを修正"`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>バグ修正後のファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>login.js</div>
              <pre>
                <code>
                  {`// ログイン機能モジュール
function loginUser(username, password) {
  console.log("ユーザーログイン試行:", username);
  `}<span className={styles.oldCode}>{`return username && password;`}</span>
                  <span className={styles.newCode}>{`return username && password && username.length > 0 && password.length > 0;`}</span>{`
}

function logoutUser() {
  console.log("ユーザーログアウト");
  return true;
}

module.exports = {
  loginUser,
  logoutUser
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o───────────────────────────────────
                
  develop (開発A面)         o────────o───────o─────────────────
                                                 
  release/                                      o────o─
  1.0.0  
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameRelease}>release/<br/>1.0.0</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchRelease} style={{ width: '100px', left: '360px' }}>
                    <div className={styles.graphCommit} style={{ left: '40px' }} />
                    <div className={styles.graphCommit} style={{ left: '90px' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "リリース完了 - mainとdevelopへのマージ",
      development: "総合試験完了・リリース",
      content: (
        <div className={styles.section}>
          <h3>リリース完了 - releaseブランチをマージ</h3>
          <p>リリース準備が完了したら、releaseブランチをmainとdevelopの両方にマージします。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# mainにマージ
$ git checkout main
$ git merge --no-ff release/1.0.0
$ git tag -a v1.0.0 -m "バージョン1.0.0リリース"

# developにもマージ（バグ修正を反映）
$ git checkout develop
$ git merge --no-ff release/1.0.0

# releaseブランチ削除
$ git branch -d release/1.0.0`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>mainブランチのファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code className={styles.highlightedCode}>
                  {`// メインアプリケーションファイル
// バージョン 1.0.0
function app() {
  console.log("アプリケーション起動");
  initializeLogin(); // 新機能：ログイン初期化
  initializeUserProfile(); // 新機能：ユーザープロファイル初期化
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}

module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>login.js</div>
              <pre>
                <code className={styles.highlightedCode}>
                  {`// ログイン機能モジュール
function loginUser(username, password) {
  console.log("ユーザーログイン試行:", username);
  return username && password && username.length > 0 && password.length > 0;
}

function logoutUser() {
  console.log("ユーザーログアウト");
  return true;
}

module.exports = {
  loginUser,
  logoutUser
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o──────────────────────o─(v1.0.0)───
                                                  ↑
  develop (開発A面)         o────────o───────o────┴───o────────
                                                 ↑
  release/                                      o────o┘
  1.0.0  
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '480px' }} />
                    <div className={styles.graphTag} style={{ left: '495px' }}>v1.0.0</div>
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '460px', top: '16px', height: '100px', width: '2px', transform: 'rotate(45deg)', backgroundColor: '#f39c12', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#f39c12 transparent transparent transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                    <div className={styles.graphCommit} style={{ left: '520px' }} />
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '450px', top: '56px', height: '60px', width: '2px', transform: 'rotate(125deg)', backgroundColor: '#f39c12', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#f39c12 transparent transparent transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameRelease}>release/<br/>1.0.0</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchRelease} style={{ width: '100px', left: '360px' }}>
                    <div className={styles.graphCommit} style={{ left: '40px' }} />
                    <div className={styles.graphCommit} style={{ left: '90px' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "本番環境のバグ修正 - hotfixブランチ",
      development: "緊急対応・バグ修正",
      content: (
        <div className={styles.section}>
          <h3>本番バグ修正 - hotfixブランチ</h3>
          <p>本番環境で重大なバグが発見された場合、mainブランチからhotfixブランチを作成して緊急修正します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout -b hotfix/1.0.1 main
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>hotfixブランチでの修正：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code>
                  {`// メインアプリケーションファイル
// `}<span className={styles.oldCode}>{`バージョン 1.0.0`}</span>
                  <span className={styles.newCode}>{`バージョン 1.0.1`}</span>{`
function app() {
  console.log("アプリケーション起動");
  `}<span className={styles.newCode}>{`try {`}</span>{`
  initializeLogin(); // 新機能：ログイン初期化
  initializeUserProfile(); // 新機能：ユーザープロファイル初期化
  `}<span className={styles.newCode}>{`} catch (error) {
    console.error("初期化エラー:", error);
  }`}</span>{`
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}

module.exports = app;`}
                </code>
              </pre>
            </div>
            <div className={styles.file}>
              <div className={styles.fileName}>package.json（一部）</div>
              <pre>
                <code>
                  {`{
  "name": "sample-app",
  `}<span className={styles.oldCode}>{`"version": "1.0.0",`}</span>
                  <span className={styles.newCode}>{`"version": "1.0.1",`}</span>{`
  "description": "サンプルアプリケーション",
  ...
}`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o──────────────────────o──────────────
                                                    ↓
  develop (開発A面)         o────────o───────o──────o────────────
                                                   
  hotfix/                                         o─
  1.0.1                             
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '480px' }} />
                    <div className={styles.graphTag} style={{ left: '495px' }}>v1.0.0</div>
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '460px', fontSize: '10px', color: '#666' }}>releaseマージ</div>
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '490px', top: '16px', height: '40px', width: '2px', backgroundColor: '#9b59b6', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', bottom: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: 'transparent transparent #9b59b6 transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                    <div className={styles.graphCommit} style={{ left: '480px' }} />
                  </div>
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameHotfix}>hotfix/<br/>1.0.1</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchHotfix} style={{ width: '40px', left: '480px' }}>
                    <div className={styles.graphCommit} style={{ left: '30px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '10px', fontSize: '10px', color: '#666' }}>初期化例外処理追加</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "hotfixのマージ - mainとdevelopへ",
      development: "緊急修正リリース",
      content: (
        <div className={styles.section}>
          <h3>hotfix完了 - mainとdevelopへのマージ</h3>
          <p>hotfixが完了したら、mainとdevelopの両方にマージして、新しいタグを付けます。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# mainにマージ
$ git checkout main
$ git merge --no-ff hotfix/1.0.1
$ git tag -a v1.0.1 -m "バージョン1.0.1緊急修正リリース"

# developにもマージ
$ git checkout develop
$ git merge --no-ff hotfix/1.0.1

# hotfixブランチを削除
$ git branch -d hotfix/1.0.1`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>マージ後のmainブランチ：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js</div>
              <pre>
                <code className={styles.highlightedCode}>
                  {`// メインアプリケーションファイル
// バージョン 1.0.1
function app() {
  console.log("アプリケーション起動");
  try {
    initializeLogin(); // 新機能：ログイン初期化
    initializeUserProfile(); // 新機能：ユーザープロファイル初期化
  } catch (error) {
    console.error("初期化エラー:", error);
  }
  return true;
}

// 新機能：ログインシステム
function initializeLogin() {
  console.log("ログインシステム初期化");
  return true;
}

// 新機能：ユーザープロファイル
function initializeUserProfile() {
  console.log("ユーザープロファイル初期化");
  return true;
}

module.exports = app;`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o──────────────────────o───────o─(v1.0.1)──
                                                    ↑       ↑
  develop (開発A面)         o────────o───────o──────o───────┴───o────
                                                   ↑           ↑
  hotfix/                                         o───────────┘
  1.0.1                             
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <div className={styles.gitGraph}>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameMain}>main/master<br/>(本番B面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchMain}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '480px' }} />
                    <div className={styles.graphCommit} style={{ left: '580px' }} />
                    <div className={styles.graphTag} style={{ left: '595px' }}>v1.0.1</div>
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '560px', fontSize: '10px', color: '#666' }}>hotfixマージ</div>
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '560px', top: '16px', height: '100px', width: '2px', transform: 'rotate(45deg)', backgroundColor: '#9b59b6', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#9b59b6 transparent transparent transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameDevelop}>develop<br/>(開発A面)</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchDevelop}>
                    <div className={styles.graphCommit} style={{ left: '200px' }} />
                    <div className={styles.graphCommit} style={{ left: '280px' }} />
                    <div className={styles.graphCommit} style={{ left: '380px' }} />
                    <div className={styles.graphCommit} style={{ left: '480px' }} />
                    <div className={styles.graphCommit} style={{ left: '620px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '600px', fontSize: '10px', color: '#666' }}>hotfixマージ</div>
                  </div>
                </div>
                <div className={styles.graphArrow} 
                     style={{ position: 'absolute', left: '600px', top: '56px', height: '60px', width: '2px', transform: 'rotate(125deg)', backgroundColor: '#9b59b6', zIndex: 1 }}>
                  <div className={styles.arrowHead} 
                       style={{ position: 'absolute', top: '-5px', left: '-4px', borderWidth: '5px', borderStyle: 'solid', borderColor: '#9b59b6 transparent transparent transparent', transform: 'rotate(0deg)' }} />
                </div>
                <div className={styles.branchRow}>
                  <div className={styles.branchName + ' ' + styles.branchNameHotfix}>hotfix/<br/>1.0.1</div>
                  <div className={styles.graphBranch + ' ' + styles.graphBranchHotfix} style={{ width: '110px', left: '480px' }}>
                    <div className={styles.graphCommit} style={{ left: '100px' }} />
                    <div className={styles.graphCommitLabel} style={{ position: 'absolute', top: '-30px', left: '80px', fontSize: '10px', color: '#666' }}>緊急修正</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      title: "新たな開発サイクル",
      development: "次期バージョン開発計画",
      content: (
        <div className={styles.section}>
          <h3>新たな開発サイクルの開始</h3>
          <p>hotfix対応後、次の機能開発に向けた新たなサイクルが始まります。ここでまたdevelopブランチから新たなfeatureブランチを作成して開発を進めます。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                $ git checkout develop
                $ git checkout -b feature/notifications develop
              </code>
            </pre>
          </div>
          <div className={styles.flowDiagram}>
            <img src="https://nvie.com/img/git-model@2x.png" alt="Git Flow Full Diagram" className={styles.diagram}/>
            <p>Git Flowの全体像：この流れを繰り返して開発を進めていきます。図は Vincent Driessen 氏による原典的な Git Flow モデル。</p>
          </div>
        </div>
      )
    }
  ];

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
    <motion.div 
      className={styles.gitFlowGuide}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h2 
        className={styles.title}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Git Flow チュートリアル
      </motion.h2>
      
      <div className={styles.progressBar}>
        {steps.map((step, index) => (
          <motion.div 
            key={index}
            className={`${styles.progressStep} ${index <= currentStep ? styles.completed : ''} ${index === currentStep ? styles.active : ''}`}
            onClick={() => setCurrentStep(index)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index, duration: 0.3 }}
          >
            <span className={styles.stepNumber}>{index + 1}</span>
            <span className={styles.stepTitle}>{step.title}</span>
          </motion.div>
        ))}
      </div>
      
      <motion.div 
        className={styles.developmentPhase}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <strong>開発工程：</strong> {steps[currentStep].development || "計画フェーズ"}
        <motion.div className={styles.viewToggle}>
          <button 
            className={`${styles.viewToggleButton} ${viewMode === 'ascii' ? styles.active : ''}`}
            onClick={() => setViewMode('ascii')}
          >
            アスキーアート
          </button>
          <button 
            className={`${styles.viewToggleButton} ${viewMode === 'graphic' ? styles.active : ''}`}
            onClick={() => setViewMode('graphic')}
          >
            グラフィカル
          </button>
          <button 
            className={`${styles.viewToggleButton} ${animationEnabled ? styles.active : ''}`}
            onClick={() => setAnimationEnabled(!animationEnabled)}
          >
            {animationEnabled ? 'アニメーション ON' : 'アニメーション OFF'}
          </button>
        </motion.div>
      </motion.div>
      
      <motion.div 
        className={styles.content}
        key={currentStep}
        initial={animationEnabled ? { opacity: 0 } : false}
        animate={animationEnabled ? { opacity: 1 } : false}
        transition={animationEnabled ? { duration: 0.5 } : { duration: 0 }}
      >
        {steps[currentStep].content}
      </motion.div>
      
      <motion.div 
        className={styles.navigation}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <motion.button 
          className={styles.navButton} 
          onClick={prevStep} 
          disabled={currentStep === 0}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          前へ
        </motion.button>
        <motion.button 
          className={styles.navButton} 
          onClick={nextStep} 
          disabled={currentStep === steps.length - 1}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          次へ
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default GitFlowGuide;