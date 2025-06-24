import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { 
  Container, 
  ContainerStatus, 
  ContainerType, 
  ResourceAllocation,
  HostSystem, 
  ContainerImage 
} from '../models/types';

// Define available container templates
const containerTemplates: ContainerImage[] = [
  {
    id: 'nginx',
    name: '寿司屋 (Nginx)',
    type: ContainerType.SUSHI,
    description: 'Webサーバーコンテナ',
    defaultResources: {
      cpu: 10,
      memory: 15,
      disk: 5,
      network: 20
    },
    defaultPorts: [
      { host: 8080, container: 80 }
    ]
  },
  {
    id: 'python',
    name: 'ラーメン屋 (Python)',
    type: ContainerType.RAMEN,
    description: 'Pythonアプリケーションサーバー',
    defaultResources: {
      cpu: 20,
      memory: 25,
      disk: 10,
      network: 15
    },
    defaultPorts: [
      { host: 8000, container: 8000 }
    ]
  },
  {
    id: 'node',
    name: 'ピザ屋 (Node.js)',
    type: ContainerType.PIZZA,
    description: 'Node.jsアプリケーションサーバー',
    defaultResources: {
      cpu: 15,
      memory: 20,
      disk: 8,
      network: 10
    },
    defaultPorts: [
      { host: 3000, container: 3000 }
    ]
  },
  {
    id: 'mongodb',
    name: 'カフェ (MongoDB)',
    type: ContainerType.CAFE,
    description: 'データベースサーバー',
    defaultResources: {
      cpu: 25,
      memory: 30,
      disk: 40,
      network: 5
    },
    defaultPorts: [
      { host: 27017, container: 27017 }
    ]
  }
];

// Initial host system state
const initialHostSystem: HostSystem = {
  resources: {
    cpu: {
      total: 100,
      used: 0,
      reserved: 0
    },
    memory: {
      total: 8192, // 8GB
      used: 0,
      reserved: 0
    },
    disk: {
      total: 100, // 100GB
      used: 0,
      reserved: 0
    }
  },
  containers: []
};

// Context interface
interface ContainerContextType {
  hostSystem: HostSystem;
  containers: Container[];
  availableImages: ContainerImage[];
  createContainer: (imageId: string, name: string, customResources?: ResourceAllocation) => void;
  startContainer: (containerId: string) => void;
  stopContainer: (containerId: string) => void;
  removeContainer: (containerId: string) => void;
  getContainerById: (containerId: string) => Container | undefined;
  getImageById: (imageId: string) => ContainerImage | undefined;
  updateContainerResources: (containerId: string, resources: ResourceAllocation) => void;
}

// Create context
const ContainerContext = createContext<ContainerContextType | undefined>(undefined);

// Provider component
interface ContainerProviderProps {
  children: ReactNode;
}

export const ContainerProvider = ({ children }: ContainerProviderProps) => {
  const [hostSystem, setHostSystem] = useState<HostSystem>(initialHostSystem);
  const [containers, setContainers] = useState<Container[]>([]);
  
  // Update resource usage whenever containers change
  useEffect(() => {
    const calculateResourceUsage = () => {
      const cpuUsed = containers.reduce((total, container) => {
        if (container.status === ContainerStatus.RUNNING) {
          return total + container.resources.cpu;
        }
        return total;
      }, 0);
      
      const memoryUsed = containers.reduce((total, container) => {
        if (container.status === ContainerStatus.RUNNING) {
          return total + (container.resources.memory * hostSystem.resources.memory.total / 100);
        }
        return total;
      }, 0);
      
      const diskUsed = containers.reduce((total, container) => {
        return total + (container.resources.disk * hostSystem.resources.disk.total / 100);
      }, 0);
      
      return {
        cpu: cpuUsed,
        memory: memoryUsed,
        disk: diskUsed
      };
    };
    
    const usage = calculateResourceUsage();
    
    setHostSystem(prev => ({
      ...prev,
      resources: {
        ...prev.resources,
        cpu: {
          ...prev.resources.cpu,
          used: usage.cpu
        },
        memory: {
          ...prev.resources.memory,
          used: usage.memory
        },
        disk: {
          ...prev.resources.disk,
          used: usage.disk
        }
      }
    }));
  }, [containers]);
  
  // Get container image template by ID
  const getImageById = (imageId: string) => {
    return containerTemplates.find(image => image.id === imageId);
  };
  
  // Get container by ID
  const getContainerById = (containerId: string) => {
    return containers.find(container => container.id === containerId);
  };
  
  // Create new container
  const createContainer = (imageId: string, name: string, customResources?: ResourceAllocation) => {
    const template = getImageById(imageId);
    
    if (!template) {
      console.error(`Container template ${imageId} not found`);
      return;
    }
    
    const resources = customResources || template.defaultResources;
    
    const newContainer: Container = {
      id: uuidv4(),
      name,
      type: template.type,
      status: ContainerStatus.STOPPED, // Start as stopped
      resources,
      ports: [...template.defaultPorts],
      volumes: [],
      createdAt: new Date(),
      logs: [`Created container ${name} from ${template.name}`]
    };
    
    setContainers(prevContainers => [...prevContainers, newContainer]);
  };
  
  // Start container
  const startContainer = (containerId: string) => {
    setContainers(prevContainers => 
      prevContainers.map(container => 
        container.id === containerId 
          ? { 
              ...container, 
              status: ContainerStatus.RUNNING,
              logs: [...container.logs, `Container started at ${new Date().toISOString()}`]
            }
          : container
      )
    );
  };
  
  // Stop container
  const stopContainer = (containerId: string) => {
    setContainers(prevContainers => 
      prevContainers.map(container => 
        container.id === containerId 
          ? { 
              ...container, 
              status: ContainerStatus.STOPPED,
              logs: [...container.logs, `Container stopped at ${new Date().toISOString()}`]
            }
          : container
      )
    );
  };
  
  // Remove container
  const removeContainer = (containerId: string) => {
    setContainers(prevContainers => 
      prevContainers.filter(container => container.id !== containerId)
    );
  };
  
  // Update container resources
  const updateContainerResources = (containerId: string, resources: ResourceAllocation) => {
    setContainers(prevContainers => 
      prevContainers.map(container => 
        container.id === containerId 
          ? { 
              ...container, 
              resources,
              logs: [...container.logs, `Container resources updated at ${new Date().toISOString()}`]
            }
          : container
      )
    );
  };
  
  const value = {
    hostSystem,
    containers,
    availableImages: containerTemplates,
    createContainer,
    startContainer,
    stopContainer,
    removeContainer,
    getContainerById,
    getImageById,
    updateContainerResources
  };
  
  return (
    <ContainerContext.Provider value={value}>
      {children}
    </ContainerContext.Provider>
  );
};

// Custom hook to use the container context
export const useContainers = () => {
  const context = useContext(ContainerContext);
  
  if (context === undefined) {
    throw new Error('useContainers must be used within a ContainerProvider');
  }
  
  return context;
};