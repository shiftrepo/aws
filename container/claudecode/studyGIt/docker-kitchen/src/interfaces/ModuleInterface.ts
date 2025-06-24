import React from 'react';

/**
 * Docker Kitchenのモジュール統合インターフェース
 * リソースダッシュボードと統合するためのモジュール定義
 */
export interface ModuleInterface {
  /** モジュール識別子 */
  id: string;
  
  /** 表示名 */
  title: string;
  
  /** メインコンポーネント */
  component: React.ComponentType<any>;
  
  /** 表示位置 - メインコンテンツかサイドバーか */
  position?: 'main' | 'sidebar';
  
  /** モジュールの初期状態 */
  initialState?: any;
  
  /** イベントハンドラ */
  onEvent?: (event: string, data: any) => void;
}

/**
 * リソースデータインターフェース
 * コンテナなどのリソース情報を表現する共通形式
 */
export interface ResourceData {
  /** リソースタイプ - コンテナまたはVM */
  type: 'container' | 'vm';
  
  /** 識別子 */
  id: string;
  
  /** 表示名 */
  name: string;
  
  /** メトリクス情報 */
  metrics: {
    /** CPU使用率（%） */
    cpu: number;
    
    /** メモリ使用量（MB） */
    memory: number;
    
    /** その他のメトリクス（拡張用） */
    [key: string]: number;
  };
  
  /** 実行状態 */
  status: 'running' | 'stopped' | 'error';
}

/**
 * イベントタイプ定義
 * モジュール間の通信に使用されるイベント
 */
export enum EventType {
  /** リソース選択時 */
  RESOURCE_SELECT = 'resource:select',
  
  /** 状態変更時 */
  STATUS_CHANGE = 'status:change',
  
  /** メトリクス更新時 */
  METRICS_UPDATE = 'metrics:update',
  
  /** Dockerfile更新時 */
  DOCKERFILE_UPDATE = 'dockerfile:update'
}