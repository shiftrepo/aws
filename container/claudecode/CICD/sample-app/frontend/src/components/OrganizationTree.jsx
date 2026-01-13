import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/api';
import TreeNode from './TreeNode';
import '../styles/OrganizationTree.css';

/**
 * OrganizationTree Component
 * 組織の階層構造を表示
 */
const OrganizationTree = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tree, setTree] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOrganizationTree = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get(`/organizations/${id}/tree`);
      setTree(response.data);
      setError(null);
    } catch (err) {
      console.error('組織階層構造の取得に失敗しました:', err);
      setError('組織階層構造の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchOrganizationTree();
  }, [fetchOrganizationTree]);

  const handleBack = () => {
    navigate('/organizations');
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button onClick={handleBack} className="btn btn-secondary">
          戻る
        </button>
      </div>
    );
  }

  if (!tree) {
    return <div className="error-message">組織データが見つかりません</div>;
  }

  return (
    <div className="organization-tree-container">
      <div className="tree-header">
        <h2>{tree.name} - 組織構成図</h2>
        <button onClick={handleBack} className="btn btn-secondary">
          戻る
        </button>
      </div>

      {tree.description && (
        <p className="tree-description">{tree.description}</p>
      )}

      <div className="tree-content">
        <h3>部門階層構造</h3>
        {tree.departments && tree.departments.length > 0 ? (
          <div className="tree-view">
            {tree.departments.map((dept) => (
              <TreeNode key={dept.id} node={dept} level={0} />
            ))}
          </div>
        ) : (
          <p className="no-data">この組織には部門が登録されていません</p>
        )}
      </div>

      <div className="tree-footer">
        <p className="tree-info">
          作成日時: {new Date(tree.createdAt).toLocaleString('ja-JP')}
          {tree.updatedAt && tree.updatedAt !== tree.createdAt && (
            <> | 更新日時: {new Date(tree.updatedAt).toLocaleString('ja-JP')}</>
          )}
        </p>
      </div>
    </div>
  );
};

export default OrganizationTree;
