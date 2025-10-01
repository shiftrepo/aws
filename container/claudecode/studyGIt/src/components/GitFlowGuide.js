import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactFlowGitGraph from './ReactFlowGitGraph';
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
              <ReactFlowGitGraph step={1} animationEnabled={animationEnabled} />
            </div>
          )}
        </div>
      )
    },
    {
      title: "並行開発開始 - 複数のfeatureブランチ作成",
      development: "詳細設計・複数機能の並行開発",
      content: (
        <div className={styles.section}>
          <h3>並行開発の開始 - 複数のfeatureブランチを作成</h3>
          <p>Git Flowの最大の強みは<strong>並行開発</strong>の実現です。developブランチから複数のfeatureブランチを同時に作成することで、異なるチームやメンバーが干渉することなく独立して機能開発を進めることができます。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# メインブランチの状態を確認
$ git checkout develop
$ git pull origin develop  # リモートの最新状態を取得

# 最初のfeatureブランチを作成
$ git checkout -b feature/login-system develop

# 2つ目のfeatureブランチも同じdevelopブランチから作成
$ git checkout develop
$ git checkout -b feature/user-profile develop

# 3つ目のfeatureブランチも同様に作成
$ git checkout develop
$ git checkout -b feature/search-function develop`}
              </code>
            </pre>
          </div>
          <div className={styles.keyPoints}>
            <h4>並行開発のポイント：</h4>
            <ul>
              <li><strong>独立性</strong>: 各機能は同じdevelopブランチから分岐し、互いに干渉せず開発可能</li>
              <li><strong>チーム分業</strong>: 機能ごとに異なるチームが同時並行で作業できる</li>
              <li><strong>リスク分散</strong>: 一方の機能開発で問題が発生しても、他の機能開発には影響しない</li>
              <li><strong>柔軟なリリース</strong>: 完成した機能から順次developにマージでき、リリースサイクルを調整可能</li>
              <li><strong>効率的なリソース活用</strong>: 開発者が特定の機能の完了を待つことなく作業できる</li>
            </ul>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────────────────────────────────────
                              ↓       ↓         ↓
  feature/                   o─       o─        o─
                        login-system  user-profile  search-function
                              (チームA)    (チームB)     (チームC)
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={2} animationEnabled={animationEnabled} />
            </div>
          )}
        </div>
      )
    },
    {
      title: "ログイン機能の開発 (チームA)",
      development: "製造・テスト (ログイン機能)",
      content: (
        <div className={styles.section}>
          <h3>ログイン機能の開発 - feature/login-system (チームA)</h3>
          <p>並行開発の最初の例として、チームAはfeature/login-systemブランチでログイン機能の開発を進めています。他のチームの作業とは<strong>完全に独立</strong>しており、自分たちのペースで機能を実装できます。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`$ git checkout feature/login-system

# ファイルの作成と変更
$ touch login.js
$ vim app.js  # アプリケーションファイルを編集

# 変更を確認
$ git status
$ git diff

# 変更をコミット
$ git add app.js login.js
$ git commit -m "ログイン機能の基本実装"

# さらに実装を進める
$ vim login.js  # 認証機能を追加
$ git commit -am "ログイン認証ロジックの実装"`}
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

function validateCredentials(username, password) {
  // 実際のアプリケーションではデータベース検証など
  const isValid = username.length >= 3 && password.length >= 8;
  return isValid;
}

module.exports = {
  loginUser,
  logoutUser,
  validateCredentials
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────────────────────────────────────
                              ↓       ↓         ↓
  feature/                   o──o──o  o─        o─
                        login-system  user-profile  search-function
                       (チームA:開発中) (チームB:未着手)  (チームC:未着手)  

  # チームAは複数のコミットを作成、他チームはまだ変更なし
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={3} animationEnabled={animationEnabled} />
            </div>
          )}
        </div>
      )
    },
    {
      title: "ユーザープロファイル機能の開発 (チームB)",
      development: "製造・テスト (ユーザープロファイル機能)",
      content: (
        <div className={styles.section}>
          <h3>並行開発 - ユーザープロファイル機能 (チームB)</h3>
          <p><strong>ここが重要な並行開発のポイント</strong>: チームBはチームAの作業完了を待たずに、独自のfeature/user-profileブランチで機能開発を<strong>同時進行</strong>しています。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# チームBは自分たちのブランチで作業開始
$ git checkout feature/user-profile

# プロファイル機能のファイル作成
$ touch user-profile.js
$ vim app.js  # チームAとは異なる変更を同じファイルに実装

# 変更をコミット
$ git add app.js user-profile.js
$ git commit -m "ユーザープロファイル機能の基本実装"

# さらにプロファイル編集機能を追加
$ vim user-profile.js
$ git commit -am "プロファイル編集機能の追加"

# プロファイル画像アップロード機能を実装
$ mkdir uploads
$ touch uploads/.gitkeep
$ vim user-profile.js  # 画像アップロード機能を追加
$ git add uploads/
$ git commit -am "プロファイル画像アップロード機能の実装"`}
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
  `}<span className={styles.newCode}>{`initializeUserProfile(); // 新機能：ユーザープロファイル初期化`}</span>{`
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

function uploadProfileImage(userId, imageFile) {
  console.log("プロファイル画像アップロード:", userId);
  // 実際のアプリケーションではファイル保存処理
  return "/uploads/" + userId + "_" + Date.now() + ".jpg";
}

function removeProfileImage(userId) {
  console.log("プロファイル画像削除:", userId);
  return true;
}

module.exports = {
  getUserProfile,
  updateUserProfile,
  uploadProfileImage,
  removeProfileImage
};`}
                </code>
              </pre>
            </div>
          </div>
          <div className={styles.keyPoints}>
            <h4>並行開発の実践ポイント：</h4>
            <ul>
              <li><strong>注目！</strong>: チームAとチームBは<strong>同じapp.jsファイル</strong>に対して異なる変更を加えています</li>
              <li>互いの作業内容を気にせず、各自の機能に集中できる</li>
              <li>コードの競合はマージ時に一度だけ解決すればよい</li>
              <li>チームBはチームAの進捗状況を気にせず、自分たちのペースで作業できる</li>
            </ul>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────────────────────────────────────
                              ↓            ↓                ↓
  feature/                   o──o──o       o──o──o──o       o─
                        login-system     user-profile    search-function
                       (チームA:開発中)  (チームB:開発中)  (チームC:未着手)
                       
  # チームAとチームBは同時に開発を進めている
  # 同じapp.jsファイルに異なる変更を加えている
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={3.5} animationEnabled={animationEnabled} />
            </div>
          )}
        </div>
      )
    },
    {
      title: "ログイン機能の開発進行 (チームA)",
      development: "製造・テスト (ログイン機能)",
      content: (
        <div className={styles.section}>
          <h3>ログイン機能の開発進行 - 全てのフィーチャーブランチで並行して開発中</h3>
          <p><strong>並行開発のポイント</strong>: 全てのチームが同時に各々のfeatureブランチで開発を進めています。これが並行開発の本質であり、複数の機能を同時に効率よく開発できる強みです。<strong>重要</strong>: この時点ではマージは行わず、各ブランチでの開発に集中します。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ログイン機能の開発を進行中
$ git checkout feature/login-system

# コードの実装とテスト
$ vim login.js
$ npm test -- --watch --testPathPattern=login

# 機能のテストを実行
$ npm run test:e2e -- --spec login

# 変更をコミット
$ git add login.js
$ git commit -m "ログイン認証フローの実装"

# 他のブランチの状況を確認
$ git fetch origin
$ git branch -a --list

# 他のチームも並行して開発を進めている
# 各ブランチは独立して開発を継続`}
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

