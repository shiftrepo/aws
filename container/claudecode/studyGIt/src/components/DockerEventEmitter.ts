/**
 * DockerEventEmitter.ts
 * Docker操作イベントの発行と購読を管理する共通システム
 */

import { DockerState, DockerStateChangeEvent, DockerEventObserver, DockerEventEmitter } from './DockerTypes';

/**
 * Docker イベントバス実装
 * 各コンポーネント間の通信を仲介し、一貫性のあるイベント処理を提供
 */
export class DockerEventBus implements DockerEventEmitter {
  private observers: DockerEventObserver[] = [];
  private currentState: DockerState;

  /**
   * コンストラクタ
   * @param initialState 初期Docker状態
   */
  constructor(initialState: DockerState) {
    this.currentState = { ...initialState };
  }

  /**
   * オブザーバー登録
   * @param observer 登録するDockerEventObserver
   */
  addObserver(observer: DockerEventObserver): void {
    if (!this.observers.includes(observer)) {
      this.observers.push(observer);
    }
  }

  /**
   * オブザーバー削除
   * @param observer 削除するDockerEventObserver
   */
  removeObserver(observer: DockerEventObserver): void {
    this.observers = this.observers.filter(o => o !== observer);
  }

  /**
   * イベント発行
   * @param event 発行するDockerStateChangeEvent
   */
  emitEvent(event: DockerStateChangeEvent): void {
    // すべてのオブザーバーに通知
    this.observers.forEach(observer => {
      try {
        observer.notify(event);
      } catch (error) {
        console.error('Error notifying observer:', error);
      }
    });
  }

  /**
   * 状態更新とイベント発行
   * @param newState 新しいDocker状態
   * @param event 関連するイベント
   */
  updateState(newState: DockerState, event?: DockerStateChangeEvent): void {
    // 前の状態を保存
    const previousState = { ...this.currentState };
    
    // 新しい状態を設定
    this.currentState = { ...newState };
    
    // イベントがない場合は、状態変更に基づいてイベントを推測
    if (!event) {
      event = this.inferEventFromStateChange(previousState, newState);
    }
    
    // イベント発行
    if (event) {
      this.emitEvent(event);
    }
  }

  /**
   * 状態変更からイベントを推測
   * @param previousState 前の状態
   * @param newState 新しい状態
   * @returns 推測されたイベント
   */
  private inferEventFromStateChange(previousState: DockerState, newState: DockerState): DockerStateChangeEvent | undefined {
    // コンテナ変更のチェック
    const prevContainers = new Set(previousState.containers.map(c => c.id));
    const newContainers = new Set(newState.containers.map(c => c.id));
    
    // 追加されたコンテナ
    const addedContainers = [...newState.containers].filter(c => !prevContainers.has(c.id));
    if (addedContainers.length > 0) {
      return {
        type: 'container_created',
        payload: { containers: addedContainers }
      };
    }
    
    // 削除されたコンテナ
    const removedContainers = [...previousState.containers].filter(c => !newContainers.has(c.id));
    if (removedContainers.length > 0) {
      return {
        type: 'container_removed',
        payload: { containers: removedContainers }
      };
    }
    
    // ステータス変更のチェック
    for (const newContainer of newState.containers) {
      const prevContainer = previousState.containers.find(c => c.id === newContainer.id);
      if (prevContainer && prevContainer.status !== newContainer.status) {
        if (newContainer.status === 'running') {
          return {
            type: 'container_started',
            payload: { container: newContainer }
          };
        } else if (newContainer.status === 'exited' || newContainer.status === 'paused') {
          return {
            type: 'container_stopped',
            payload: { container: newContainer }
          };
        }
      }
    }
    
    // イメージ変更のチェック
    const prevImages = new Set(previousState.images);
    const newImages = new Set(newState.images);
    
    // 追加されたイメージ
    const addedImages = [...newState.images].filter(img => !prevImages.has(img));
    if (addedImages.length > 0) {
      return {
        type: 'image_pulled',
        payload: { images: addedImages }
      };
    }
    
    // 削除されたイメージ
    const removedImages = [...previousState.images].filter(img => !newImages.has(img));
    if (removedImages.length > 0) {
      return {
        type: 'image_removed',
        payload: { images: removedImages }
      };
    }
    
    // ネットワーク変更のチェック
    const prevNetworks = new Set(previousState.networks);
    const newNetworks = new Set(newState.networks);
    
    // 追加されたネットワーク
    const addedNetworks = [...newState.networks].filter(net => !prevNetworks.has(net));
    if (addedNetworks.length > 0) {
      return {
        type: 'network_created',
        payload: { networks: addedNetworks }
      };
    }
    
    // 削除されたネットワーク
    const removedNetworks = [...previousState.networks].filter(net => !newNetworks.has(net));
    if (removedNetworks.length > 0) {
      return {
        type: 'network_removed',
        payload: { networks: removedNetworks }
      };
    }
    
    // ボリューム変更のチェック
    const prevVolumes = new Set(previousState.volumes);
    const newVolumes = new Set(newState.volumes);
    
    // 追加されたボリューム
    const addedVolumes = [...newState.volumes].filter(vol => !prevVolumes.has(vol));
    if (addedVolumes.length > 0) {
      return {
        type: 'volume_created',
        payload: { volumes: addedVolumes }
      };
    }
    
    // 削除されたボリューム
    const removedVolumes = [...previousState.volumes].filter(vol => !newVolumes.has(vol));
    if (removedVolumes.length > 0) {
      return {
        type: 'volume_removed',
        payload: { volumes: removedVolumes }
      };
    }
    
    // 特定の変更が検出されない場合
    return undefined;
  }

  /**
   * 現在の状態を取得
   * @returns 現在のDocker状態
   */
  getState(): DockerState {
    return { ...this.currentState };
  }
}