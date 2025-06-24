// Container Types
export enum ContainerStatus {
  RUNNING = 'running',
  STOPPED = 'stopped',
  PAUSED = 'paused',
  EXITED = 'exited',
}

export enum ContainerType {
  SUSHI = 'sushi',
  RAMEN = 'ramen',
  PIZZA = 'pizza',
  CAFE = 'cafe',
  BAKERY = 'bakery',
}

export interface ResourceAllocation {
  cpu: number; // Percentage (0-100)
  memory: number; // Percentage (0-100)
  disk: number; // Percentage (0-100)
  network: number; // Percentage (0-100)
}

export interface Container {
  id: string;
  name: string;
  type: ContainerType;
  status: ContainerStatus;
  resources: ResourceAllocation;
  ports: Array<{
    host: number;
    container: number;
  }>;
  volumes: Array<{
    host: string;
    container: string;
  }>;
  createdAt: Date;
  logs: string[];
}

// Host System
export interface HostSystem {
  resources: {
    cpu: {
      total: number;
      used: number;
      reserved: number;
    };
    memory: {
      total: number; // in MB
      used: number;
      reserved: number;
    };
    disk: {
      total: number; // in GB
      used: number;
      reserved: number;
    };
  };
  containers: Container[];
}

// Container Images (Templates)
export interface ContainerImage {
  id: string;
  name: string;
  type: ContainerType;
  description: string;
  defaultResources: ResourceAllocation;
  defaultPorts: Array<{
    host: number;
    container: number;
  }>;
}

// Orchestration
export interface ServiceDefinition {
  name: string;
  containerType: ContainerType;
  replicas: number;
  resources: ResourceAllocation;
}

export interface OrchestrationPlan {
  id: string;
  name: string;
  description: string;
  services: ServiceDefinition[];
}