function validateCredentials(username, password) {
  // 実際のアプリケーションではデータベース検証など
  const isValid = username.length >= 3 && password.length >= 8;
  return isValid;
}

module.exports = {
  loginUser,
  logoutUser,
  validateCredentials
};`}
                </code>
              </pre>
            </div>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────────────o──────────────────────
                              ↓                     ↑            ↓         ↓
  feature/                   o──o──o───────────────o        o──o──o──o     o─
                          login-system              user-profile      search-function
                         (マージ完了)              (開発継続中)     (開発未着手)
                         
  # チームAは開発完了・マージ済み、チームBはまだ開発中だがマージを待つ必要はない
  # developブランチにはログイン機能のみが統合された状態
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={4} animationEnabled={animationEnabled} />
            </div>
          )}
          <div className={styles.keyPoints}>
            <h4>マージのポイント：</h4>
            <ul>
              <li><strong>独立した完了</strong>: 完成した機能から順次developにマージできる</li>
              <li><strong>継続的統合</strong>: 他の機能ブランチの開発状況に関わらずリリースサイクルを進められる</li>
              <li><strong>分業と効率化</strong>: マージ後もチームBは自分たちのブランチで開発を継続できる</li>
              <li><strong>トレーサビリティ</strong>: --no-ffオプションでマージコミットを作成し、機能の統合履歴を明確に残す</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "ユーザープロファイル機能の完了とマージ (チームB)",
      development: "単体試験・結合試験 (ユーザープロファイル機能)",
      content: (
        <div className={styles.section}>
          <h3>ユーザープロファイル機能の完了とマージ - 最新developとの統合</h3>
          <p><strong>並行開発の統合ポイント</strong>: チームBのユーザープロファイル機能の開発とテストが完了しました。ここで<strong>重要なステップ</strong>は、マージ前にまず最新のdevelopブランチ（チームAの変更を含む）を自分たちのブランチに統合し、衝突を解決することです。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ユーザープロファイル機能の開発完了
$ git checkout feature/user-profile

# 統合前にテスト実行
$ npm test -- --testPathPattern=user-profile

# developブランチの最新変更（ログイン機能を含む）を取り込む
$ git merge develop

# !!! 競合が発生 !!!
# app.jsファイルで競合が発生（両チームが同じファイルを変更）
AUTO-MERGING app.js
CONFLICT (content): Merge conflict in app.js
Automatic merge failed; fix conflicts and then commit the result.

# 競合を解決
$ vim app.js  # エディタで競合を解決

# 競合解決後、変更をコミット
$ git add app.js
$ git commit -m "ログイン機能との統合および競合解決"

# developへマージ
$ git checkout develop
$ git merge --no-ff feature/user-profile -m "機能追加: ユーザープロファイル機能の実装"
$ git branch -d feature/user-profile
$ git push origin develop`}
              </code>
            </pre>
          </div>
          <div className={styles.fileChanges}>
            <h4>競合解決とマージ後のdevelopブランチのファイル状態：</h4>
            <div className={styles.file}>
              <div className={styles.fileName}>app.js（競合解決後）</div>
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

