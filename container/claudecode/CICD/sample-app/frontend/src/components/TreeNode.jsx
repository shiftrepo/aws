import React, { useState } from 'react';
import '../styles/TreeNode.css';

/**
 * TreeNode Component
 * 階層構造の各ノードを表示
 */
const TreeNode = ({ node, level = 0 }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="tree-node">
      <div
        className="tree-node-content"
        style={{ paddingLeft: `${level * 20}px` }}
      >
        {hasChildren && (
          <span className="tree-node-toggle" onClick={toggleExpand}>
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && <span className="tree-node-spacer">　</span>}
        <span className="tree-node-name">{node.name}</span>
        {node.description && (
          <span className="tree-node-description"> - {node.description}</span>
        )}
        {hasChildren && (
          <span className="tree-node-count"> ({node.children.length})</span>
        )}
      </div>
      {hasChildren && isExpanded && (
        <div className="tree-node-children">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;
