import React from 'react';
import { motion } from 'framer-motion';
import { useContainers } from '../context/ContainerContext';
import { ContainerStatus } from '../models/types';

interface ContainerListProps {
  /** 起動イベントハンドラ */
  onStart?: (containerId: string) => void;
  /** 停止イベントハンドラ */
  onStop?: (containerId: string) => void;
  /** 削除イベントハンドラ */
  onRemove?: (containerId: string) => void;
}

const ContainerList: React.FC<ContainerListProps> = ({
  onStart,
  onStop,
  onRemove
}) => {
  const { containers, startContainer, stopContainer, removeContainer } = useContainers();
  
  // コンテナの起動処理
  const handleStart = (containerId: string) => {
    startContainer(containerId);
    if (onStart) {
      onStart(containerId);
    }
  };
  
  // コンテナの停止処理
  const handleStop = (containerId: string) => {
    stopContainer(containerId);
    if (onStop) {
      onStop(containerId);
    }
  };
  
  // コンテナの削除処理
  const handleRemove = (containerId: string) => {
    removeContainer(containerId);
    if (onRemove) {
      onRemove(containerId);
    }
  };
  
  // 経過時間表示のヘルパー関数
  const getTimeElapsed = (createdAt: Date): string => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - createdAt.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return `${diffInSeconds}秒前`;
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
      return `${diffInMinutes}分前`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
      return `${diffInHours}時間前`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}日前`;
  };
  
  return (
    <motion.div
      className="border rounded-lg overflow-hidden bg-white shadow"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold">営業中テナント (コンテナリスト)</h3>
      </div>
      
      {containers.length === 0 ? (
        <div className="p-6 text-center text-gray-500">
          テナントがありません。新しいコンテナを作成してください。
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  コンテナ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  タイプ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  作成日時
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状態
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {containers.map(container => (
                <motion.tr 
                  key={container.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">
                        {container.name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {container.id.substring(0, 8)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {container.type}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {getTimeElapsed(container.createdAt)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      container.status === ContainerStatus.RUNNING 
                        ? 'bg-green-100 text-green-800' 
                        : container.status === ContainerStatus.STOPPED
                          ? 'bg-gray-100 text-gray-800'
                          : container.status === ContainerStatus.PAUSED
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                    }`}>
                      {container.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      {container.status === ContainerStatus.RUNNING ? (
                        <button
                          onClick={() => handleStop(container.id)}
                          className="text-docker-blue hover:text-blue-900"
                        >
                          停止
                        </button>
                      ) : (
                        <button
                          onClick={() => handleStart(container.id)}
                          className="text-kitchen-green hover:text-green-700"
                        >
                          開始
                        </button>
                      )}
                      <button
                        onClick={() => handleRemove(container.id)}
                        className="text-kitchen-red hover:text-red-700"
                      >
                        削除
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};

export default ContainerList;