function uploadProfileImage(userId, imageFile) {
  console.log("プロファイル画像アップロード:", userId);
  // 実際のアプリケーションではファイル保存処理
  return "/uploads/" + userId + "_" + Date.now() + ".jpg";
}

function removeProfileImage(userId) {
  console.log("プロファイル画像削除:", userId);
  return true;
}

module.exports = {
  getUserProfile,
  updateUserProfile,
  uploadProfileImage,
  removeProfileImage
};`}
                </code>
              </pre>
            </div>
          </div>
          <div className={styles.keyPoints}>
            <h4>並行開発の統合ポイント：</h4>
            <ul>
              <li><strong>競合解決の例</strong>：<code>{`<<<<<<< HEAD
  initializeLogin();
=======
  initializeUserProfile();
>>>>>>> feature/user-profile`}</code></li>
              <li><strong>適切な解決方法</strong>：両方の機能呼び出しを残す</li>
              <li><strong>事前統合の重要性</strong>：developへマージする前に、まずdevelopの変更をfeatureブランチに取り込む</li>
              <li><strong>競合の最小化</strong>：競合はfeatureブランチ上で一度だけ解決すればよい</li>
              <li><strong>機能の独立性</strong>：両機能が互いに干渉することなく並行開発された</li>
            </ul>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────o───────────────────o─────────
                              ↓               ↑       ↓            ↑
  feature/                   o──o──o─────────o       o──o──o──o────o
                        login-system              user-profile
                        (マージ済み)              (マージ済み)
                        
  # 両方のfeatureブランチがdevelopにマージされた
  # user-profileブランチがマージ前にdevelopの最新変更を取り込んだ
  # アプリケーションはログイン機能とプロファイル機能を両方サポート
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={5} animationEnabled={animationEnabled} />
            </div>
          )}
          <div className={styles.keyPoints}>
            <h4>並行開発のメリット：</h4>
            <ul>
              <li><strong>開発効率</strong>: 機能ごとに独立して開発が進むため、チーム全体の開発効率が向上</li>
              <li><strong>リスク分散</strong>: あるチームの進捗が遅れても他チームの作業がブロックされない</li>
              <li><strong>品質保証</strong>: 各機能がマージされる前に適切なテストを個別に実施できる</li>
              <li><strong>優先度管理</strong>: 異なる優先度の機能を効率的に管理・リリースできる</li>
              <li><strong>統合の柔軟性</strong>: 完成した機能から順次統合でき、リリースサイクルを最適化できる</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "リリース準備とサードチームの並行開発 (機能統合)",
      development: "総合試験開始とサードチーム開発",
      content: (
        <div className={styles.section}>
          <h3>リリース準備とサードチームの並行開発</h3>
          <p><strong>並行開発の次のステージ</strong>: 2つの主要機能開発が完了し、developブランチからreleaseブランチを作成してリリース準備を始めます。<strong>注目すべき点</strong>: この間にもチームCは次のリリースに向けた検索機能の開発を並行して進めることができます。</p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# リリース準備ブランチの作成
$ git checkout develop
$ git checkout -b release/1.0.0 develop

# バージョン番号の更新
$ vim package.json  # バージョン番号を0.9.0から1.0.0に更新
$ vim app.js       # バージョンコメントを追加

# 変更をコミット
$ git commit -am "バージョン1.0.0準備"

# 同時に、チームCは検索機能の開発を継続
# (別のターミナルやマシンで並行作業)
$ git checkout feature/search-function
$ vim search.js    # 検索機能の開発継続
$ git commit -am "高度な検索アルゴリズムの実装"`}
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
          <div className={styles.keyPoints}>
            <h4>並行開発のマルチステージ：</h4>
            <ul>
              <li><strong>リリース準備</strong>: 完成した機能はリリース準備段階に</li>
              <li><strong>継続開発</strong>: 同時に次のリリースに向けた開発が並行して進行</li>
              <li><strong>マルチフロー</strong>: 「リリース」と「開発」の2つの並行フローが存在</li>
              <li><strong>リソース最適化</strong>: 全開発者がリリース作業を待つ必要なく効率的に作業可能</li>
            </ul>
          </div>
          {viewMode === 'ascii' ? (
            <div className={styles.asciiArt}>
              <pre>
                {`
  main/master (本番B面)     o─────────────────────────────────────────────────
                
  develop (開発A面)         o─────────────────o───────────────────o─────────
                                                                    ↓
  release/                                                         o──o
  1.0.0                                                   (リリース準備中)
  
  feature/                                                             o──o──o
  search-function                                               (チームC:開発継続中)
  
  # リリース準備と並行して、次のリリースに向けた開発も継続できる
  # この方式により、開発サイクルが途切れることなく続く
                `}
              </pre>
            </div>
          ) : (
            <div className={styles.graphicView}>
              <ReactFlowGitGraph step={6} animationEnabled={animationEnabled} />
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
              <ReactFlowGitGraph step={6} animationEnabled={animationEnabled} />
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
              <ReactFlowGitGraph step={7} animationEnabled={animationEnabled} />
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
              <ReactFlowGitGraph step={8} animationEnabled={animationEnabled} />
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
              <ReactFlowGitGraph step={9} animationEnabled={animationEnabled} />
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
              <ReactFlowGitGraph step={10} animationEnabled={animationEnabled} />
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