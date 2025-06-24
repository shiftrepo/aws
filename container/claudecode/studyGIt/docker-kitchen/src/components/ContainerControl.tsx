import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useContainers } from '../context/ContainerContext';

const ContainerControl: React.FC = () => {
  const { availableImages, createContainer } = useContainers();
  
  const [selectedImageId, setSelectedImageId] = useState<string>('');
  const [containerName, setContainerName] = useState<string>('');
  const [cpuAllocation, setCpuAllocation] = useState<number>(10);
  const [memoryAllocation, setMemoryAllocation] = useState<number>(15);
  
  const selectedImage = availableImages.find(image => image.id === selectedImageId);
  
  const handleCreateContainer = () => {
    if (!selectedImageId || !containerName) return;
    
    createContainer(selectedImageId, containerName, {
      cpu: cpuAllocation,
      memory: memoryAllocation,
      disk: 10,
      network: 10
    });
    
    // Reset form
    setContainerName('');
    setCpuAllocation(10);
    setMemoryAllocation(15);
  };
  
  return (
    <motion.div 
      className="border rounded-lg p-4 bg-white shadow"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h3 className="text-lg font-semibold mb-4">出店申込 (コンテナ作成)</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              出店タイプ (コンテナイメージ)
            </label>
            <select
              value={selectedImageId}
              onChange={(e) => setSelectedImageId(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-docker-blue focus:border-docker-blue"
            >
              <option value="">選択してください</option>
              {availableImages.map(image => (
                <option key={image.id} value={image.id}>
                  {image.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              店舗名 (コンテナ名)
            </label>
            <input
              type="text"
              value={containerName}
              onChange={(e) => setContainerName(e.target.value)}
              placeholder="例: sushi-shop-1"
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-docker-blue focus:border-docker-blue"
            />
          </div>
        </div>
        
        <div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CPU割り当て (電力契約)
            </label>
            <div className="flex items-center">
              <input
                type="range"
                min="5"
                max="50"
                value={cpuAllocation}
                onChange={(e) => setCpuAllocation(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="ml-2 text-sm text-gray-500 min-w-[40px]">{cpuAllocation}%</span>
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              メモリ割り当て (座席数)
            </label>
            <div className="flex items-center">
              <input
                type="range"
                min="5"
                max="60"
                value={memoryAllocation}
                onChange={(e) => setMemoryAllocation(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="ml-2 text-sm text-gray-500 min-w-[40px]">{memoryAllocation}%</span>
            </div>
          </div>
        </div>
      </div>
      
      {selectedImage && (
        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <h4 className="font-medium text-sm mb-1">{selectedImage.name} 詳細:</h4>
          <p className="text-sm text-gray-600 mb-2">{selectedImage.description}</p>
          <div className="text-xs text-gray-500">
            デフォルトポート: {selectedImage.defaultPorts.map(port => `${port.host}:${port.container}`).join(', ')}
          </div>
        </div>
      )}
      
      <div className="mt-6 flex justify-end">
        <button
          onClick={handleCreateContainer}
          disabled={!selectedImageId || !containerName}
          className={`px-4 py-2 rounded-md text-white ${
            !selectedImageId || !containerName
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-docker-blue hover:bg-blue-700'
          }`}
        >
          出店開始 (コンテナ作成)
        </button>
      </div>
    </motion.div>
  );
};

export default ContainerControl;