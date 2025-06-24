import React from 'react';
import { motion } from 'framer-motion';
import { useContainers } from '../context/ContainerContext';

const ResourceMonitor: React.FC = () => {
  const { hostSystem } = useContainers();
  
  // Calculate the total CPU and memory usage as percentages
  const cpuUsagePercent = (hostSystem.resources.cpu.used / hostSystem.resources.cpu.total) * 100;
  const memoryUsagePercent = (hostSystem.resources.memory.used / hostSystem.resources.memory.total) * 100;
  const diskUsagePercent = (hostSystem.resources.disk.used / hostSystem.resources.disk.total) * 100;
  
  // Get values for memory in more readable format
  const memoryUsedGB = (hostSystem.resources.memory.used / 1024).toFixed(1);
  const memoryTotalGB = (hostSystem.resources.memory.total / 1024).toFixed(1);
  
  const getColorForUsage = (percentage: number): string => {
    if (percentage < 50) return 'text-kitchen-green';
    if (percentage < 80) return 'text-kitchen-orange';
    return 'text-kitchen-red';
  };
  
  return (
    <motion.div 
      className="border rounded-lg p-4 bg-white shadow"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h3 className="text-lg font-semibold mb-4">リソース使用状況</h3>
      
      <div className="space-y-4">
        {/* CPU Usage */}
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">電力使用量 (CPU)</span>
            <span className={`text-sm ${getColorForUsage(cpuUsagePercent)}`}>
              {cpuUsagePercent.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${
                cpuUsagePercent < 50 ? 'bg-kitchen-green' :
                cpuUsagePercent < 80 ? 'bg-kitchen-orange' : 'bg-kitchen-red'
              }`}
              style={{ width: `${cpuUsagePercent}%` }}
            ></div>
          </div>
        </div>
        
        {/* Memory Usage */}
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">水道使用量 (メモリ)</span>
            <span className={`text-sm ${getColorForUsage(memoryUsagePercent)}`}>
              {memoryUsedGB} / {memoryTotalGB} GB
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${
                memoryUsagePercent < 50 ? 'bg-kitchen-green' :
                memoryUsagePercent < 80 ? 'bg-kitchen-orange' : 'bg-kitchen-red'
              }`}
              style={{ width: `${memoryUsagePercent}%` }}
            ></div>
          </div>
        </div>
        
        {/* Disk Usage */}
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">貯蔵庫使用量 (ディスク)</span>
            <span className={`text-sm ${getColorForUsage(diskUsagePercent)}`}>
              {hostSystem.resources.disk.used} / {hostSystem.resources.disk.total} GB
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${
                diskUsagePercent < 50 ? 'bg-kitchen-green' :
                diskUsagePercent < 80 ? 'bg-kitchen-orange' : 'bg-kitchen-red'
              }`}
              style={{ width: `${diskUsagePercent}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t">
        <h4 className="text-sm font-medium text-gray-700 mb-2">システム情報</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="text-gray-500">Docker Engine:</div>
          <div>v20.10.8</div>
          <div className="text-gray-500">実行中のコンテナ:</div>
          <div>{hostSystem.containers.filter(c => c.status === 'running').length}</div>
          <div className="text-gray-500">総コンテナ数:</div>
          <div>{hostSystem.containers.length}</div>
        </div>
      </div>
    </motion.div>
  );
};

export default ResourceMonitor;