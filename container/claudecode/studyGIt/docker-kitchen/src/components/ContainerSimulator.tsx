import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ContainerProvider, useContainers } from '../context/ContainerContext';
import FoodCourt from './FoodCourt';
import ContainerControl from './ContainerControl';
import ResourceMonitor from './ResourceMonitor';
import ContainerList from './ContainerList';

interface ContainerSimulatorProps {
  /** コンテナ操作イベントハンドラ - ダッシュボードとの統合用 */
  onContainerAction?: (containerId: string, action: 'start' | 'stop' | 'remove') => void;
}

const ContainerSimulatorContent: React.FC<ContainerSimulatorProps> = ({ 
  onContainerAction 
}) => {
  const { containers, startContainer, stopContainer, removeContainer } = useContainers();
  
  // 内部処理とイベント発火を行う関数
  const handleStart = (containerId: string) => {
    startContainer(containerId);
    if (onContainerAction) {
      onContainerAction(containerId, 'start');
    }
  };
  
  const handleStop = (containerId: string) => {
    stopContainer(containerId);
    if (onContainerAction) {
      onContainerAction(containerId, 'stop');
    }
  };
  
  const handleRemove = (containerId: string) => {
    removeContainer(containerId);
    if (onContainerAction) {
      onContainerAction(containerId, 'remove');
    }
  };

  return (
    <div className="container mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-docker-blue mb-4">
          フードコートマネージャー（コンテナ管理シミュレーター）
        </h2>
        <p className="mb-6 text-gray-600">
          このシミュレーターでは、Dockerのコンテナ管理をフードコートのテナント管理に例えて学ぶことができます。
          新しいテナント（コンテナ）の出店、営業開始・停止、リソース割り当てなどの操作を行ってみましょう。
        </p>
        
        {/* Main visualization area */}
        <FoodCourt />
        
        {/* Control panels */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ContainerControl />
          </div>
          <div>
            <ResourceMonitor />
          </div>
        </div>
        
        {/* Container list */}
        <div className="mt-8">
          <ContainerList 
            onStart={handleStart}
            onStop={handleStop}
            onRemove={handleRemove}
          />
        </div>
      </div>
    </div>
  );
};

const ContainerSimulator: React.FC<ContainerSimulatorProps> = (props) => {
  // ダッシュボードとの統合時はプロバイダーがダッシュボードから提供されるため、
  // このコンポーネント内でのみプロバイダーを作成するかを確認
  const [isWrappedWithProvider] = useState(false);

  // モジュールとして統合される場合はプロバイダーを作成せず内部コンポーネントのみ返す
  if (isWrappedWithProvider) {
    return <ContainerSimulatorContent {...props} />;
  }

  // スタンドアロンで使用する場合はプロバイダーでラップする
  return (
    <ContainerProvider>
      <ContainerSimulatorContent {...props} />
    </ContainerProvider>
  );
};

export default ContainerSimulator;