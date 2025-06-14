// Mermaid.js によるGit Flow可視化プロトタイプ

import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';

// Mermaid初期化オプション
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  },
  securityLevel: 'loose', // インラインスタイル適用のために必要
});

const MermaidGitFlow = ({ step }) => {
  const [svg, setSvg] = useState('');
  const [loading, setLoading] = useState(true);

  const gitFlowDiagrams = {
    1: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
    `,
    2: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
    `,
    3: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
    `,
    4: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
    `,
    5: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
    `,
    6: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
        branch release/1.0.0
        commit id: "prepare v1.0.0"
    `,
    7: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
        branch release/1.0.0
        commit id: "prepare v1.0.0"
        commit id: "fix login bug"
    `,
    8: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
        branch release/1.0.0
        commit id: "prepare v1.0.0"
        commit id: "fix login bug"
        checkout main
        merge release/1.0.0 tag: "v1.0.0"
        checkout develop
        merge release/1.0.0
    `,
    9: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
        branch release/1.0.0
        commit id: "prepare v1.0.0"
        commit id: "fix login bug"
        checkout main
        merge release/1.0.0 tag: "v1.0.0"
        checkout develop
        merge release/1.0.0
        checkout main
        branch hotfix/1.0.1
        commit id: "critical fix"
    `,
    10: `
      gitGraph LR:
        commit id: "initial"
        branch develop
        commit id: "develop created"
        branch feature/login
        commit id: "login feature"
        checkout develop
        merge feature/login
        commit id: "feature merged"
        branch feature/profile
        commit id: "profile feature"
        checkout develop
        merge feature/profile
        commit id: "profile feature merged"
        branch release/1.0.0
        commit id: "prepare v1.0.0"
        commit id: "fix login bug"
        checkout main
        merge release/1.0.0 tag: "v1.0.0"
        checkout develop
        merge release/1.0.0
        checkout main
        branch hotfix/1.0.1
        commit id: "critical fix"
        checkout main
        merge hotfix/1.0.1 tag: "v1.0.1"
        checkout develop
        merge hotfix/1.0.1
    `
  };

  useEffect(() => {
    const renderDiagram = async () => {
      setLoading(true);
      if (gitFlowDiagrams[step]) {
        try {
          const { svg } = await mermaid.render('gitflow-diagram', gitFlowDiagrams[step]);
          setSvg(svg);
        } catch (error) {
          console.error("Mermaid rendering failed:", error);
        }
      }
      setLoading(false);
    };

    renderDiagram();
  }, [step]);

  return (
    <div className="mermaid-diagram">
      {loading ? (
        <div>Loading diagram...</div>
      ) : (
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      )}
      <style jsx>{`
        .mermaid-diagram {
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

export default MermaidGitFlow;