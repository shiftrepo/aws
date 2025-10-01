import React, { useState } from 'react';
import Link from 'next/link';
import styles from './docker-learning.module.css';

export default function DockerLearning() {
  const [activeTab, setActiveTab] = useState('what-is-container');
  
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>
          Docker<span className={styles.highlight}>学習</span>
        </h1>
        <Link href="/">
          <a className={styles.backLink}>
            トップページへ戻る
          </a>
        </Link>
      </header>

      <nav className={styles.navigation}>
        <ul className={styles.tabList}>
          <li 
            className={`${styles.tab} ${activeTab === 'what-is-container' ? styles.active : ''}`}
            onClick={() => setActiveTab('what-is-container')}
          >
            コンテナとは何か？
          </li>
          <li 
            className={`${styles.tab} ${activeTab === 'vs-virtual-machine' ? styles.active : ''}`}
            onClick={() => setActiveTab('vs-virtual-machine')}
          >
            仮想マシンとの違い
          </li>
          <li 
            className={`${styles.tab} ${activeTab === 'host-container-relation' ? styles.active : ''}`}
            onClick={() => setActiveTab('host-container-relation')}
          >
            ホストとの関係
          </li>
          <li 
            className={`${styles.tab} ${activeTab === 'interactive-demo' ? styles.active : ''}`}
            onClick={() => setActiveTab('interactive-demo')}
          >
            インタラクティブデモ
          </li>
        </ul>
      </nav>

      <main className={styles.content}>
        {activeTab === 'what-is-container' && (
          <div className={styles.tabContent}>
            <h2>コンテナとは何か？</h2>
            <div className={styles.visualContainer}>
              <div className={styles.containerVisual}>
                <div className={styles.containerBox}>
                  <div className={styles.appLayer}>アプリケーション</div>
                  <div className={styles.libLayer}>ライブラリ／依存関係</div>
                  <div className={styles.binLayer}>バイナリ／ツール</div>
                </div>
              </div>
              <div className={styles.description}>
                <p>
                  <strong>コンテナ</strong>は、アプリケーションとその依存関係を一緒にパッケージ化した軽量な実行環境です。
                </p>
                <p>
                  アプリケーションコードだけでなく、ライブラリ、設定ファイル、バイナリなど、
                  アプリケーションの実行に必要なすべてのものを含んでいます。
                </p>
                <p>
                  コンテナは<strong>分離された空間</strong>で動作するため、どの環境でも同じように動作します。
                  「私のマシンでは動作するのに...」という問題を解消します。
                </p>
              </div>
            </div>
            <div className={styles.keyPoints}>
              <h3>コンテナの主な特徴</h3>
              <ul>
                <li><strong>軽量</strong>: 仮想マシンと比べてリソース消費が少ない</li>
                <li><strong>ポータブル</strong>: どの環境でも同じように実行できる</li>
                <li><strong>迅速</strong>: 数秒で起動可能</li>
                <li><strong>分離</strong>: 他のコンテナやホストシステムに影響を与えない</li>
                <li><strong>スケーラブル</strong>: 必要に応じて複数のインスタンスを簡単に作成</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'vs-virtual-machine' && (
          <div className={styles.tabContent}>
            <h2>仮想マシンとの違い</h2>
            <div className={styles.comparisonContainer}>
              <div className={styles.comparisonItem}>
                <h3>コンテナ</h3>
                <div className={styles.containerStack}>
                  <div className={styles.app}>App A + 必要なライブラリ</div>
                  <div className={styles.app}>App B + 必要なライブラリ</div>
                  <div className={styles.app}>App C + 必要なライブラリ</div>
                  <div className={styles.containerEngine}>コンテナエンジン/ランタイム</div>
                  <div className={styles.os}>ホストOS（カーネル共有）</div>
                  <div className={styles.hardware}>ハードウェア</div>
                </div>
                <ul className={styles.featureList}>
                  <li>OSカーネルを共有</li>
                  <li>軽量（MBレベル）</li>
                  <li>起動時間: 数秒</li>
                  <li>OSレベルの仮想化</li>
                </ul>
              </div>
              <div className={styles.comparisonItem}>
                <h3>仮想マシン</h3>
                <div className={styles.vmStack}>
                  <div className={styles.vmBox}>
                    <div className={styles.app}>App A</div>
                    <div className={styles.guestOs}>ゲストOS</div>
                  </div>
                  <div className={styles.vmBox}>
                    <div className={styles.app}>App B</div>
                    <div className={styles.guestOs}>ゲストOS</div>
                  </div>
                  <div className={styles.vmBox}>
                    <div className={styles.app}>App C</div>
                    <div className={styles.guestOs}>ゲストOS</div>
                  </div>
                  <div className={styles.hypervisor}>ハイパーバイザー</div>
                  <div className={styles.hardware}>ハードウェア</div>
                </div>
                <ul className={styles.featureList}>
                  <li>完全なOS（各VMに専用）</li>
                  <li>ハードウェアを仮想化</li>
                  <li>重量級（GBレベル）</li>
                  <li>起動時間: 数分</li>
                </ul>
              </div>
            </div>
            <div className={styles.keyDifference}>
              <p>
                <strong>主な違い</strong>: コンテナは<em>OSレベルを仮想化</em>し、カーネルを共有するのに対し、
                仮想マシンは<em>ハードウェアレベルから完全に仮想化</em>します。
                コンテナは軽量（MBレベル）で高速起動が可能で、複数のコンテナが同一ホスト上で動作します。
                仮想マシンはハイパーバイザーが物理ハードウェアを仮想化し、各VMが独自の完全なオペレーティングシステムを持っています。
              </p>
            </div>
          </div>
        )}

        {activeTab === 'host-container-relation' && (
          <div className={styles.tabContent}>
            <h2>ホストとコンテナの関係</h2>
            <div className={styles.relationshipDiagram}>
              <div className={styles.hostSystem}>
                <h3>ホストシステム</h3>
                <div className={styles.hostComponents}>
                  <div className={styles.hostKernel}>Linuxカーネル</div>
                  <div className={styles.hostResources}>
                    <div>CPU</div>
                    <div>メモリ</div>
                    <div>ストレージ</div>
                    <div>ネットワーク</div>
                  </div>
                </div>
              </div>
              <div className={styles.arrows}>↔</div>
              <div className={styles.containerSystem}>
                <h3>コンテナ</h3>
                <div className={styles.multipleContainers}>
                  <div className={styles.singleContainer}>
                    <div>アプリA</div>
                    <div>ライブラリ</div>
                    <div>名前空間</div>
                    <div>cgroups</div>
                  </div>
                  <div className={styles.singleContainer}>
                    <div>アプリB</div>
                    <div>ライブラリ</div>
                    <div>名前空間</div>
                    <div>cgroups</div>
                  </div>
                </div>
              </div>
            </div>
            <div className={styles.relationshipExplanation}>
              <h3>ホストとコンテナの関係性</h3>
              <ul>
                <li>
                  <strong>カーネル共有</strong>: コンテナはホストOSのカーネルを共有しますが、
                  それぞれのコンテナはファイルシステム、プロセス、ネットワークが分離されています。
                </li>
                <li>
                  <strong>名前空間 (Namespaces)</strong>: Linuxの名前空間機能により、
                  コンテナ内のプロセスが独自の分離された環境を持ちます。
                </li>
                <li>
                  <strong>コントロールグループ (cgroups)</strong>: コンテナが使用できる
                  CPU、メモリ、ディスクI/Oなどのリソースを制限できます。
                </li>
                <li>
                  <strong>ポート転送</strong>: コンテナの内部ポートをホストの特定のポートに
                  マッピングすることで、外部からアクセス可能になります。
                </li>
                <li>
                  <strong>ボリュームマウント</strong>: ホストのディレクトリをコンテナ内に
                  マウントして、データの永続化や共有が可能です。
                </li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'interactive-demo' && (
          <div className={styles.tabContent}>
            <h2>インタラクティブデモ</h2>
            <p className={styles.comingSoon}>
              インタラクティブなDocker学習エクスペリエンスを準備中です。
              近日公開予定ですので、もうしばらくお待ちください。
            </p>
            <div className={styles.mockTerminal}>
              <div className={styles.terminalHeader}>
                <span>Docker ターミナル</span>
              </div>
              <div className={styles.terminalBody}>
                <p>$ docker run -d -p 80:80 nginx</p>
                <p>a7f3s9d8f7a9sd87f9as8d7f9asd8f7</p>
                <p>$ docker ps</p>
                <p className={styles.terminalOutput}>
                CONTAINER ID   IMAGE   COMMAND                  CREATED         STATUS         PORTS                NAMES<br/>
                a7f3s9d8       nginx   "/docker-entrypoint.…"   5 seconds ago   Up 4 seconds   0.0.0.0:80{'->'}80/tcp   inspiring_edison
                </p>
                <p>$ docker exec -it a7f3s9d8 /bin/bash</p>
                <p>root@a7f3s9d8:/# ls</p>
                <p>bin  boot  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var</p>
                <p>root@a7f3s9d8:/# exit</p>
                <p>$ _</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}