import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
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
    fontSize: '10px',
    fontWeight: 'bold',
  }
};

// エッジスタイル
const edgeStyles = {
  main: { stroke: '#e74c3c', strokeWidth: 2 },
  develop: { stroke: '#3498db', strokeWidth: 2 },
  feature: { stroke: '#2ecc71', strokeWidth: 2 },
  release: { stroke: '#f39c12', strokeWidth: 2 },
  hotfix: { stroke: '#9b59b6', strokeWidth: 2 },
};

// Git Flowのステップごとのノードとエッジ定義
const gitFlowStepsData = {
  1: {
    title: "開発の開始 - developブランチ",
    description: "プロジェクト開始時、最初にmainブランチからdevelopブランチを作成します。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(開発A面)' }, 
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
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  2: {
    title: "機能開発 - featureブランチ",
    description: "新機能を開発する際は、developブランチからfeatureブランチを作成します。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(開発A面)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature',
        source: 'develop-1',
        target: 'feature-login',
        animated: true,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  3: {
    title: "featureブランチをdevelopにマージ",
    description: "機能の開発とテストが完了したら、featureブランチをdevelopブランチにマージします。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(開発A面)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-2', 
        type: 'default',
        data: { label: 'develop\n(マージ後)' }, 
        position: { x: 350, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature',
        source: 'develop-1',
        target: 'feature-login',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-flow',
        source: 'develop-1',
        target: 'develop-2',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'feature-develop',
        source: 'feature-login',
        target: 'develop-2',
        animated: true,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  3.5: {
    title: "並行開発 - 複数のfeatureブランチ",
    description: "複数の機能を同時に開発するため、developブランチから複数のfeatureブランチを同時に作成します。各チームは並行して独立した機能開発を進めます。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(開発A面)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system\n(チームA:開発中)' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-profile', 
        type: 'default',
        data: { label: 'feature/user-profile\n(チームB:開発中)' }, 
        position: { x: 350, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-search', 
        type: 'default',
        data: { label: 'feature/search\n(チームC:未着手)' }, 
        position: { x: 450, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-notification', 
        type: 'default',
        data: { label: 'feature/notification\n(チームD:未着手)' }, 
        position: { x: 550, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-login',
        source: 'develop-1',
        target: 'feature-login',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-profile',
        source: 'develop-1',
        target: 'feature-profile',
        animated: true,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-search',
        source: 'develop-1',
        target: 'feature-search',
        animated: false,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-notification',
        source: 'develop-1',
        target: 'feature-notification',
        animated: false,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  4: {
    title: "ログイン機能の開発進行",
    description: "チームAはログイン機能の開発を進めています。同時に他のチームも並行して開発を進めており、マージせずに各ブランチで作業することが並行開発の強みです。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(開発A面)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system\n(チームA:開発進行中)' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-profile', 
        type: 'default',
        data: { label: 'feature/user-profile\n(チームB:開発中)' }, 
        position: { x: 350, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-search', 
        type: 'default',
        data: { label: 'feature/search\n(チームC:開発中)' }, 
        position: { x: 450, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-notification', 
        type: 'default',
        data: { label: 'feature/notification\n(チームD:開発中)' }, 
        position: { x: 550, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-login',
        source: 'develop-1',
        target: 'feature-login',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-profile',
        source: 'develop-1',
        target: 'feature-profile',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-search',
        source: 'develop-1',
        target: 'feature-search',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-notification',
        source: 'develop-1',
        target: 'feature-notification',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      }
    ]
  },
  5: {
    title: "ユーザープロファイル機能の完了とマージ",
    description: "並行開発の成果として、チームBのユーザープロファイル機能の開発とテストが完了したため、feature/user-profileブランチを既にログイン機能を含むdevelopブランチにマージします。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(当初)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-2', 
        type: 'default',
        data: { label: 'develop\n(login機能統合済)' }, 
        position: { x: 350, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-3', 
        type: 'default',
        data: { label: 'develop\n(login+profile機能統合済)' }, 
        position: { x: 450, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system\n(完了)' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-profile', 
        type: 'default',
        data: { label: 'feature/user-profile\n(完了)' }, 
        position: { x: 350, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-search', 
        type: 'default',
        data: { label: 'feature/search\n(開発中)' }, 
        position: { x: 450, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-notification', 
        type: 'default',
        data: { label: 'feature/notification\n(開発中)' }, 
        position: { x: 550, y: 250 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-flow-1',
        source: 'develop-1',
        target: 'develop-2',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'develop-flow-2',
        source: 'develop-2',
        target: 'develop-3',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'develop-feature-login',
        source: 'develop-1',
        target: 'feature-login',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'feature-login-develop',
        source: 'feature-login',
        target: 'develop-2',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-profile',
        source: 'develop-1',
        target: 'feature-profile',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'feature-profile-develop',
        source: 'feature-profile',
        target: 'develop-3',
        animated: true,
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-search',
        source: 'develop-1',
        target: 'feature-search',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-notification',
        source: 'develop-1',
        target: 'feature-notification',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      }
    ]
  },
  6: {
    title: "リリース準備 - releaseブランチの作成",
    description: "並行開発の成果であるログイン機能とユーザープロファイル機能が統合された後、リリース準備を始める段階でdevelopブランチからreleaseブランチを作成します。残りの機能開発は次回リリースに向けて継続します。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-1', 
        type: 'default',
        data: { label: 'develop\n(当初)' }, 
        position: { x: 250, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-3', 
        type: 'default',
        data: { label: 'develop\n(login+profile機能統合済)' }, 
        position: { x: 450, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'release-1', 
        type: 'default',
        data: { label: 'release/1.0.0' }, 
        position: { x: 550, y: 250 },
        style: nodeStyles.release
      },
      { 
        id: 'feature-login', 
        type: 'default',
        data: { label: 'feature/login-system\n(完了)' }, 
        position: { x: 150, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-profile', 
        type: 'default',
        data: { label: 'feature/user-profile\n(完了)' }, 
        position: { x: 350, y: 250 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-search', 
        type: 'default',
        data: { label: 'feature/search\n(次回リリースへ)' }, 
        position: { x: 450, y: 350 },
        style: nodeStyles.feature
      },
      { 
        id: 'feature-notification', 
        type: 'default',
        data: { label: 'feature/notification\n(次回リリースへ)' }, 
        position: { x: 550, y: 350 },
        style: nodeStyles.feature
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-1',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-flow-combined',
        source: 'develop-1',
        target: 'develop-3',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'develop-feature-login',
        source: 'develop-1',
        target: 'feature-login',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-profile',
        source: 'develop-1',
        target: 'feature-profile',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'feature-login-develop',
        source: 'feature-login',
        target: 'develop-3',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'feature-profile-develop',
        source: 'feature-profile',
        target: 'develop-3',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-release',
        source: 'develop-3',
        target: 'release-1',
        animated: true,
        style: edgeStyles.release,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-feature-search',
        source: 'develop-3',
        target: 'feature-search',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      },
      {
        id: 'develop-feature-notification',
        source: 'develop-3',
        target: 'feature-notification',
        style: edgeStyles.feature,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
        animated: true,
      }
    ]
  },
  7: {
    title: "バグ修正 - releaseブランチでの修正",
    description: "リリース準備中に発見されたバグは、releaseブランチ上で修正します。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-3', 
        type: 'default',
        data: { label: 'develop\n(login+profile機能統合済)' }, 
        position: { x: 450, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'release-1', 
        type: 'default',
        data: { label: 'release/1.0.0' }, 
        position: { x: 550, y: 250 },
        style: nodeStyles.release
      },
      { 
        id: 'release-2', 
        type: 'default',
        data: { label: 'release/1.0.0\n(バグ修正後)' }, 
        position: { x: 650, y: 250 },
        style: nodeStyles.release
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-3',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'develop-release',
        source: 'develop-3',
        target: 'release-1',
        style: edgeStyles.release,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'release-flow',
        source: 'release-1',
        target: 'release-2',
        style: edgeStyles.release,
        animated: true,
        type: 'smoothstep',
      }
    ]
  },
  8: {
    title: "リリース完了 - mainとdevelopへのマージ",
    description: "リリース準備が完了したら、releaseブランチをmainとdevelopの両方にマージします。",
    nodes: [
      { 
        id: 'main-1', 
        type: 'default',
        data: { label: 'main/master\n(本番B面)' }, 
        position: { x: 250, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'main-2', 
        type: 'default',
        data: { label: 'main/master\n(リリース後)' }, 
        position: { x: 550, y: 50 },
        style: nodeStyles.main
      },
      {
        id: 'tag-v1',
        type: 'default',
        data: { label: 'v1.0.0' },
        position: { x: 580, y: 20 },
        style: nodeStyles.tag
      },
      { 
        id: 'develop-3', 
        type: 'default',
        data: { label: 'develop' }, 
        position: { x: 450, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-4', 
        type: 'default',
        data: { label: 'develop\n(マージ後)' }, 
        position: { x: 650, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'release-2', 
        type: 'default',
        data: { label: 'release/1.0.0' }, 
        position: { x: 650, y: 250 },
        style: nodeStyles.release
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-1',
        target: 'develop-3',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'main-flow',
        source: 'main-1',
        target: 'main-2',
        style: edgeStyles.main,
        type: 'smoothstep',
      },
      {
        id: 'develop-flow',
        source: 'develop-3',
        target: 'develop-4',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'release-main',
        source: 'release-2',
        target: 'main-2',
        animated: true,
        style: edgeStyles.release,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'release-develop',
        source: 'release-2',
        target: 'develop-4',
        animated: true,
        style: edgeStyles.release,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  9: {
    title: "本番環境のバグ修正 - hotfixブランチ",
    description: "本番環境で重大なバグが発見された場合、mainブランチからhotfixブランチを作成して緊急修正します。",
    nodes: [
      { 
        id: 'main-2', 
        type: 'default',
        data: { label: 'main/master\n(リリース済)' }, 
        position: { x: 550, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'develop-4', 
        type: 'default',
        data: { label: 'develop' }, 
        position: { x: 650, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'hotfix-1', 
        type: 'default',
        data: { label: 'hotfix/1.0.1' }, 
        position: { x: 750, y: 250 },
        style: nodeStyles.hotfix
      }
    ],
    edges: [
      {
        id: 'main-develop',
        source: 'main-2',
        target: 'develop-4',
        style: edgeStyles.develop,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'main-hotfix',
        source: 'main-2',
        target: 'hotfix-1',
        animated: true,
        style: edgeStyles.hotfix,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
  10: {
    title: "hotfixのマージ - mainとdevelopへ",
    description: "hotfixが完了したら、mainとdevelopの両方にマージして、新しいタグを付けます。",
    nodes: [
      { 
        id: 'main-2', 
        type: 'default',
        data: { label: 'main/master' }, 
        position: { x: 550, y: 50 },
        style: nodeStyles.main
      },
      { 
        id: 'main-3', 
        type: 'default',
        data: { label: 'main/master\n(hotfix後)' }, 
        position: { x: 750, y: 50 },
        style: nodeStyles.main
      },
      {
        id: 'tag-v2',
        type: 'default',
        data: { label: 'v1.0.1' },
        position: { x: 780, y: 20 },
        style: nodeStyles.tag
      },
      { 
        id: 'develop-4', 
        type: 'default',
        data: { label: 'develop' }, 
        position: { x: 650, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'develop-5', 
        type: 'default',
        data: { label: 'develop\n(hotfix後)' }, 
        position: { x: 850, y: 150 },
        style: nodeStyles.develop
      },
      { 
        id: 'hotfix-1', 
        type: 'default',
        data: { label: 'hotfix/1.0.1' }, 
        position: { x: 750, y: 250 },
        style: nodeStyles.hotfix
      }
    ],
    edges: [
      {
        id: 'main-flow',
        source: 'main-2',
        target: 'main-3',
        style: edgeStyles.main,
        type: 'smoothstep',
      },
      {
        id: 'develop-flow',
        source: 'develop-4',
        target: 'develop-5',
        style: edgeStyles.develop,
        type: 'smoothstep',
      },
      {
        id: 'hotfix-main',
        source: 'hotfix-1',
        target: 'main-3',
        animated: true,
        style: edgeStyles.hotfix,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      },
      {
        id: 'hotfix-develop',
        source: 'hotfix-1',
        target: 'develop-5',
        animated: true,
        style: edgeStyles.hotfix,
        type: 'smoothstep',
        markerEnd: { type: 'arrowclosed' },
      }
    ]
  },
};

const ReactFlowGitGraph = ({ step = 1, animationEnabled = true }) => {
  // Support for fractional steps like 3.5
  const availableSteps = Object.keys(gitFlowStepsData).map(Number).sort((a, b) => a - b);
  const maxStep = Math.max(...availableSteps);
  const minStep = Math.min(...availableSteps);
  
  // Find the closest step in our available steps
  let currentStep = step;
  
  // If the exact step doesn't exist, find the closest match
  if (!availableSteps.includes(step)) {
    // First, clamp the step between min and max values
    currentStep = Math.min(Math.max(minStep, step), maxStep);
    
    // If it's still not an exact match (like 3.5), find the closest available step
    if (!availableSteps.includes(currentStep)) {
      // For steps like 3.5, we want to find the exact match or the closest one
      const closestStep = availableSteps.reduce((prev, curr) => 
        Math.abs(curr - currentStep) < Math.abs(prev - currentStep) ? curr : prev
      );
      currentStep = closestStep;
    }
  }
  
  const stepData = gitFlowStepsData[currentStep] || gitFlowStepsData[1];
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // アニメーションの有無に応じてエッジを更新
  useEffect(() => {
    const updatedEdges = stepData.edges.map(edge => ({
      ...edge,
      animated: animationEnabled ? edge.animated : false
    }));
    setEdges(updatedEdges);
    setNodes(stepData.nodes);
  }, [stepData, animationEnabled, setEdges, setNodes]);

  const onConnect = useCallback((params) => 
    setEdges((eds) => addEdge({ ...params, type: 'smoothstep' }, eds)),
  [setEdges]);

  return (
    <div style={{ height: 400, width: '100%', border: '1px solid #ddd', borderRadius: '8px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap 
          nodeStrokeColor={(n) => {
            if (n.style?.background) return n.style.background;
            return '#eee';
          }}
          nodeColor={(n) => {
            if (n.style?.background) return n.style.background;
            return '#fff';
          }}
          nodeBorderRadius={2}
        />
        <Background color="#f8f8f8" gap={16} />
        <Panel position="top-center" style={{ textAlign: 'center', padding: '10px' }}>
          <h3 style={{ margin: 0 }}>{stepData.title}</h3>
          <p style={{ marginBottom: 0 }}>{stepData.description}</p>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default ReactFlowGitGraph;