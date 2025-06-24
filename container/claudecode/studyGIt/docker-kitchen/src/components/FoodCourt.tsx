import React from 'react';
import { motion } from 'framer-motion';
import { useContainers } from '../context/ContainerContext';
import { ContainerStatus, ContainerType } from '../models/types';
import { FaPizzaSlice, FaRamenBowl, FaWineGlass, FaCoffee, FaBirthdayCake } from 'react-icons/fa';
import { GiSushis } from 'react-icons/gi';

// Container type to icon mapping
const containerIcons: Record<ContainerType, React.ReactNode> = {
  [ContainerType.SUSHI]: <GiSushis size={24} />,
  [ContainerType.RAMEN]: <FaRamenBowl size={24} />,
  [ContainerType.PIZZA]: <FaPizzaSlice size={24} />,
  [ContainerType.CAFE]: <FaCoffee size={24} />,
  [ContainerType.BAKERY]: <FaBirthdayCake size={24} />
};

// Container status to color mapping
const statusColors: Record<ContainerStatus, string> = {
  [ContainerStatus.RUNNING]: 'bg-kitchen-green',
  [ContainerStatus.STOPPED]: 'bg-gray-400',
  [ContainerStatus.PAUSED]: 'bg-kitchen-orange',
  [ContainerStatus.EXITED]: 'bg-kitchen-red'
};

const FoodCourt: React.FC = () => {
  const { containers, hostSystem } = useContainers();
  
  // Calculate the total CPU and memory usage as percentages
  const cpuUsagePercent = (hostSystem.resources.cpu.used / hostSystem.resources.cpu.total) * 100;
  const memoryUsagePercent = (hostSystem.resources.memory.used / hostSystem.resources.memory.total) * 100;
  
  return (
    <div className="relative">
      {/* Food court visual representation */}
      <div className="border-2 border-docker-blue rounded-lg p-4 bg-blue-50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-docker-blue">
            フードコート (ホストシステム)
          </h3>
          <div className="flex space-x-4 text-sm">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-kitchen-green mr-2"></div>
              <span>稼働中</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-gray-400 mr-2"></div>
              <span>停止中</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-kitchen-orange mr-2"></div>
              <span>一時停止</span>
            </div>
          </div>
        </div>
        
        {/* Infrastructure visualization */}
        <div className="mb-6 p-3 border border-gray-300 rounded bg-white shadow-sm">
          <div className="text-sm text-gray-600 mb-2">共有インフラ (カーネル)</div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">電力 (CPU): {cpuUsagePercent.toFixed(1)}%</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-docker-blue rounded-full h-2" 
                  style={{ width: `${cpuUsagePercent}%` }}
                />
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">
                水道 (メモリ): {(hostSystem.resources.memory.used / 1024).toFixed(1)} GB / {(hostSystem.resources.memory.total / 1024).toFixed(1)} GB
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-docker-blue rounded-full h-2" 
                  style={{ width: `${memoryUsagePercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>
        
        {/* Container visualization */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {containers.length === 0 ? (
            <div className="col-span-3 py-10 text-center text-gray-500">
              テナントがありません。新しいコンテナを作成してください。
            </div>
          ) : (
            containers.map(container => (
              <motion.div
                key={container.id}
                className={`border rounded-lg p-4 ${container.status === ContainerStatus.RUNNING ? 'border-kitchen-green' : 'border-gray-300'}`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <div className={`w-10 h-10 rounded-full ${statusColors[container.status]} flex items-center justify-center text-white mr-3`}>
                      {containerIcons[container.type]}
                    </div>
                    <div>
                      <h4 className="font-medium">{container.name}</h4>
                      <div className="text-xs text-gray-500">ID: {container.id.substring(0, 8)}</div>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs ${
                    container.status === ContainerStatus.RUNNING ? 'bg-green-100 text-green-800' :
                    container.status === ContainerStatus.STOPPED ? 'bg-gray-100 text-gray-800' :
                    container.status === ContainerStatus.PAUSED ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {container.status}
                  </div>
                </div>
                
                {/* Resource usage */}
                <div className="mt-3 space-y-2">
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>CPU: {container.resources.cpu}%</span>
                      <span>使用量</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1">
                      <div 
                        className="bg-docker-blue rounded-full h-1" 
                        style={{ width: `${container.resources.cpu}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>メモリ: {container.resources.memory}%</span>
                      <span>{(container.resources.memory * hostSystem.resources.memory.total / 100 / 1024).toFixed(1)} GB</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-1">
                      <div 
                        className="bg-docker-blue rounded-full h-1" 
                        style={{ width: `${container.resources.memory}%` }}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Port mapping */}
                {container.ports.length > 0 && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-1">ポートマッピング:</div>
                    <div className="flex flex-wrap gap-2">
                      {container.ports.map((port, index) => (
                        <div key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {port.host}:{port.container}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))
          )}
        </div>
      </div>
      
      {/* Docker Engine visualization */}
      <div className="mt-4 border-2 border-docker-blue border-dashed rounded-lg p-4 bg-white">
        <h4 className="text-md font-semibold text-docker-blue mb-2">
          フードコート管理事務所 (Docker Engine)
        </h4>
        <div className="text-sm text-gray-600">
          コンテナ数: {containers.length} | 
          実行中: {containers.filter(c => c.status === ContainerStatus.RUNNING).length} | 
          停止中: {containers.filter(c => c.status === ContainerStatus.STOPPED).length}
        </div>
      </div>
    </div>
  );
};

export default FoodCourt;