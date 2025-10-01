/**
 * DockerTypes.ts
 * Shared type definitions for Docker-related components
 */

// コンテナの状態タイプ
export type ContainerStatus = 'running' | 'exited' | 'created' | 'paused';

// ポートマッピングインターフェース
export interface PortMapping {
  host: string;
  container: string;
}

// ボリュームマッピングインターフェース
export interface VolumeMapping {
  host: string;
  container: string;
}

// コンテナインターフェース
export interface Container {
  id: string;
  name: string;
  image: string;
  status: ContainerStatus;
  ports: PortMapping[];
  volumes: VolumeMapping[];
  networks: string[];
  env?: Record<string, string>;
  command?: string;
  created: string;
  // ビジュアライゼーション用拡張プロパティ
  x?: number;
  y?: number;
  highlighted?: boolean;
}

// イメージインターフェース
export interface DockerImage {
  id: string;
  repository: string;
  tag: string;
  size: string;
  created: string;
}

// Docker状態インターフェース
export interface DockerState {
  containers: Container[];
  images: string[];
  volumes: string[];
  networks: string[];
}

// Docker状態変更イベント
export type DockerStateChangeEvent = {
  type: 'container_created' | 'container_started' | 'container_stopped' | 'container_removed' | 
        'image_pulled' | 'image_removed' | 
        'network_created' | 'network_removed' | 
        'volume_created' | 'volume_removed' |
        'state_reset';
  payload: any;
}

// Docker状態リスナーインターフェース
export interface DockerStateListener {
  onDockerStateChange: (state: DockerState, event?: DockerStateChangeEvent) => void;
}

// コンテナの相互関係
export interface ContainerRelationship {
  from: string; // コンテナID または 'host'
  to: string;   // コンテナID または 'network:network_name' または 'volume:volume_name'
  type: 'network' | 'volume' | 'depends_on';
  network?: string; // ネットワーク名（type='network'の場合）
  volume?: string;  // ボリューム名（type='volume'の場合）
}

// 教育用ヒントインターフェース
export interface DockerEducationalTip {
  id: string;
  title: string;
  content: string;
  elementType: 'container' | 'image' | 'network' | 'volume' | 'port' | 'command';
  level: 'beginner' | 'intermediate' | 'advanced';
}

// アニメーションの状態
export interface AnimationState {
  isAnimating: boolean;
  type: string;
  targetId?: string;
  progress: number; // 0-100
  onComplete?: () => void;
}

// 難易度レベル
export enum DifficultyLevel {
  BEGINNER = 1,
  BASIC = 2,
  INTERMEDIATE = 3,
  ADVANCED = 4
}

// Docker操作イベントオブザーバー
export interface DockerEventObserver {
  // イベント通知メソッド
  notify(event: DockerStateChangeEvent): void;
}

// Docker操作イベント発行者
export interface DockerEventEmitter {
  // オブザーバー登録
  addObserver(observer: DockerEventObserver): void;
  
  // オブザーバー削除
  removeObserver(observer: DockerEventObserver): void;
  
  // イベント発行
  emitEvent(event: DockerStateChangeEvent): void;
}