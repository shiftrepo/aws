import React, { useEffect, useMemo } from 'react';
import { ModuleInterface, ResourceData, EventType } from '../interfaces/ModuleInterface';
import { ContainerProvider, useContainers } from '../context/ContainerContext';
import ContainerSimulator from '../components/ContainerSimulator';
import { ContainerStatus } from '../models/types';

/**
 * リソースデータへの変換関数
 * コンテナモデルをダッシュボード用のリソースデータに変換する
 */
const mapContainerToResourceData = (container: any): ResourceData => {
  // コンテナステータスをインターフェース定義に変換
  const statusMap: Record<ContainerStatus, 'running' | 'stopped' | 'error'> = {
    [ContainerStatus.RUNNING]: 'running',
    [ContainerStatus.STOPPED]: 'stopped',
    [ContainerStatus.PAUSED]: 'stopped',
    [ContainerStatus.EXITED]: 'error',
  };

  return {
    type: 'container',
    id: container.id,
    name: container.name,
    metrics: {
      cpu: container.resources.cpu,
      memory: container.resources.memory * 81.92, // 8GB * percentage / 100
      disk: container.resources.disk,
      network: container.resources.network,
    },
    status: statusMap[container.status],
  };
};

/**
 * コンテナ管理モジュールの内部コンポーネント
 * イベント通信機能を持ち、ダッシュボードと通信する
 */
const ContainerManagerInternal: React.FC<{
  onEvent?: (event: string, data: any) => void;
}> = ({ onEvent }) => {
  const { containers, startContainer, stopContainer } = useContainers();
  
  // コンテナデータ変更時にメトリクス更新イベントを発火
  useEffect(() => {
    if (onEvent) {
      const resourceData = containers.map(mapContainerToResourceData);
      onEvent(EventType.METRICS_UPDATE, resourceData);
    }
  }, [containers, onEvent]);

  // コンテナの状態変更をハンドリング(内部向け)
  const handleContainerAction = (containerId: string, action: 'start' | 'stop') => {
    if (action === 'start') {
      startContainer(containerId);
    } else {
      stopContainer(containerId);
    }
    
    // 状態変更イベントを発火
    if (onEvent) {
      const container = containers.find(c => c.id === containerId);
      if (container) {
        const resourceData = mapContainerToResourceData(container);
        onEvent(EventType.STATUS_CHANGE, resourceData);
      }
    }
  };

  return <ContainerSimulator onContainerAction={handleContainerAction} />;
};

/**
 * Docker Kitchenダッシュボード統合用のコンテナ管理モジュール定義
 */
export const containerManagerModule: ModuleInterface = {
  id: 'container-manager',
  title: 'コンテナ管理',
  component: ({ onEvent }) => (
    <ContainerProvider>
      <ContainerManagerInternal onEvent={onEvent} />
    </ContainerProvider>
  ),
  position: 'main',
  // ダッシュボードからのイベント受信
  onEvent: (event, data) => {
    // ダッシュボードからのイベントに応じた処理
    console.log(`コンテナ管理モジュールがイベントを受信: ${event}`, data);
  }
};