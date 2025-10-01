"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './DockerVisualizer.module.css';
import { 
  DockerState, Container, PortMapping, VolumeMapping, 
  DockerStateChangeEvent, DockerEventObserver, ContainerRelationship,
  DockerEducationalTip, AnimationState
} from './DockerTypes';

interface DockerVisualizerProps {
  dockerState: DockerState;
  onDockerStateChange?: (newState: DockerState, event?: DockerStateChangeEvent) => void;
  showAnimations?: boolean;
  educationalMode?: boolean;
  difficultyLevel?: number;
}

export default function DockerVisualizer({ 
  dockerState, 
  onDockerStateChange,
  showAnimations = true,
  educationalMode = true,
  difficultyLevel = 1
}: DockerVisualizerProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [previousState, setPreviousState] = useState<DockerState | null>(null);
  const [animationState, setAnimationState] = useState<AnimationState>({
    isAnimating: false,
    type: 'none',
    progress: 0
  });
  const [selectedElement, setSelectedElement] = useState<{
    type: 'container' | 'image' | 'network' | 'volume' | null,
    id: string | null
  }>({
    type: null,
    id: null
  });
  
  // コンテナ間の関係を計算
  const [relationships, setRelationships] = useState<ContainerRelationship[]>([]);
  
  // 教育用ヒント
  const [visibleTips, setVisibleTips] = useState<DockerEducationalTip[]>([]);
  
  // アニメーション効果用のタイマー参照
  const animationTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // アニメーション完了時の処理
  const handleAnimationComplete = useCallback(() => {
    if (animationState.onComplete) {
      animationState.onComplete();
    }
    setAnimationState(prev => ({ ...prev, isAnimating: false, progress: 100 }));
    
    // ステータス変更に応じた教育用ヒントを表示（自動）
    if (educationalMode && animationState.type && animationState.targetId) {
      const eventType = animationState.type.split('_')[0] as 'container' | 'network' | 'volume' | 'image';
      setTimeout(() => {
        const tips = getEducationalTipsForEvent(eventType, animationState.type);
        if (tips.length > 0) {
          setVisibleTips(tips);
          // 10秒後に自動で閉じる
          if (animationTimerRef.current) {
            clearTimeout(animationTimerRef.current);
          }
          animationTimerRef.current = setTimeout(() => setVisibleTips([]), 10000);
        }
      }, 500);
    }
  }, [animationState, educationalMode]);
  
  // Docker状態の変更を検出して処理
  useEffect(() => {
    if (!previousState) {
      // 初回レンダリング時は前回の状態を設定するだけ
      setPreviousState(dockerState);
      return;
    }

    // 状態の変化を検出
    const detectStateChanges = () => {
      // 新しいコンテナの検出
      const newContainers = dockerState.containers.filter(
        container => !previousState.containers.some(c => c.id === container.id)
      );
      
      if (newContainers.length > 0) {
        setAnimationState({
          isAnimating: true,
          type: 'container_created',
          targetId: newContainers[0].id,
          progress: 0
        });
        
        // アニメーション完了後に実行するコールバック
        setTimeout(() => {
          handleAnimationComplete();
        }, showAnimations ? 600 : 0);
      }
      
      // ステータスが変更されたコンテナの検出
      const statusChangedContainers = dockerState.containers.filter(container => {
        const previousContainer = previousState.containers.find(c => c.id === container.id);
        return previousContainer && previousContainer.status !== container.status;
      });
      
      if (statusChangedContainers.length > 0) {
        const changedContainer = statusChangedContainers[0];
        const eventType = changedContainer.status === 'running' 
          ? 'container_started' 
          : 'container_stopped';
          
        setAnimationState({
          isAnimating: true,
          type: eventType,
          targetId: changedContainer.id,
          progress: 0
        });
        
        setTimeout(() => {
          handleAnimationComplete();
        }, showAnimations ? 400 : 0);
      }
      
      // 削除されたコンテナの検出
      const removedContainers = previousState.containers.filter(
        container => !dockerState.containers.some(c => c.id === container.id)
      );
      
      if (removedContainers.length > 0) {
        setAnimationState({
          isAnimating: true,
          type: 'container_removed',
          targetId: removedContainers[0].id,
          progress: 0
        });
        
        setTimeout(() => {
          handleAnimationComplete();
        }, showAnimations ? 500 : 0);
      }
      
      // ネットワークの変更検出
      if (previousState.networks.length !== dockerState.networks.length) {
        const eventType = previousState.networks.length < dockerState.networks.length
          ? 'network_created'
          : 'network_removed';
          
        setAnimationState({
          isAnimating: true,
          type: eventType,
          progress: 0
        });
        
        setTimeout(() => {
          handleAnimationComplete();
        }, showAnimations ? 300 : 0);
      }
      
      // ボリュームの変更検出
      if (previousState.volumes.length !== dockerState.volumes.length) {
        const eventType = previousState.volumes.length < dockerState.volumes.length
          ? 'volume_created'
          : 'volume_removed';
          
        setAnimationState({
          isAnimating: true,
          type: eventType,
          progress: 0
        });
        
        setTimeout(() => {
          handleAnimationComplete();
        }, showAnimations ? 300 : 0);
      }
    };
    
    // 前回の状態と現在の状態が異なる場合に変更を検出
    if (JSON.stringify(previousState) !== JSON.stringify(dockerState)) {
      detectStateChanges();
      // 新しい状態を保存
      setPreviousState(dockerState);
    }
  }, [dockerState, previousState, showAnimations, handleAnimationComplete]);
  
  // コンテナ間の関係を計算
  useEffect(() => {
    const newRelationships: ContainerRelationship[] = [];
    
    // コンテナとネットワークの関係
    dockerState.containers.forEach(container => {
      container.networks.forEach(network => {
        newRelationships.push({
          from: container.id,
          to: `network:${network}`,
          type: 'network',
          network
        });
      });
      
      // コンテナとボリュームの関係
      container.volumes.forEach(volume => {
        newRelationships.push({
          from: container.id,
          to: `volume:${volume.host}`,
          type: 'volume',
          volume: volume.host
        });
      });
    });
    
    setRelationships(newRelationships);
  }, [dockerState]);
  
  // レンダリング用のメイン関数
  useEffect(() => {
    if (!canvasRef.current) return;
    
    // 既存の要素をクリア
    while (canvasRef.current.firstChild) {
      canvasRef.current.removeChild(canvasRef.current.firstChild);
    }
    
    // アニメーション状態をリセット（新たにレンダリングする場合）
    if (animationState.isAnimating && animationState.progress >= 100) {
      setAnimationState({
        isAnimating: false,
        type: 'none',
        progress: 0
      });
    }
    
    // コンテナがない場合は初期メッセージを表示
    if (dockerState.containers.length === 0) {
      const emptyMsg = document.createElement('div');
      emptyMsg.className = styles.emptyState;
      emptyMsg.innerHTML = `
        <div class="${styles.emptyIcon}">🐳</div>
        <h3>まだコンテナはありません</h3>
        <p>コンテナを作成すると、ここに可視化されます。</p>
      `;
      canvasRef.current.appendChild(emptyMsg);
      return;
    }
    
    // Docker可視化のためのエレメントを構築
    const visualization = document.createElement('div');
    visualization.className = styles.visualization;
    
    // ホストマシン要素
    const hostMachine = document.createElement('div');
    hostMachine.className = styles.hostMachine;
    hostMachine.innerHTML = `
      <div class="${styles.hostHeader}">
        <span class="${styles.hostIcon}">💻</span>
        ホストマシン
      </div>
      <div class="${styles.hostContent}"></div>
    `;
    
    // イメージセクション
    const images = document.createElement('div');
    images.className = styles.images;
    images.innerHTML = `<div class="${styles.sectionTitle}">Dockerイメージ</div>`;
    
    const imagesList = document.createElement('div');
    imagesList.className = styles.imagesList;
    
    dockerState.images.forEach(image => {
      const imageEl = document.createElement('div');
      imageEl.className = styles.imageItem;
      
      // イメージ名とタグの分離
      const [imageName, imageTag] = image.split(':');
      
      imageEl.innerHTML = `
        <div class="${styles.imageIcon}">📦</div>
        <div class="${styles.imageDetails}">
          <div class="${styles.imageName}">${imageName}</div>
          <div class="${styles.imageTag}">${imageTag || 'latest'}</div>
        </div>
      `;
      imagesList.appendChild(imageEl);
      
      // インタラクティブなツールチップ
      imageEl.addEventListener('click', () => {
        const tooltip = document.createElement('div');
        tooltip.className = styles.tooltip;
        tooltip.innerHTML = `
          <div class="${styles.tooltipHeader}">Dockerイメージとは</div>
          <div class="${styles.tooltipBody}">
            <p>Dockerイメージはアプリケーションと実行環境を含むスナップショットです。</p>
            <p>イメージは<span class="${styles.highlight}">読み取り専用</span>で、コンテナ起動の元になります。</p>
            <p><strong>名前:タグ</strong>形式で識別され、タグがない場合は<strong>latest</strong>とみなされます。</p>
          </div>
        `;
        
        // 既存のツールチップを削除
        const existingTooltips = canvasRef.current?.querySelectorAll(`.${styles.tooltip}`);
        existingTooltips?.forEach(tip => tip.remove());
        
        // 新しいツールチップを追加
        imageEl.appendChild(tooltip);
        
        // クリックでツールチップを閉じる
        tooltip.addEventListener('click', (e) => {
          e.stopPropagation();
          tooltip.remove();
        });
      });
    });
    
    images.appendChild(imagesList);
    
    // ネットワークセクション
    const networks = document.createElement('div');
    networks.className = styles.networks;
    networks.innerHTML = `<div class="${styles.sectionTitle}">ネットワーク</div>`;
    
    const networkDiagram = document.createElement('div');
    networkDiagram.className = styles.networkDiagram;
    
    dockerState.networks.forEach(network => {
      const networkEl = document.createElement('div');
      networkEl.className = styles.network;
      networkEl.innerHTML = `
        <div class="${styles.networkLabel}">
          <span class="${styles.networkIcon}">🔄</span>
          ${network}
        </div>
        <div class="${styles.networkContainers}">
          ${dockerState.containers
            .filter(container => container.networks.includes(network))
            .map(container => {
              let statusClass = '';
              if (container.status === 'running') statusClass = styles.running;
              else if (container.status === 'exited') statusClass = styles.exited;
              else if (container.status === 'created') statusClass = styles.created;
              
              return `
                <div class="${styles.networkContainerBadge} ${statusClass}">
                  ${container.name}
                </div>
              `;
            }).join('')}
        </div>
      `;
      networkDiagram.appendChild(networkEl);
      
      // インタラクティブ要素の追加
      networkEl.addEventListener('click', () => {
        const tooltip = document.createElement('div');
        tooltip.className = styles.tooltip;
        tooltip.innerHTML = `
          <div class="${styles.tooltipHeader}">Dockerネットワークとは</div>
          <div class="${styles.tooltipBody}">
            <p>Dockerネットワークはコンテナ間の通信を可能にする仮想ネットワークです。</p>
            <p>同じネットワーク上のコンテナは<span class="${styles.highlight}">コンテナ名</span>でお互いに通信できます。</p>
            <p><strong>ブリッジネットワーク</strong>：デフォルトのネットワークタイプ</p>
            <p><strong>ホストネットワーク</strong>：ホストのネットワークを直接使用</p>
          </div>
        `;
        
        // 既存のツールチップを削除
        const existingTooltips = canvasRef.current?.querySelectorAll(`.${styles.tooltip}`);
        existingTooltips?.forEach(tip => tip.remove());
        
        // 新しいツールチップを追加
        networkEl.appendChild(tooltip);
        
        // クリックでツールチップを閉じる
        tooltip.addEventListener('click', (e) => {
          e.stopPropagation();
          tooltip.remove();
        });
      });
    });
    
    networks.appendChild(networkDiagram);
    
    // コンテナセクション
    const containers = document.createElement('div');
    containers.className = styles.containers;
    containers.innerHTML = `<div class="${styles.sectionTitle}">コンテナ</div>`;
    
    dockerState.containers.forEach(container => {
      const containerEl = document.createElement('div');
      containerEl.className = `${styles.container} ${styles[container.status]}`;
      
      // ステータスに応じたアイコンを表示
      let statusIcon = '⚪️';
      let statusText = 'Unknown';
      if (container.status === 'running') {
        statusIcon = '🟢';
        statusText = '実行中';
      } else if (container.status === 'exited') {
        statusIcon = '🔴';
        statusText = '停止';
      } else if (container.status === 'created') {
        statusIcon = '🟡';
        statusText = '作成済み';
      }
      
      containerEl.innerHTML = `
        <div class="${styles.containerHeader}">
          <span class="${styles.containerStatusIcon}">${statusIcon}</span>
          <span class="${styles.containerName}">${container.name}</span>
          <span class="${styles.containerStatusText}">${statusText}</span>
        </div>
        <div class="${styles.containerDetails}">
          <div class="${styles.containerImage}">イメージ: ${container.image}</div>
          <div class="${styles.containerPorts}">
            <span>ポート:</span>
            ${container.ports.length === 0 ? 
              '<div class="' + styles.noMapping + '">なし</div>' :
              container.ports.map(port => 
                `<div class="${styles.portMapping}">
                  <span class="${styles.hostPort}">${port.host}</span>
                  <span class="${styles.mappingArrow}">→</span>
                  <span class="${styles.containerPort}">${port.container}</span>
                </div>`
              ).join('')
            }
          </div>
          <div class="${styles.containerVolumes}">
            <span>ボリューム:</span>
            ${container.volumes.length === 0 ? 
              '<div class="' + styles.noMapping + '">なし</div>' :
              container.volumes.map(volume => 
                `<div class="${styles.volumeMapping}">
                  <span class="${styles.hostVolume}">${volume.host}</span>
                  <span class="${styles.mappingArrow}">→</span>
                  <span class="${styles.containerVolume}">${volume.container}</span>
                </div>`
              ).join('')
            }
          </div>
          <div class="${styles.containerNetworks}">
            <span>ネットワーク:</span>
            ${container.networks.map(network => 
              `<div class="${styles.networkTag}">${network}</div>`
            ).join('')}
          </div>
        </div>
      `;
      
      containers.appendChild(containerEl);
      
      // インタラクティブ要素の追加
      containerEl.addEventListener('click', () => {
        // コンテナ詳細パネルを表示する機能
        const detailPanel = document.createElement('div');
        detailPanel.className = styles.containerDetailPanel;
        
        // ステータスに応じた背景色のクラスを適用
        detailPanel.classList.add(styles[`${container.status}Detail`]);
        
        detailPanel.innerHTML = `
          <div class="${styles.detailHeader}">
            <div class="${styles.detailTitle}">
              <span class="${styles.containerStatusIcon}">${statusIcon}</span>
              ${container.name}
            </div>
            <div class="${styles.detailClose}">✕</div>
          </div>
          <div class="${styles.detailContent}">
            <div class="${styles.detailSection}">
              <h4>コンテナ情報</h4>
              <div class="${styles.detailRow}">
                <span class="${styles.detailLabel}">ID:</span>
                <span class="${styles.detailValue}">${container.id}</span>
              </div>
              <div class="${styles.detailRow}">
                <span class="${styles.detailLabel}">ステータス:</span>
                <span class="${styles.detailValue}">${statusText}</span>
              </div>
              <div class="${styles.detailRow}">
                <span class="${styles.detailLabel}">イメージ:</span>
                <span class="${styles.detailValue}">${container.image}</span>
              </div>
            </div>
            
            <div class="${styles.detailSection}">
              <h4>ポートマッピング</h4>
              ${container.ports.length === 0 ? 
                '<div class="' + styles.noDetail + '">ポートマッピングはありません</div>' :
                container.ports.map(port => 
                  `<div class="${styles.detailRow}">
                    <span class="${styles.detailLabel}">ホスト:コンテナ</span>
                    <span class="${styles.detailValue}">${port.host}:${port.container}</span>
                  </div>`
                ).join('')
              }
            </div>
            
            <div class="${styles.detailSection}">
              <h4>ボリューム</h4>
              ${container.volumes.length === 0 ? 
                '<div class="' + styles.noDetail + '">ボリュームはありません</div>' :
                container.volumes.map(volume => 
                  `<div class="${styles.detailRow}">
                    <span class="${styles.detailLabel}">ホスト:</span>
                    <span class="${styles.detailValue}">${volume.host}</span>
                  </div>
                  <div class="${styles.detailRow}">
                    <span class="${styles.detailLabel}">コンテナ:</span>
                    <span class="${styles.detailValue}">${volume.container}</span>
                  </div>`
                ).join('')
              }
            </div>
            
            <div class="${styles.detailSection}">
              <h4>ネットワーク</h4>
              ${container.networks.map(network => 
                `<div class="${styles.detailRow}">
                  <span class="${styles.detailValue}">${network}</span>
                </div>`
              ).join('')}
            </div>
            
            <div class="${styles.detailHelp}">
              <h4>Dockerコンテナとは</h4>
              <p>
                Dockerコンテナはイメージのインスタンスで、独立した実行環境を提供します。
                ポートマッピングでホストとコンテナ間の通信を可能にし、ボリュームでデータを永続化します。
              </p>
            </div>
          </div>
        `;
        
        // 既存の詳細パネルを削除
        const existingPanels = canvasRef.current?.querySelectorAll(`.${styles.containerDetailPanel}`);
        existingPanels?.forEach(panel => panel.remove());
        
        // 詳細パネルの閉じるボタンの機能を追加
        detailPanel.querySelector(`.${styles.detailClose}`)?.addEventListener('click', (e) => {
          e.stopPropagation();
          detailPanel.remove();
        });
        
        // 新しい詳細パネルを追加
        visualization.appendChild(detailPanel);
      });
    });
    
    // ボリュームセクション
    const volumes = document.createElement('div');
    volumes.className = styles.volumes;
    volumes.innerHTML = `<div class="${styles.sectionTitle}">ボリューム</div>`;
    
    const volumesList = document.createElement('div');
    volumesList.className = styles.volumesList;
    
    dockerState.volumes.forEach(volume => {
      const volumeEl = document.createElement('div');
      volumeEl.className = styles.volume;
      volumeEl.innerHTML = `
        <div class="${styles.volumeIcon}">💾</div>
        <div class="${styles.volumeLabel}">${volume}</div>
      `;
      volumesList.appendChild(volumeEl);
      
      // インタラクティブ要素の追加
      volumeEl.addEventListener('click', () => {
        const tooltip = document.createElement('div');
        tooltip.className = styles.tooltip;
        tooltip.innerHTML = `
          <div class="${styles.tooltipHeader}">Dockerボリュームとは</div>
          <div class="${styles.tooltipBody}">
            <p>Dockerボリュームはコンテナのデータを永続化するための仕組みです。</p>
            <p>コンテナが削除されても、ボリュームのデータは<span class="${styles.highlight}">保持</span>されます。</p>
            <p>主な種類:</p>
            <ul>
              <li><strong>名前付きボリューム</strong>: Docker管理の永続ボリューム</li>
              <li><strong>バインドマウント</strong>: ホストのパスを直接マウント</li>
            </ul>
          </div>
        `;
        
        // 既存のツールチップを削除
        const existingTooltips = canvasRef.current?.querySelectorAll(`.${styles.tooltip}`);
        existingTooltips?.forEach(tip => tip.remove());
        
        // 新しいツールチップを追加
        volumeEl.appendChild(tooltip);
        
        // クリックでツールチップを閉じる
        tooltip.addEventListener('click', (e) => {
          e.stopPropagation();
          tooltip.remove();
        });
      });
    });
    
    volumes.appendChild(volumesList);
    
    // 要素を追加
    hostMachine.querySelector(`.${styles.hostContent}`)?.appendChild(images);
    hostMachine.querySelector(`.${styles.hostContent}`)?.appendChild(networks);
    hostMachine.querySelector(`.${styles.hostContent}`)?.appendChild(containers);
    hostMachine.querySelector(`.${styles.hostContent}`)?.appendChild(volumes);
    visualization.appendChild(hostMachine);
    
    canvasRef.current.appendChild(visualization);
    
    // 関係線を描画する
    drawRelationshipLines(visualization);
    
    // SVG要素を作成して関係線を描画する関数
    function drawRelationshipLines(parentElement: HTMLElement) {
      // SVG要素を作成
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('class', styles.relationshipLines);
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '100%');
      
      // コンテナ、ネットワーク、ボリュームの要素を取得
      const containerElements = parentElement.querySelectorAll(`.${styles.container}`);
      const networkElements = parentElement.querySelectorAll(`.${styles.network}`);
      const volumeElements = parentElement.querySelectorAll(`.${styles.volume}`);
      
      // 関係ごとにラインを描画
      if (containerElements.length > 0 && (networkElements.length > 0 || volumeElements.length > 0)) {
        relationships.forEach(rel => {
          // 要素の座標を取得
          let fromElement: Element | null = null;
          let toElement: Element | null = null;
          
          // 関係の始点と終点を特定
          for (const container of containerElements) {
            if ((container as HTMLElement).dataset.id === rel.from) {
              fromElement = container;
              break;
            }
          }
          
          // 関係の種類に基づいて終点を特定
          if (rel.type === 'network') {
            for (const network of networkElements) {
              if ((network as HTMLElement).dataset.id === `network:${rel.network}`) {
                toElement = network;
                break;
              }
            }
          } else if (rel.type === 'volume') {
            for (const volume of volumeElements) {
              if ((volume as HTMLElement).dataset.id === `volume:${rel.volume}`) {
                toElement = volume;
                break;
              }
            }
          }
          
          // 始点と終点が存在する場合は線を描画
          if (fromElement && toElement) {
            const fromRect = fromElement.getBoundingClientRect();
            const toRect = toElement.getBoundingClientRect();
            const parentRect = parentElement.getBoundingClientRect();
            
            // 親要素を基準にした相対座標を計算
            const fromX = fromRect.left + fromRect.width / 2 - parentRect.left;
            const fromY = fromRect.top + fromRect.height / 2 - parentRect.top;
            const toX = toRect.left + toRect.width / 2 - parentRect.left;
            const toY = toRect.top + toRect.height / 2 - parentRect.top;
            
            // パス要素を作成
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M${fromX},${fromY} Q${fromX},${(fromY + toY) / 2} ${(fromX + toX) / 2},${(fromY + toY) / 2} T${toX},${toY}`);
            path.setAttribute('class', `${styles.relationshipPath} ${styles[rel.type]}`);
            
            // マーカー要素を追加
            const marker = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            marker.setAttribute('cx', toX.toString());
            marker.setAttribute('cy', toY.toString());
            marker.setAttribute('r', '3');
            marker.setAttribute('class', `${styles.relationshipMarker} ${styles[rel.type]}`);
            
            svg.appendChild(path);
            svg.appendChild(marker);
          }
        });
        
        // SVGを親要素に追加
        if (svg.childNodes.length > 0) {
          parentElement.appendChild(svg);
        }
      }
    }
    
  }, [dockerState]);
  
  // 要素クリック時の処理
  const handleElementClick = (type: 'container' | 'image' | 'network' | 'volume', id: string) => {
    if (selectedElement.type === type && selectedElement.id === id) {
      // 同じ要素がクリックされた場合は選択解除
      setSelectedElement({ type: null, id: null });
      setVisibleTips([]);
    } else {
      // 新しい要素を選択
      setSelectedElement({ type, id });
      
      // 要素に応じた教育用ヒントを表示
      if (educationalMode) {
        const tips = getEducationalTipsForElement(type, id);
        setVisibleTips(tips);
      }
    }
  };
  
  // イベントに応じた教育用ヒントを取得
  const getEducationalTipsForEvent = (
    elementType: 'container' | 'image' | 'network' | 'volume',
    eventType: string
  ): DockerEducationalTip[] => {
    const tips: DockerEducationalTip[] = [];
    
    // コンテナイベント関連のヒント
    if (elementType === 'container') {
      if (eventType === 'container_created') {
        tips.push({
          id: 'container-create-event',
          title: 'コンテナの作成',
          content: 'docker run コマンドでコンテナを作成しました。コンテナはイメージから作成され、独立した環境で実行されます。',
          elementType: 'container',
          level: 'beginner'
        });
      } else if (eventType === 'container_started') {
        tips.push({
          id: 'container-start-event',
          title: 'コンテナの起動',
          content: 'コンテナが起動しました。起動中のコンテナはアプリケーションプロセスを実行し、ポートをリッスンしています。',
          elementType: 'container',
          level: 'beginner'
        });
      } else if (eventType === 'container_stopped') {
        tips.push({
          id: 'container-stop-event',
          title: 'コンテナの停止',
          content: 'コンテナを停止しました。停止したコンテナはプロセスを終了していますが、ファイルシステムの状態は保持されています。',
          elementType: 'container',
          level: 'beginner'
        });
      } else if (eventType === 'container_removed') {
        tips.push({
          id: 'container-remove-event',
          title: 'コンテナの削除',
          content: 'コンテナを削除しました。削除されたコンテナのファイルシステムは破棄されますが、ボリュームのデータは保持されます。',
          elementType: 'container',
          level: 'intermediate'
        });
      }
    } else if (elementType === 'network') {
      if (eventType === 'network_created') {
        tips.push({
          id: 'network-create-event',
          title: 'ネットワークの作成',
          content: '新しいDockerネットワークが作成されました。ネットワークはコンテナ間の通信を可能にします。',
          elementType: 'network',
          level: 'intermediate'
        });
      }
    } else if (elementType === 'volume') {
      if (eventType === 'volume_created') {
        tips.push({
          id: 'volume-create-event',
          title: 'ボリュームの作成',
          content: '新しいDockerボリュームが作成されました。ボリュームはコンテナのデータを永続化します。',
          elementType: 'volume',
          level: 'intermediate'
        });
      }
    } else if (elementType === 'image') {
      if (eventType === 'image_pulled') {
        tips.push({
          id: 'image-pull-event',
          title: 'イメージの取得',
          content: '新しいDockerイメージを取得しました。イメージはコンテナを作成するためのテンプレートです。',
          elementType: 'image',
          level: 'beginner'
        });
      }
    }
    
    // 難易度レベルに基づきフィルタリング
    return tips.filter(tip => {
      if (tip.level === 'beginner') return true;
      if (tip.level === 'intermediate' && difficultyLevel >= 2) return true;
      if (tip.level === 'advanced' && difficultyLevel >= 3) return true;
      return false;
    });
  };
  
  // 要素に応じた教育用ヒントを取得
  const getEducationalTipsForElement = (
    type: 'container' | 'image' | 'network' | 'volume', 
    id: string
  ): DockerEducationalTip[] => {
    const tips: DockerEducationalTip[] = [];
    
    // コンテナの教育用ヒント
    if (type === 'container') {
      const container = dockerState.containers.find(c => c.id === id);
      if (container) {
        // コンテナの基本概念
        tips.push({
          id: 'container-basics',
          title: 'コンテナとは',
          content: 'コンテナは、アプリケーションとその依存関係を含む軽量な実行環境です。ホストOSのカーネルを共有しながら、独立したプロセス空間を提供します。',
          elementType: 'container',
          level: 'beginner'
        });
        
        // VM との違い
        tips.push({
          id: 'container-vs-vm',
          title: 'コンテナとVMの違い',
          content: 'コンテナはホストOSのカーネルを共有するため、VMよりも軽量で高速です。VMはハードウェアレベルで分離され、独自のOSを持ちます。',
          elementType: 'container',
          level: 'beginner'
        });
        
        // ポート関連のヒント
        if (container.ports.length > 0) {
          tips.push({
            id: 'port-mapping',
            title: 'ポートマッピング',
            content: 'ホストマシンのポートをコンテナ内のポートにマッピングすることで、外部からのアクセスが可能になります。書式は「ホスト:コンテナ」です。',
            elementType: 'container',
            level: 'beginner'
          });
        }
        
        // ボリューム関連のヒント
        if (container.volumes.length > 0) {
          tips.push({
            id: 'volume-usage',
            title: 'ボリュームマウント',
            content: 'ボリュームはコンテナのデータを永続化します。コンテナが削除されても、ボリュームのデータは保持されます。',
            elementType: 'container',
            level: 'intermediate'
          });
        }
      }
    }
    
    // ネットワークの教育用ヒント
    if (type === 'network') {
      tips.push({
        id: 'network-basics',
        title: 'Dockerネットワーク',
        content: 'Dockerネットワークはコンテナ間の通信を可能にします。同じネットワーク上のコンテナは、コンテナ名で相互にアクセスできます。',
        elementType: 'network',
        level: 'beginner'
      });
      
      // ネットワークの種類
      tips.push({
        id: 'network-types',
        title: 'ネットワークの種類',
        content: 'Dockerには複数のネットワークタイプがあります：bridge（デフォルト）、host（ホストと共有）、none（分離）、overlay（複数ホスト間）など。',
        elementType: 'network',
        level: 'intermediate'
      });
      
      // DNS解決のヒント
      tips.push({
        id: 'network-dns',
        title: 'コンテナDNS解決',
        content: 'Docker内蔵のDNSサーバーにより、同一ネットワーク内のコンテナは名前で互いを検出できます。これによりサービスディスカバリーが容易になります。',
        elementType: 'network',
        level: 'intermediate'
      });
    }
    
    // ボリュームの教育用ヒント
    if (type === 'volume') {
      tips.push({
        id: 'volume-basics',
        title: 'Dockerボリューム',
        content: 'ボリュームはDockerコンテナのデータを永続化するための仕組みです。コンテナのライフサイクルとは独立して管理されます。',
        elementType: 'volume',
        level: 'beginner'
      });
      
      // ボリュームの種類
      tips.push({
        id: 'volume-types',
        title: 'ボリュームの種類',
        content: '名前付きボリューム（Docker管理）、バインドマウント（ホストのパス）、tmpfs（メモリ上）の3種類があります。',
        elementType: 'volume',
        level: 'intermediate'
      });
      
      // ボリュームのベストプラクティス
      tips.push({
        id: 'volume-best-practices',
        title: 'ボリュームのベストプラクティス',
        content: 'コンテナ内のデータベースファイル、設定ファイル、アプリケーションデータなどの永続化が必要なデータには必ずボリュームを使用しましょう。また、複数のコンテナで同じデータにアクセスする場合にも有用です。',
        elementType: 'volume',
        level: 'advanced'
      });
    }
    
    // 難易度レベルに基づきフィルタリング
    return tips.filter(tip => {
      if (tip.level === 'beginner') return true;
      if (tip.level === 'intermediate' && difficultyLevel >= 2) return true;
      if (tip.level === 'advanced' && difficultyLevel >= 3) return true;
      return false;
    });
  };
  
  // アニメーション状態に基づくクラス名を生成
  const getAnimationClassName = (elementType: string, elementId: string): string => {
    if (!animationState.isAnimating) return '';
    if (animationState.targetId && animationState.targetId !== elementId) return '';
    
    switch (animationState.type) {
      case 'container_created':
        return elementType === 'container' ? styles.animateCreate : '';
      case 'container_started':
        return elementType === 'container' ? styles.animateStart : '';
      case 'container_stopped':
        return elementType === 'container' ? styles.animateStop : '';
      case 'container_removed':
        return elementType === 'container' ? styles.animateRemove : '';
      case 'network_created':
        return elementType === 'network' ? styles.animateCreate : '';
      case 'network_removed':
        return elementType === 'network' ? styles.animateRemove : '';
      case 'volume_created':
        return elementType === 'volume' ? styles.animateCreate : '';
      case 'volume_removed':
        return elementType === 'volume' ? styles.animateRemove : '';
      case 'image_pulled':
        return elementType === 'image' ? styles.animateCreate : '';
      case 'image_removed':
        return elementType === 'image' ? styles.animateRemove : '';
      default:
        return '';
    }
  };
  
  // コンポーネントのアンマウント時にタイマーをクリア
  useEffect(() => {
    return () => {
      if (animationTimerRef.current) {
        clearTimeout(animationTimerRef.current);
      }
    };
  }, []);

  return (
    <div className={styles.dockerVisualizer}>
      <motion.h2 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Docker環境可視化
      </motion.h2>
      
      <motion.div 
        className={styles.description}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Dockerコンテナ、ネットワーク、ボリュームの関係をビジュアル化して確認できます。
        要素をクリックすると詳細が表示されます。
      </motion.div>
      
      {/* DIVベースの可視化（非React）は保持しつつ、アニメーション用のオーバーレイを追加 */}
      <div className={styles.canvasWrapper}>
        <div className={styles.canvas} ref={canvasRef}></div>
        
        {/* アニメーションオーバーレイ */}
        {showAnimations && animationState.isAnimating && (
          <motion.div 
            className={styles.animationOverlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className={styles.animationStatus}>
              {animationState.type === 'container_created' && '新しいコンテナを作成中...'}
              {animationState.type === 'container_started' && 'コンテナを起動中...'}
              {animationState.type === 'container_stopped' && 'コンテナを停止中...'}
              {animationState.type === 'container_removed' && 'コンテナを削除中...'}
              {animationState.type === 'network_created' && '新しいネットワークを作成中...'}
              {animationState.type === 'network_removed' && 'ネットワークを削除中...'}
              {animationState.type === 'volume_created' && '新しいボリュームを作成中...'}
              {animationState.type === 'volume_removed' && 'ボリュームを削除中...'}
              {animationState.type === 'image_pulled' && '新しいイメージを取得中...'}
              {animationState.type === 'image_removed' && 'イメージを削除中...'}
            </div>
            <motion.div 
              className={styles.progressBar}
              initial={{ width: '0%' }}
              animate={{ width: '100%' }}
              transition={{ duration: 0.5 }}
            />
          </motion.div>
        )}
      </div>
      
      {/* 凡例 */}
      <motion.div 
        className={styles.legend}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.runningLegend}`}></div>
          <span>実行中のコンテナ</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.exitedLegend}`}></div>
          <span>停止したコンテナ</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.createdLegend}`}></div>
          <span>作成済みコンテナ</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.volumeLegend}`}></div>
          <span>ボリューム</span>
        </div>
        <div className={styles.legendItem}>
          <div className={`${styles.legendSymbol} ${styles.networkLegend}`}></div>
          <span>ネットワーク</span>
        </div>
      </motion.div>
      
      {/* 教育用ヒント */}
      <AnimatePresence>
        {visibleTips.length > 0 && (
          <motion.div 
            className={styles.activeTips}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className={styles.tipsHeader}>
              <h3>Docker知識: {selectedElement.type || visibleTips[0].elementType}</h3>
              <button 
                className={styles.closeTips}
                onClick={() => {
                  setVisibleTips([]);
                  if (animationTimerRef.current) {
                    clearTimeout(animationTimerRef.current);
                    animationTimerRef.current = null;
                  }
                }}
              >
                閉じる
              </button>
            </div>
            <div className={styles.tipsList}>
              {visibleTips.map((tip) => (
                <motion.div 
                  key={tip.id}
                  className={styles.tipItem}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <h4>{tip.title}</h4>
                  <p>{tip.content}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 基本的な教育コンテンツ */}
      <motion.div 
        className={styles.educationTips}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <h3>Docker基礎知識</h3>
        <ul>
          <li>
            <strong>コンテナ</strong>: 
            アプリケーションとその依存関係を一緒にパッケージ化したもの。
            ホストOSのカーネルを共有しながら、分離された実行環境を提供します。
          </li>
          <li>
            <strong>イメージ</strong>: 
            コンテナの実行に必要なファイルシステムのスナップショット。
            読み取り専用で、コンテナはこれをもとに実行されます。
          </li>
          <li>
            <strong>ポートマッピング</strong>: 
            ホストマシンのポートからコンテナのポートへのリダイレクト。
            外部からコンテナ内のサービスにアクセスするために使用します。
          </li>
          <li>
            <strong>ボリューム</strong>: 
            コンテナのデータを永続化するための仕組み。
            コンテナのライフサイクルとは独立してデータを保持できます。
          </li>
          <li>
            <strong>ネットワーク</strong>: 
            コンテナ間の通信を可能にするための仮想ネットワーク。
            同じネットワーク内のコンテナはコンテナ名で相互通信できます。
          </li>
        </ul>
      </motion.div>
    </div>
  );
}