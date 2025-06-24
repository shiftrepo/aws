import { useEffect } from 'react';
import { useContainers } from '../context/ContainerContext';
import { Container, ContainerStatus } from '../models/types';

/**
 * Custom hook for handling container animation states and transitions
 * for status changes like running, stopping, etc.
 */
export const useContainerAnimation = () => {
  const { containers, startContainer, stopContainer } = useContainers();
  
  // This effect could handle complex animation sequences based on container status changes
  useEffect(() => {
    // Example: We could add animation delays, sequences, etc. here
    // For instance, we might want to show a "starting" animation before changing to "running"
    
    // For now, this is a placeholder for more complex animation logic
    const runningContainers = containers.filter(c => c.status === ContainerStatus.RUNNING);
    console.log(`Currently running ${runningContainers.length} containers`);
    
  }, [containers]);
  
  // Helper function to get animation properties based on container status
  const getAnimationProps = (container: Container) => {
    switch (container.status) {
      case ContainerStatus.RUNNING:
        return {
          initial: { opacity: 0.6, scale: 0.9 },
          animate: { opacity: 1, scale: 1 },
          transition: { duration: 0.3 }
        };
      case ContainerStatus.STOPPED:
        return {
          initial: { opacity: 1 },
          animate: { opacity: 0.7 },
          transition: { duration: 0.3 }
        };
      case ContainerStatus.PAUSED:
        return {
          initial: { opacity: 1 },
          animate: { opacity: 0.8 },
          transition: { duration: 0.2 }
        };
      default:
        return {
          initial: { opacity: 0 },
          animate: { opacity: 0.6 },
          transition: { duration: 0.3 }
        };
    }
  };
  
  // Animated versions of container operations
  const animatedStartContainer = (containerId: string) => {
    // Could add pre-animation here
    startContainer(containerId);
  };
  
  const animatedStopContainer = (containerId: string) => {
    // Could add pre-animation here
    stopContainer(containerId);
  };
  
  return {
    getAnimationProps,
    animatedStartContainer,
    animatedStopContainer
  };
};