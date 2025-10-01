"use client";

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import styles from './DockerGuide.module.css';
import DEFAULT_DOCKER_STATE from './DefaultDocker';
import { useDockerLearning } from './DockerLearningContext';
import { DifficultyLevel } from './DockerSimulator';

const DockerGuide = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [viewMode, setViewMode] = useState('graphic'); // 'graphic' または 'text'
  const [animationEnabled, setAnimationEnabled] = useState(true);
  
  // DockerLearningContextから学習進捗を取得
  const { 
    progress, 
    completeTopic, 
    topics, 
    currentTopicId,
    setCurrentTopic,
    getNextRecommendedTopic,
    setLanguage 
  } = useDockerLearning();
  
  // 言語切り替え処理
  const handleLanguageChange = (lang: 'ja' | 'en') => {
    setLanguage(lang);
    // ここで言語に応じたコンテンツ切り替えロジックを実装
    // 実装例: 各ステップの内容を言語に応じて切り替える
    console.log(`Language changed to: ${lang}`);
  };
  
  const steps = [
    {
      title: "Dockerとは",
      development: "基礎概念",
      content: (
        <div className={styles.section}>
          <h3>Dockerとは何か？</h3>
          <p>
            Dockerは、アプリケーションを開発・配布・実行するためのオープンプラットフォームです。
            環境を<strong>コンテナ</strong>として分離・パッケージ化することで、どこでも同じように動作することを保証します。
            「ローカルでは動くけど本番環境では動かない」という問題を解決する技術です。
          </p>
          
          <motion.div 
            className={styles.iconRow}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, staggerChildren: 0.1 }}
          >
            <motion.div className={styles.iconBox} whileHover={{ scale: 1.1 }}>
              <div className={styles.icon}>🐳</div>
              <div className={styles.label}>Docker</div>
            </motion.div>
            <motion.div className={styles.iconBox} whileHover={{ scale: 1.1 }}>
              <div className={styles.icon}>📦</div>
              <div className={styles.label}>コンテナ</div>
            </motion.div>
            <motion.div className={styles.iconBox} whileHover={{ scale: 1.1 }}>
              <div className={styles.icon}>🖼️</div>
              <div className={styles.label}>イメージ</div>
            </motion.div>
            <motion.div className={styles.iconBox} whileHover={{ scale: 1.1 }}>
              <div className={styles.icon}>📄</div>
              <div className={styles.label}>Dockerfile</div>
            </motion.div>
            <motion.div className={styles.iconBox} whileHover={{ scale: 1.1 }}>
              <div className={styles.icon}>🔄</div>
              <div className={styles.label}>Docker Compose</div>
            </motion.div>
          </motion.div>
          
          <div className={styles.interactiveSection}>
            <h4>コンテナとは何か？</h4>
            <p>
              コンテナはアプリケーションとその依存関係（ライブラリやランタイム環境など）を一つのパッケージにまとめたものです。
              コンテナ内のアプリケーションは、ホスト環境から隔離された独自の仮想環境で実行されます。
            </p>
            
            <div className={styles.conceptExplanation}>
              <div className={styles.conceptTitle}>
                <span className={styles.conceptIcon}>🔍</span>
                <h5>重要ポイント：コンテナとは？</h5>
              </div>
              <ul>
                <li><strong>独立した実行環境</strong>：自己完結型の実行単位</li>
                <li><strong>アプリケーション＋依存関係</strong>：必要なものだけを含む</li>
                <li><strong>ポータブル</strong>：どこでも同じように動作する</li>
                <li><strong>軽量</strong>：仮想マシンよりも少ないリソースで稼働</li>
                <li><strong>短命</strong>：使い捨てが前提（ステートレス設計）</li>
              </ul>
            </div>
          </div>
          
          <h4>コンテナと仮想マシンの違い</h4>
          
          <div className={styles.comparisonDiagram}>
            <div className={styles.comparisonColumn}>
              <h5 className={styles.comparisonTitle}>コンテナ</h5>
              <div className={styles.comparisonImage}>
                <motion.div 
                  className={styles.containerArchitecture}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className={styles.containerApps}>
                    <div className={styles.containerApp}>App A</div>
                    <div className={styles.containerApp}>App B</div>
                    <div className={styles.containerApp}>App C</div>
                  </div>
                  <div className={styles.containerRuntime}>Docker Engine</div>
                  <div className={styles.hostOS}>ホストOS</div>
                  <div className={styles.hostHardware}>物理ハードウェア</div>
                </motion.div>
              </div>
              <div className={styles.comparisonPoints}>
                <ul>
                  <li>OSカーネルを共有</li>
                  <li>必要なライブラリのみをパッケージ化</li>
                  <li>起動時間：数秒</li>
                  <li>サイズ：数MB～数百MB</li>
                </ul>
              </div>
            </div>
            
            <div className={styles.comparisonColumn}>
              <h5 className={styles.comparisonTitle}>仮想マシン</h5>
              <div className={styles.comparisonImage}>
                <motion.div 
                  className={styles.vmArchitecture}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <div className={styles.vmGroup}>
                    <div className={styles.vm}>
                      <div className={styles.vmApp}>App A</div>
                      <div className={styles.vmOS}>ゲストOS</div>
                    </div>
                    <div className={styles.vm}>
                      <div className={styles.vmApp}>App B</div>
                      <div className={styles.vmOS}>ゲストOS</div>
                    </div>
                    <div className={styles.vm}>
                      <div className={styles.vmApp}>App C</div>
                      <div className={styles.vmOS}>ゲストOS</div>
                    </div>
                  </div>
                  <div className={styles.hypervisor}>ハイパーバイザー</div>
                  <div className={styles.hostOS}>ホストOS</div>
                  <div className={styles.hostHardware}>物理ハードウェア</div>
                </motion.div>
              </div>
              <div className={styles.comparisonPoints}>
                <ul>
                  <li>独自のOSを実行</li>
                  <li>完全な仮想化環境</li>
                  <li>起動時間：数分</li>
                  <li>サイズ：数GB～数十GB</li>
                </ul>
              </div>
            </div>
          </div>
          
          <table className={styles.compareTable}>
            <thead>
              <tr>
                <th></th>
                <th>コンテナ</th>
                <th>仮想マシン（VM）</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>起動時間</strong></td>
                <td>数秒</td>
                <td>数分</td>
              </tr>
              <tr>
                <td><strong>サイズ</strong></td>
                <td>数MB～数百MB</td>
                <td>数GB～数十GB</td>
              </tr>
              <tr>
                <td><strong>リソース効率</strong></td>
                <td>非常に高い</td>
                <td>中程度</td>
              </tr>
              <tr>
                <td><strong>分離レベル</strong></td>
                <td>プロセスレベル</td>
                <td>ハードウェアレベル</td>
              </tr>
              <tr>
                <td><strong>OS</strong></td>
                <td>ホストOSのカーネルを共有</td>
                <td>ゲストOSが必要</td>
              </tr>
              <tr>
                <td><strong>セキュリティ</strong></td>
                <td>やや低い（共有カーネル）</td>
                <td>高い（完全分離）</td>
              </tr>
              <tr>
                <td><strong>用途</strong></td>
                <td>マイクロサービス、CI/CD</td>
                <td>異なるOS、レガシーアプリ</td>
              </tr>
            </tbody>
          </table>
          
          <div className={styles.hostRelationship}>
            <h4>コンテナとホストの関係</h4>
            <p>
              コンテナはホストOSのカーネルを共有しながら、隔離された実行環境を提供します。
              この仕組みにより、軽量かつ高速な動作を実現しています。
            </p>
            
            <div className={styles.hostRelationshipDiagram}>
              <motion.div 
                className={styles.hostRelationshipContainer}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8 }}
              >
                <div className={styles.hostSystem}>
                  <div className={styles.hostTitle}>ホストシステム</div>
                  <div className={styles.hostKernel}>
                    <span>Linuxカーネル</span>
                    <div className={styles.kernelFeatures}>
                      <div className={styles.kernelFeature}>namespaces</div>
                      <div className={styles.kernelFeature}>cgroups</div>
                      <div className={styles.kernelFeature}>capabilities</div>
                    </div>
                  </div>
                  
                  <div className={styles.containersGroup}>
                    <motion.div 
                      className={styles.containerBox}
                      whileHover={{ y: -5 }}
                    >
                      <div className={styles.containerHeader}>コンテナA</div>
                      <div className={styles.containerContent}>
                        <div>App A</div>
                        <div>Libs</div>
                      </div>
                    </motion.div>
                    <motion.div 
                      className={styles.containerBox}
                      whileHover={{ y: -5 }}
                    >
                      <div className={styles.containerHeader}>コンテナB</div>
                      <div className={styles.containerContent}>
                        <div>App B</div>
                        <div>Libs</div>
                      </div>
                    </motion.div>
                    <motion.div 
                      className={styles.containerBox}
                      whileHover={{ y: -5 }}
                    >
                      <div className={styles.containerHeader}>コンテナC</div>
                      <div className={styles.containerContent}>
                        <div>App C</div>
                        <div>Libs</div>
                      </div>
                    </motion.div>
                  </div>
                </div>
              </motion.div>
            </div>
            
            <div className={styles.conceptExplanation}>
              <div className={styles.conceptTitle}>
                <span className={styles.conceptIcon}>🔐</span>
                <h5>コンテナの隔離技術</h5>
              </div>
              <ul>
                <li><strong>namespaces</strong>：プロセス、ネットワーク、ファイルシステムなどの分離</li>
                <li><strong>cgroups</strong>：CPUやメモリなどのリソース制限</li>
                <li><strong>capabilities</strong>：特権操作の制限</li>
                <li><strong>seccomp</strong>：システムコールのフィルタリング</li>
              </ul>
            </div>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>Dockerの主要概念</h4>
            <ul>
              <li><strong>イメージ</strong>: アプリケーションと実行環境をパッケージ化したテンプレート（読み取り専用）</li>
              <li><strong>コンテナ</strong>: イメージの実行インスタンス（読み書き可能なレイヤーを追加）</li>
              <li><strong>Dockerfile</strong>: イメージをビルドするための指示書（コード化されたレシピ）</li>
              <li><strong>Docker Compose</strong>: 複数のコンテナを定義・実行するためのツール（アプリ構成管理）</li>
              <li><strong>レジストリ</strong>: イメージを保存・共有するためのリポジトリ（配布拠点）</li>
              <li><strong>ボリューム</strong>: コンテナのデータを永続化する仕組み（データの永続性）</li>
              <li><strong>ネットワーク</strong>: コンテナ間の通信を管理する仕組み（分離通信路）</li>
            </ul>
          </div>
          
          <div className={styles.dockerExample}>
            <img 
              src="https://docs.docker.com/engine/images/architecture.svg" 
              alt="Docker Architecture" 
              className={styles.dockerExampleImg}
            />
            <div className={styles.diagramCaption}>
              Docker アーキテクチャ概要（出典: Docker公式ドキュメント）
            </div>
          </div>
          
          <div className={styles.interactiveLearning}>
            <h4>理解度チェック</h4>
            <div className={styles.questionBox}>
              <p>質問: コンテナと仮想マシンの最も重要な違いは何ですか？</p>
              <details>
                <summary>答えを見る</summary>
                <div className={styles.answerBox}>
                  <p>コンテナはホストOSのカーネルを共有するため、軽量で高速に起動できますが、仮想マシンは独自のゲストOSを持ち、完全に分離された環境を提供します。コンテナはアプリケーションとその依存関係のみを含み、仮想マシンは完全なOSとアプリケーションを含みます。</p>
                </div>
              </details>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Docker基本コマンド",
      development: "基本操作",
      content: (
        <div className={styles.section}>
          <h3>Docker基本コマンド</h3>
          <p>
            Dockerを使いこなすためには、基本的なコマンドを理解することが重要です。
            以下は最も頻繁に使用されるDockerコマンドです。
          </p>
          
          <h4>コンテナ操作</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# コンテナの起動
$ docker run -d --name my-container -p 8080:80 nginx

# コンテナ一覧表示
$ docker ps        # 実行中のコンテナのみ
$ docker ps -a     # 全てのコンテナ

# コンテナの停止
$ docker stop my-container

# コンテナの再開
$ docker start my-container

# コンテナの削除
$ docker rm my-container
$ docker rm -f my-container   # 実行中でも強制削除`}
              </code>
            </pre>
          </div>
          
          <h4>イメージ操作</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# イメージのダウンロード
$ docker pull nginx:latest

# イメージ一覧表示
$ docker images

# イメージのビルド
$ docker build -t my-app:1.0 .

# イメージの削除
$ docker rmi nginx:latest`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>コマンドオプションの意味</h4>
            <ul>
              <li><code>-d</code>: デタッチドモード（バックグラウンドで実行）</li>
              <li><code>--name</code>: コンテナに名前をつける</li>
              <li><code>-p</code>: ポートマッピング（ホスト:コンテナ）</li>
              <li><code>-v</code>: ボリュームマウント（ホスト:コンテナ）</li>
              <li><code>-e</code>: 環境変数を設定</li>
              <li><code>-t</code>: イメージにタグをつける</li>
              <li><code>-f</code>: 強制実行（例: 実行中のコンテナを強制削除）</li>
            </ul>
          </div>
          
          <h4>コンテナとの対話</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# 実行中のコンテナでコマンドを実行
$ docker exec my-container ls -la

# コンテナ内でシェルを起動
$ docker exec -it my-container bash

# コンテナのログを表示
$ docker logs my-container

# コンテナのログをリアルタイム表示（follow）
$ docker logs -f my-container`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>コンテナライフサイクル</h4>
            <ul>
              <li><strong>created</strong>: 作成された状態</li>
              <li><strong>running</strong>: 実行中の状態</li>
              <li><strong>paused</strong>: 一時停止状態</li>
              <li><strong>exited</strong>: 停止状態</li>
              <li><strong>dead</strong>: 削除できない問題のある状態</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "Dockerfile",
      development: "イメージ構築",
      content: (
        <div className={styles.section}>
          <h3>Dockerfile - Dockerイメージ定義ファイル</h3>
          <p>
            Dockerfileは、Dockerイメージをビルドするための指示書です。
            一連のコマンドを記述することで、再現性の高いイメージを作成できます。
          </p>
          
          <h4>基本的なDockerfile</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ベースイメージを指定
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# パッケージ管理ファイルをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# ソースコードをコピー
COPY . .

# ポート公開
EXPOSE 3000

# アプリケーション起動コマンド
CMD ["npm", "start"]`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>主要なDockerfile命令</h4>
            <ul>
              <li><code>FROM</code>: ベースイメージを指定</li>
              <li><code>WORKDIR</code>: 作業ディレクトリを設定</li>
              <li><code>COPY</code>: ホストからコンテナにファイルをコピー</li>
              <li><code>ADD</code>: ファイルをコピーし、tarの展開なども可能</li>
              <li><code>RUN</code>: コマンドを実行し、結果を新レイヤーとして保存</li>
              <li><code>ENV</code>: 環境変数を設定</li>
              <li><code>EXPOSE</code>: コンテナがリッスンするポートを指定</li>
              <li><code>CMD</code>: コンテナ起動時のデフォルトコマンド</li>
              <li><code>ENTRYPOINT</code>: コンテナ起動時に必ず実行されるコマンド</li>
            </ul>
          </div>
          
          <h4>マルチステージビルド</h4>
          <p>
            マルチステージビルドを使用すると、ビルドに必要なツールと実行に必要な環境を分離でき、
            最終的なイメージサイズを小さくできます。
          </p>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ビルドステージ
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 実行ステージ
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>Dockerfileのベストプラクティス</h4>
            <ul>
              <li><strong>レイヤーの最小化</strong>: RUN, COPY, ADDは新しいレイヤーを作成します</li>
              <li><strong>キャッシュの活用</strong>: 頻繁に変更されないものを先に配置</li>
              <li><strong>適切なベースイメージ</strong>: 最小限のイメージ（alpine等）を使用</li>
              <li><strong>.dockerignore</strong>: 不要なファイルをビルドに含めない</li>
              <li><strong>非rootユーザー</strong>: セキュリティ向上のために特権のないユーザーを使用</li>
              <li><strong>マルチステージビルド</strong>: ビルドツールと実行環境の分離</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "Docker Compose",
      development: "複数コンテナ構成",
      content: (
        <div className={styles.section}>
          <h3>Docker Compose - 複数コンテナの管理</h3>
          <p>
            Docker Composeは、複数のコンテナからなるアプリケーションを定義・実行するためのツールです。
            YAMLファイルを使用して、サービス、ネットワーク、ボリュームを設定します。
          </p>
          
          <h4>基本的なdocker-compose.yml</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      
  db:
    image: postgres:13
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_USER=user
      - POSTGRES_DB=myapp
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
      
volumes:
  postgres-data:`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>Docker Compose 基本コマンド</h4>
            <ul>
              <li><code>docker-compose up</code>: サービスを起動</li>
              <li><code>docker-compose up -d</code>: バックグラウンドで起動</li>
              <li><code>docker-compose down</code>: サービスを停止・削除</li>
              <li><code>docker-compose logs</code>: サービスのログを表示</li>
              <li><code>docker-compose exec service_name command</code>: サービスでコマンドを実行</li>
              <li><code>docker-compose build</code>: サービスをビルド</li>
              <li><code>docker-compose ps</code>: サービスの状態を確認</li>
            </ul>
          </div>
          
          <div className={styles.file}>
            <div className={styles.fileName}>このプロジェクトのdocker-compose.yml</div>
            <pre>
              <code>
                {`version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: git-playground
    ports:
      - "3000:3000"
    volumes:
      - .:/app:z,U
      - /app/node_modules
    user: "root:root"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_HOST_URL=mcp.shift-terminus.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>Docker Compose 主要要素</h4>
            <ul>
              <li><strong>services</strong>: アプリケーションを構成するコンテナ群</li>
              <li><strong>volumes</strong>: データの永続化と共有のための仕組み</li>
              <li><strong>networks</strong>: コンテナ間通信のためのネットワーク設定</li>
              <li><strong>depends_on</strong>: サービス間の依存関係</li>
              <li><strong>environment</strong>: 環境変数設定</li>
              <li><strong>ports</strong>: ポートマッピング</li>
              <li><strong>build</strong>: Dockerfileからのビルド設定</li>
            </ul>
          </div>
          
          <p>
            Docker Composeを使えば、開発環境を簡単に共有でき、「私の環境では動いている」問題を解消します。
            チーム全員が同じ環境で開発できるのは、大きなメリットです。
          </p>
        </div>
      )
    },
    {
      title: "Docker ネットワーク",
      development: "コンテナ間通信",
      content: (
        <div className={styles.section}>
          <h3>Docker ネットワーク - コンテナ間通信</h3>
          <p>
            Dockerネットワークは、コンテナ間の通信や外部へのアクセスを管理する仕組みです。
            適切なネットワーク設計は、セキュリティと柔軟性の両方において重要です。
          </p>
          
          <h4>ネットワークタイプ</h4>
          <table className={styles.compareTable}>
            <thead>
              <tr>
                <th>ネットワークタイプ</th>
                <th>説明</th>
                <th>ユースケース</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>bridge</strong></td>
                <td>デフォルトのネットワーク。独立した内部ネットワークを作成</td>
                <td>単一ホストでの複数コンテナ間通信</td>
              </tr>
              <tr>
                <td><strong>host</strong></td>
                <td>ホストのネットワークをコンテナが直接使用</td>
                <td>最高のネットワークパフォーマンスが必要な場合</td>
              </tr>
              <tr>
                <td><strong>none</strong></td>
                <td>ネットワーク接続なし</td>
                <td>完全に分離されたコンテナが必要な場合</td>
              </tr>
              <tr>
                <td><strong>overlay</strong></td>
                <td>複数のDockerホスト間でのネットワーク</td>
                <td>Swarmモードでの分散アプリケーション</td>
              </tr>
              <tr>
                <td><strong>macvlan</strong></td>
                <td>コンテナにMACアドレスを割り当て、物理デバイスのように扱う</td>
                <td>レガシーアプリケーションの移行</td>
              </tr>
            </tbody>
          </table>
          
          <h4>ネットワーク操作コマンド</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ネットワーク一覧表示
$ docker network ls

# カスタムネットワーク作成
$ docker network create my-network

# ネットワークの詳細情報表示
$ docker network inspect my-network

# コンテナをネットワークに接続
$ docker network connect my-network my-container

# コンテナをネットワークから切断
$ docker network disconnect my-network my-container

# ネットワーク削除
$ docker network rm my-network`}
              </code>
            </pre>
          </div>
          
          <h4>Docker Composeでのネットワーク設定</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend
      
  api:
    image: node:alpine
    networks:
      - frontend
      - backend
      
  db:
    image: postgres
    networks:
      - backend
      
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 外部アクセス不可`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>Docker ネットワークのポイント</h4>
            <ul>
              <li><strong>コンテナ名での通信</strong>: 同一ネットワーク内のコンテナは名前で相互通信可能</li>
              <li><strong>ポート公開</strong>: 外部からのアクセスには <code>-p</code> オプションでポート公開が必要</li>
              <li><strong>複数ネットワーク</strong>: コンテナは複数のネットワークに所属可能</li>
              <li><strong>セキュリティ</strong>: 内部ネットワークを使って外部からの直接アクセスを制限</li>
              <li><strong>DNS解決</strong>: Docker内部DNSでコンテナ名をIPに解決</li>
            </ul>
          </div>
          
          <div className={styles.dockerExample}>
            <img 
              src="https://docs.docker.com/engine/tutorials/networkingcontainers/images/working.png" 
              alt="Docker Network Example" 
              className={styles.dockerExampleImg}
            />
            <div className={styles.diagramCaption}>
              Dockerコンテナネットワーク構成例（出典: Docker公式ドキュメント）
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Docker ボリューム",
      development: "データ永続化",
      content: (
        <div className={styles.section}>
          <h3>Docker ボリューム - データの永続化</h3>
          <p>
            Dockerコンテナ内のデータは、コンテナが削除されると失われます。
            ボリュームを使用することで、データを永続化し、コンテナ間で共有することができます。
          </p>
          
          <h4>ボリュームの種類</h4>
          <table className={styles.compareTable}>
            <thead>
              <tr>
                <th>種類</th>
                <th>説明</th>
                <th>ユースケース</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Dockerボリューム</strong></td>
                <td>Dockerが管理するボリューム</td>
                <td>データベース、設定ファイルなど</td>
              </tr>
              <tr>
                <td><strong>バインドマウント</strong></td>
                <td>ホスト上の特定パスをマウント</td>
                <td>開発環境、設定ファイル</td>
              </tr>
              <tr>
                <td><strong>tmpfs マウント</strong></td>
                <td>メモリ上の一時ファイルシステム</td>
                <td>一時データ、キャッシュ</td>
              </tr>
            </tbody>
          </table>
          
          <h4>ボリューム操作コマンド</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# ボリューム一覧表示
$ docker volume ls

# ボリューム作成
$ docker volume create my-volume

# ボリュームの詳細情報表示
$ docker volume inspect my-volume

# ボリュームの削除
$ docker volume rm my-volume

# 未使用ボリュームの一括削除
$ docker volume prune`}
              </code>
            </pre>
          </div>
          
          <h4>コンテナ起動時のボリューム指定</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# Dockerボリュームの使用
$ docker run -v my-volume:/data nginx

# バインドマウントの使用
$ docker run -v $(pwd)/host-dir:/container-dir nginx

# 読み取り専用マウント
$ docker run -v my-volume:/data:ro nginx`}
              </code>
            </pre>
          </div>
          
          <h4>Docker Composeでのボリューム設定</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`version: '3.8'

services:
  db:
    image: postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
      
  app:
    build: .
    volumes:
      - .:/app  # バインドマウント
      - /app/node_modules  # 匿名ボリューム
      
volumes:
  postgres-data:  # 名前付きボリューム`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>ボリューム利用のベストプラクティス</h4>
            <ul>
              <li><strong>開発環境</strong>: バインドマウントでソースコードを直接マウントし、ホットリロード可能に</li>
              <li><strong>本番環境</strong>: Dockerボリュームを使用してデータを永続化</li>
              <li><strong>ボリューム命名</strong>: 目的を明確にした命名規則を適用</li>
              <li><strong>読み取り専用</strong>: 必要に応じて読み取り専用マウントを使用</li>
              <li><strong>一時ディレクトリ</strong>: コンテナ内の一時ファイルにはtmpfsを検討</li>
              <li><strong>バックアップ</strong>: 重要なデータボリュームは定期的にバックアップ</li>
            </ul>
          </div>
          
          <div className={styles.file}>
            <div className={styles.fileName}>このプロジェクトのdocker-compose.yml（ボリューム部分）</div>
            <pre>
              <code>
                {`volumes:
  - .:/app:z,U    # ホストのカレントディレクトリをコンテナの/appにマウント
  - /app/node_modules  # コンテナ内のnode_modulesを保護`}
              </code>
            </pre>
          </div>
          
          <p>
            <strong>特筆事項</strong>: <code>:z,U</code> フラグはSELinux環境でのファイル共有を有効にするものです。
            また <code>/app/node_modules</code> のようなマウントは「匿名ボリューム」と呼ばれ、
            バインドマウントで上書きされるのを防ぎます。
          </p>
        </div>
      )
    },
    {
      title: "開発環境でのDocker",
      development: "開発ワークフロー",
      content: (
        <div className={styles.section}>
          <h3>開発環境でのDocker活用</h3>
          <p>
            開発環境にDockerを導入することで、「環境差異」による問題を解消し、
            開発からテスト、本番環境までの一貫したワークフローを実現します。
          </p>
          
          <h4>開発環境のメリット</h4>
          <ul>
            <li><strong>環境の統一</strong>: 「自分のマシンでは動く」問題の解消</li>
            <li><strong>迅速なセットアップ</strong>: 新メンバーが数分で開発環境を構築可能</li>
            <li><strong>依存関係の分離</strong>: 異なるプロジェクト間の依存関係の競合を回避</li>
            <li><strong>サービス分離</strong>: データベースなどの各サービスを独立して管理</li>
            <li><strong>クリーンな環境</strong>: 使い終わったら削除可能</li>
          </ul>
          
          <h4>開発用Dockerfile例</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# 開発環境用Dockerfile
FROM node:18-alpine

# 開発ツールのインストール
RUN apk add --no-cache git curl

WORKDIR /app

# パッケージ管理ファイルのみをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# ソースコードはバインドマウントするので、コピー不要

# ポート公開
EXPOSE 3000

# 開発サーバー起動（ホットリロード付き）
CMD ["npm", "run", "dev"]`}
              </code>
            </pre>
          </div>
          
          <h4>開発用Docker Compose例</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app  # ソースコードをマウント
      - /app/node_modules  # node_modulesを保護
    environment:
      - NODE_ENV=development
    command: npm run dev  # ホットリロード付き開発サーバー
      
  db:
    image: postgres:13
    ports:
      - "5432:5432"
    volumes:
      - postgres-dev-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=devpassword
      - POSTGRES_USER=devuser
      - POSTGRES_DB=devdb
      
volumes:
  postgres-dev-data:`}
              </code>
            </pre>
          </div>
          
          <div className={styles.keyPoints}>
            <h4>開発環境でのDockerのコツ</h4>
            <ul>
              <li><strong>ホットリロード</strong>: バインドマウントとホットリロード対応の開発サーバーを活用</li>
              <li><strong>デバッグ</strong>: <code>docker-compose logs -f</code> でリアルタイムログ監視</li>
              <li><strong>シェル</strong>: <code>docker-compose exec app sh</code> でコンテナ内シェルにアクセス</li>
              <li><strong>キャッシュ</strong>: ビルド時間短縮のためDockerキャッシュを活用</li>
              <li><strong>環境変数</strong>: <code>.env</code>ファイルで環境変数管理</li>
              <li><strong>コンテナ名</strong>: わかりやすい名前でコンテナを管理</li>
              <li><strong>ネットワーク分離</strong>: フロントエンド/バックエンド用の別ネットワークを検討</li>
            </ul>
          </div>
          
          <div className={styles.file}>
            <div className={styles.fileName}>実際の開発ワークフロー例</div>
            <pre>
              <code>
                {`# 1. 開発環境起動
$ docker-compose up -d

# 2. コードの変更（ホストマシン上で編集）
# ホットリロードにより自動反映

# 3. テスト実行
$ docker-compose exec app npm test

# 4. コンテナ内でコマンド実行
$ docker-compose exec app npm install some-package

# 5. ログ確認
$ docker-compose logs -f

# 6. 開発環境の停止
$ docker-compose down  # データボリュームは保持

# 7. 開発環境の完全削除
$ docker-compose down -v  # ボリュームも削除`}
              </code>
            </pre>
          </div>
        </div>
      )
    },
    {
      title: "本番環境でのDocker",
      development: "デプロイメント",
      content: (
        <div className={styles.section}>
          <h3>本番環境でのDocker</h3>
          <p>
            Dockerは開発環境だけでなく、本番環境でも大きなメリットを提供します。
            スケーラビリティ、移植性、一貫性のある展開が可能になります。
          </p>
          
          <h4>本番用Dockerfile例</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# 本番環境用マルチステージビルドDockerfile
# ビルドステージ
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 実行ステージ
FROM node:18-alpine

# セキュリティのため非rootユーザーを作成
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# 本番環境の依存関係のみインストール
COPY package*.json ./
RUN npm ci --only=production

# ビルド成果物をコピー
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/next.config.js ./

# 非rootユーザーに切り替え
USER appuser

EXPOSE 3000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').request('http://localhost:3000', {timeout:2000}).end()" || exit 1

CMD ["npm", "start"]`}
              </code>
            </pre>
          </div>
          
          <h4>本番デプロイの考慮事項</h4>
          <table className={styles.compareTable}>
            <thead>
              <tr>
                <th>項目</th>
                <th>ベストプラクティス</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>セキュリティ</strong></td>
                <td>
                  <ul>
                    <li>非rootユーザーでコンテナを実行</li>
                    <li>不要なパッケージを含めない</li>
                    <li>イメージの脆弱性スキャンを実施</li>
                    <li>シークレットを環境変数やシークレット管理ツールで管理</li>
                  </ul>
                </td>
              </tr>
              <tr>
                <td><strong>パフォーマンス</strong></td>
                <td>
                  <ul>
                    <li>イメージサイズを最小化（マルチステージビルド）</li>
                    <li>適切なキャッシュ戦略</li>
                    <li>リソース制限の設定</li>
                  </ul>
                </td>
              </tr>
              <tr>
                <td><strong>可用性</strong></td>
                <td>
                  <ul>
                    <li>ヘルスチェックの実装</li>
                    <li>適切な再起動ポリシー</li>
                    <li>複数インスタンスでの実行</li>
                  </ul>
                </td>
              </tr>
              <tr>
                <td><strong>監視</strong></td>
                <td>
                  <ul>
                    <li>ログ収集の設定</li>
                    <li>メトリクスの収集</li>
                    <li>アラートの設定</li>
                  </ul>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div className={styles.keyPoints}>
            <h4>コンテナオーケストレーション</h4>
            <p>本番環境では、複数コンテナの管理にオーケストレーションツールが必要です：</p>
            <ul>
              <li><strong>Kubernetes</strong>: 大規模環境向けの完全なコンテナオーケストレーションシステム</li>
              <li><strong>Docker Swarm</strong>: Dockerに統合されたシンプルなオーケストレーションツール</li>
              <li><strong>Amazon ECS/EKS</strong>: AWSのコンテナサービス</li>
              <li><strong>Google GKE</strong>: GoogleのマネージドKubernetesサービス</li>
              <li><strong>Azure AKS</strong>: MicrosoftのマネージドKubernetesサービス</li>
            </ul>
          </div>
          
          <h4>CI/CDパイプラインとの統合</h4>
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# GitHub Actions ワークフロー例
name: Docker CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
        
      - name: Login to Container Registry
        uses: docker/login-action@v1
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull ghcr.io/${{ github.repository }}:latest
            docker-compose -f docker-compose.prod.yml up -d --force-recreate`}
              </code>
            </pre>
          </div>
        </div>
      )
    },
    {
      title: "Dockerベストプラクティス",
      development: "最適化と改善",
      content: (
        <div className={styles.section}>
          <h3>Dockerベストプラクティス総集編</h3>
          <p>
            これまで学んだDockerの知識を活かすための、ベストプラクティスと一般的なパターンをまとめます。
            これらの実践は、効率的で保守しやすいDockerベースのアプリケーション開発に役立ちます。
          </p>
          
          <h4>イメージ最適化</h4>
          <ol>
            <li><strong>適切なベースイメージ</strong>: 可能な限り軽量なベースイメージ（alpine等）を使用</li>
            <li><strong>マルチステージビルド</strong>: ビルドツールと実行環境を分離し、最終イメージを小さく</li>
            <li><strong>レイヤー最小化</strong>: RUN命令を集約してレイヤー数を減らす</li>
            <li><strong>不要ファイル削除</strong>: キャッシュやテンポラリファイルを削除</li>
            <li><strong>.dockerignore</strong>: 不要ファイルをビルドコンテキストから除外</li>
          </ol>
          
          <div className={styles.codeBlock}>
            <pre>
              <code>
                {`# 最適化されたDockerfile例
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build && npm prune --production

FROM node:18-alpine

WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

# 1つのRUN命令で複数操作（レイヤー最小化）
RUN addgroup -S appgroup && \\
    adduser -S appuser -G appgroup && \\
    chown -R appuser:appgroup /app

USER appuser
CMD ["node", "dist/server.js"]`}
              </code>
            </pre>
          </div>
          
          <h4>セキュリティ強化</h4>
          <ul>
            <li><strong>最小権限原則</strong>: 非rootユーザーでコンテナを実行</li>
            <li><strong>イメージスキャン</strong>: Trivy, Clair等でイメージの脆弱性をスキャン</li>
            <li><strong>不変イメージ</strong>: イメージにタグではなくダイジェスト（SHA256）を使用</li>
            <li><strong>シークレット管理</strong>: シークレットをDockerfileや環境変数に直接含めない</li>
            <li><strong>読み取り専用ファイルシステム</strong>: <code>--read-only</code>フラグで実行</li>
            <li><strong>ケイパビリティ制限</strong>: 必要最小限のケイパビリティのみ付与</li>
          </ul>
          
          <h4>効率的な開発環境</h4>
          <ul>
            <li><strong>ホットリロード</strong>: バインドマウントとホットリロード対応の開発サーバー</li>
            <li><strong>コード共有</strong>: 開発コードをボリュームでマウントし、変更を即時反映</li>
            <li><strong>デバッグツール</strong>: 開発環境には適切なデバッグツールを含める</li>
            <li><strong>開発/本番の分離</strong>: 異なるDockerfile（dev/prod）を用意</li>
            <li><strong>依存関係キャッシュ</strong>: node_modules等をボリュームやビルドキャッシュで管理</li>
          </ul>
          
          <div className={styles.keyPoints}>
            <h4>コンテナライフサイクル管理</h4>
            <ul>
              <li><strong>自己修復性</strong>: ヘルスチェックと適切な再起動ポリシーを設定</li>
              <li><strong>グレースフルシャットダウン</strong>: SIGTERMシグナルを適切に処理</li>
              <li><strong>初期化スクリプト</strong>: コンテナ起動時の初期化作業を自動化</li>
              <li><strong>サイドカーパターン</strong>: 関連機能を別コンテナで実装（ログ収集等）</li>
              <li><strong>PID 1問題</strong>: シグナル処理のためにtiniやdumb-initを使用</li>
            </ul>
          </div>
          
          <h4>組織内Docker標準化</h4>
          <ul>
            <li><strong>ベースイメージの標準化</strong>: 組織内で共通のベースイメージを定義</li>
            <li><strong>CI/CDパイプライン統合</strong>: 自動ビルド・テスト・デプロイを整備</li>
            <li><strong>イメージレジストリ管理</strong>: プライベートレジストリの使用と管理</li>
            <li><strong>ドキュメント</strong>: Dockerfileにコメントと使用方法を記載</li>
            <li><strong>タグ戦略</strong>: バージョニングとタグ付けの規則を決定</li>
            <li><strong>イメージライフサイクル</strong>: 古いイメージの定期的なクリーンアップ</li>
          </ul>
          
          <div className={styles.keyPoints}>
            <h4>パフォーマンスチューニング</h4>
            <ul>
              <li><strong>リソース制限</strong>: CPU/メモリ制限の適切な設定</li>
              <li><strong>軽量化</strong>: イメージサイズの最小化</li>
              <li><strong>キャッシュ戦略</strong>: ビルドキャッシュの効果的な活用</li>
              <li><strong>ネットワークチューニング</strong>: 適切なネットワークドライバの選択</li>
              <li><strong>ストレージドライバ</strong>: ワークロードに適したストレージドライバの選択</li>
              <li><strong>水平スケーリング</strong>: 複数インスタンスでの負荷分散</li>
            </ul>
          </div>
          
          <div className={styles.dockerExample}>
            <p>
              Dockerは強力なツールですが、適切に使用するには経験と知識が必要です。
              この講座で学んだ内容を実践し、継続的に学習することで、
              Docker活用のスキルを磨いていきましょう。
            </p>
          </div>
        </div>
      )
    }
  ];

  // 学習進捗と連携した次のステップ移動
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      // 現在のステップを完了としてマーク
      const currentStepData = steps[currentStep];
      const topicId = getTopicIdFromTitle(currentStepData.title);
      if (topicId) {
        completeTopic(topicId);
      }
      
      // 次のステップへ移動
      setCurrentStep(currentStep + 1);
      
      // 対応するトピックを現在のトピックとして設定
      const nextStepData = steps[currentStep + 1];
      const nextTopicId = getTopicIdFromTitle(nextStepData.title);
      if (nextTopicId) {
        setCurrentTopic(nextTopicId);
      }
    }
  };
  
  // トピックタイトルからトピックIDを取得するヘルパー関数
  const getTopicIdFromTitle = (title: string): string | null => {
    switch (title) {
      case 'Dockerとは': return 'docker-intro';
      case 'コンテナとVMの違い': return 'container-vs-vm';
      case 'Docker基本コマンド': return 'docker-basic-commands';
      case 'Dockerfile': return 'dockerfile';
      case 'Docker Compose': return 'docker-compose';
      case 'Docker ネットワーク': return 'docker-networks';
      case 'Docker ボリューム': return 'docker-volumes';
      case 'Dockerベストプラクティス': return 'docker-best-practices';
      default: return null;
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <motion.div 
      className={styles.dockerGuide}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h2 
        className={styles.title}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        data-version="v1.2.0"
      >
        Docker チュートリアル
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
        <strong>学習テーマ：</strong> {steps[currentStep].development || "基礎概念"}
        <div className={styles.userLevel}>
          <span>学習レベル: {getDifficultyLevelName(progress.difficultyLevel)}</span>
          {progress.badges.length > 0 && (
            <div className={styles.badges}>
              {progress.badges.map((badge, index) => (
                <span key={index} className={styles.badge} title={getBadgeDescription(badge)}>
                  {getBadgeEmoji(badge)}
                </span>
              ))}
            </div>
          )}
        </div>
        <motion.div className={styles.viewToggle}>
          <button 
            className={`${styles.viewToggleButton} ${viewMode === 'text' ? styles.active : ''}`}
            onClick={() => setViewMode('text')}
          >
            テキスト中心
          </button>
          <button 
            className={`${styles.viewToggleButton} ${viewMode === 'graphic' ? styles.active : ''}`}
            onClick={() => setViewMode('graphic')}
          >
            図解中心
          </button>
          <button 
            className={`${styles.viewToggleButton} ${animationEnabled ? styles.active : ''}`}
            onClick={() => setAnimationEnabled(!animationEnabled)}
          >
            {animationEnabled ? 'アニメーション ON' : 'アニメーション OFF'}
          </button>
          <select 
            className={styles.languageSelector}
            value={progress.language}
            onChange={(e) => handleLanguageChange(e.target.value as 'ja' | 'en')}
          >
            <option value="ja">日本語</option>
            <option value="en">English</option>
          </select>
        </motion.div>
      </motion.div>
      
      <motion.div 
        className={styles.content}
        key={currentStep}
        initial={animationEnabled ? { opacity: 0 } : false}
        animate={animationEnabled ? { opacity: 1 } : false}
        transition={animationEnabled ? { duration: 0.5 } : { duration: 0 }}
      >
        {/* 学習進捗に基づいたコンテンツの適応表示 */}
        {steps[currentStep].content}
        
        {/* 学習進捗に基づくアダプティブコンテンツ */}
        {currentStep > 0 && progress.completedTopics.includes(getTopicIdFromTitle(steps[currentStep-1].title) || '') && (
          <div className={styles.adaptiveLearning}>
            <div className={styles.previousKnowledge}>
              <h4>前回の学習内容を活かして</h4>
              <p>前回学習した{steps[currentStep-1].title}の知識を活かして、{steps[currentStep].title}をマスターしましょう。</p>
            </div>
          </div>
        )}
        
        {/* 難易度レベルに応じた追加コンテンツ */}
        {progress.difficultyLevel >= DifficultyLevel.INTERMEDIATE && currentStep >= 3 && (
          <div className={styles.advancedContent}>
            <h4>上級者向け追加情報</h4>
            <p>あなたのレベルに合わせた上級者向けの追加情報です。</p>
            <ul>
              <li>最適化テクニック: マルチステージビルドや軽量イメージの活用</li>
              <li>セキュリティベストプラクティス: 非rootユーザーの使用と権限制限</li>
              <li>CI/CDパイプラインとの統合: GitHubアクションやJenkins連携</li>
            </ul>
          </div>
        )}
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

// 難易度レベル名を取得
const getDifficultyLevelName = (level: DifficultyLevel): string => {
  switch (level) {
    case DifficultyLevel.BEGINNER:
      return '初心者';
    case DifficultyLevel.BASIC:
      return '基本';
    case DifficultyLevel.INTERMEDIATE:
      return '中級';
    case DifficultyLevel.ADVANCED:
      return '上級';
    default:
      return '不明';
  }
};

// バッジの説明を取得
const getBadgeDescription = (badge: string): string => {
  switch (badge) {
    case 'beginner-scholar':
      return 'Docker基礎知識マスター';
    case 'command-novice':
      return 'コマンド達成者';
    case 'docker-architect':
      return 'Docker構成設計者';
    default:
      return 'バッジ';
  }
};

// バッジの絵文字を取得
const getBadgeEmoji = (badge: string): string => {
  switch (badge) {
    case 'beginner-scholar':
      return '🎓';
    case 'command-novice':
      return '⌨️';
    case 'docker-architect':
      return '🏗️';
    default:
      return '🏅';
  }
};

export default DockerGuide;