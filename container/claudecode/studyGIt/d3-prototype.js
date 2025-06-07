// D3.js によるGit Flow可視化プロトタイプ

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const D3GitFlowGraph = ({ step }) => {
  const svgRef = useRef();

  // Git Flowの各ステップに応じたデータ定義
  const gitFlowData = {
    1: {
      nodes: [
        { id: 'main-1', label: 'main/master', type: 'main', x: 100, y: 50 },
        { id: 'develop-1', label: 'develop', type: 'develop', x: 250, y: 50 },
      ],
      links: [
        { source: 'main-1', target: 'develop-1', type: 'branch' }
      ]
    },
    2: {
      nodes: [
        { id: 'main-1', label: 'main/master', type: 'main', x: 100, y: 50 },
        { id: 'develop-1', label: 'develop', type: 'develop', x: 250, y: 50 },
        { id: 'feature-1', label: 'feature/login', type: 'feature', x: 400, y: 80 },
      ],
      links: [
        { source: 'main-1', target: 'develop-1', type: 'branch' },
        { source: 'develop-1', target: 'feature-1', type: 'branch' }
      ]
    },
    3: {
      nodes: [
        { id: 'main-1', label: 'main/master', type: 'main', x: 100, y: 50 },
        { id: 'develop-1', label: 'develop', type: 'develop', x: 250, y: 50 },
        { id: 'develop-2', label: 'develop', type: 'develop', x: 400, y: 50 },
        { id: 'feature-1', label: 'feature/login', type: 'feature', x: 325, y: 100 },
      ],
      links: [
        { source: 'main-1', target: 'develop-1', type: 'branch' },
        { source: 'develop-1', target: 'feature-1', type: 'branch' },
        { source: 'feature-1', target: 'develop-2', type: 'merge' },
        { source: 'develop-1', target: 'develop-2', type: 'commit' },
      ]
    },
    // ステップ4〜10のデータも同様に追加
  };

  useEffect(() => {
    if (!svgRef.current) return;

    const currentStep = Math.min(Math.max(1, step), Object.keys(gitFlowData).length);
    const { nodes, links } = gitFlowData[currentStep] || gitFlowData[1];

    // 既存のSVG内容をクリア
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current);
    const width = 800;
    const height = 400;
    const nodeRadius = 15;

    // ブランチタイプに応じた色の設定
    const colors = {
      main: '#e74c3c',
      develop: '#3498db',
      feature: '#2ecc71',
      release: '#f39c12',
      hotfix: '#9b59b6',
      tag: '#f1c40f'
    };

    // リンクタイプに応じた線のスタイル設定
    const linkStyles = {
      commit: { strokeWidth: 2, stroke: '#666', dashArray: 'none', animation: 'none' },
      branch: { strokeWidth: 2, stroke: '#666', dashArray: '5,5', animation: 'dash 20s linear infinite' },
      merge: { strokeWidth: 3, stroke: '#27ae60', dashArray: 'none', animation: 'none' }
    };

    // リンク（矢印）の描画
    const link = svg.append("g")
      .selectAll("path")
      .data(links)
      .enter()
      .append("path")
      .attr("d", d => {
        const sourceNode = nodes.find(node => node.id === d.source);
        const targetNode = nodes.find(node => node.id === d.target);
        return `M${sourceNode.x},${sourceNode.y} L${targetNode.x},${targetNode.y}`;
      })
      .attr("stroke", d => linkStyles[d.type].stroke)
      .attr("stroke-width", d => linkStyles[d.type].strokeWidth)
      .attr("fill", "none")
      .attr("stroke-dasharray", d => linkStyles[d.type].dashArray)
      .attr("marker-end", "url(#arrowhead)");

    // 矢印マーカーの定義
    svg.append("defs").append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 8)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#666");

    // ノードの描画
    const node = svg.append("g")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .attr("transform", d => `translate(${d.x}, ${d.y})`);

    // ノードの円を追加
    node.append("circle")
      .attr("r", nodeRadius)
      .attr("fill", d => colors[d.type])
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);

    // ノードのラベルを追加
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", nodeRadius * 2)
      .text(d => d.label)
      .attr("font-size", "12px")
      .attr("fill", "#333");

    // CSSアニメーションの追加
    const style = document.createElement('style');
    style.textContent = `
      @keyframes dash {
        to {
          stroke-dashoffset: 100;
        }
      }
    `;
    document.head.appendChild(style);

  }, [step]);

  return (
    <div className="git-flow-graph">
      <svg ref={svgRef} width="100%" height="400px" />
      <style jsx>{`
        .git-flow-graph {
          width: 100%;
          overflow-x: auto;
          padding: 20px 0;
          background: #f9f9f9;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
      `}</style>
    </div>
  );
};

export default D3GitFlowGraph;