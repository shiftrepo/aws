// ReactFlow によるGit Flow可視化プロトタイプ

import React, { useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';

// カスタムノードスタイル
const nodeStyles = {
  main: {
    background: '#e74c3c',
    color: 'white',
    border: '1px solid #c0392b',
    borderRadius: '4px',
    padding: '10px',
    width: '150px',
  },
  develop: {
    background: '#3498db',
    color: 'white',
    border: '1px solid #2980b9',
    borderRadius: '4px',
    padding: '10px',
    width: '150px',
  },
  feature: {
    background: '#2ecc71',
    color: 'white',
    border: '1px solid #27ae60',
    borderRadius: '4px',
    padding: '10px',
    width: '150px',
  },
  release: {
    background: '#f39c12',
    color: 'white',
    border: '1px solid #e67e22',
    borderRadius: '4px',
    padding: '10px',
    width: '150px',
  },
  hotfix: {
    background: '#9b59b6',
    color: 'white',
    border: '1px solid #8e44ad',
    borderRadius: '4px',
    padding: '10px',
    width: '150px',
  },
  tag: {
    background: '#f1c40f',
    color: 'black',
    border: '1px solid #f39c12',
    borderRadius: '50%',
    padding: '5px',
    width: '40px',
    height: '40px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }
};

// Git Flowのステップごとのノードとエッジ定義
const gitFlowStepsData = {
  1: {
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        animated: true,
        style: { stroke: '#3498db' }
      }
    ]
  },
  2: {
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login' }, 
        position: { x: 250, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: { stroke: '#3498db' }
      },
      {
        id: 'develop-feature',
        source: 'develop-1',
        target: 'feature-login',
        animated: true,
        style: { stroke: '#2ecc71' }
      }
    ]
  },
  // ステップ3〜10の定義も同様に追加
};

const ReactFlowGitGraph = ({ step }) => {
  const currentStep = Math.min(Math.max(1, step), Object.keys(gitFlowStepsData).length);
  const stepData = gitFlowStepsData[currentStep] || gitFlowStepsData[1];

  const [nodes, setNodes, onNodesChange] = useNodesState(stepData.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(stepData.edges);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div style={{ height: 400, width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
};

export default ReactFlowGitGraph;