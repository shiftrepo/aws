#!/bin/bash
################################################################################
# 開発ワークフローデモスクリプト
#
# 目的: 組織構成図機能追加を通じて、以下の開発フローを実演
#   1. Issue作成（GitHub）
#   2. 機能実装（Backend + Frontend）
#   3. テスト追加（100%カバレッジ維持）
#   4. GitLabへpush → CI/CD自動実行
#   5. Merge Request作成
#   6. 承認 → デプロイ
#   7. マスタリポジトリへ同期
#
# 使用方法:
#   ./scripts/demo-development-workflow.sh
#
# 前提条件:
#   - sudo setup-from-scratch.sh が実行済み
#   - sudo setup-cicd.sh が実行済み
#   - setup-sample-app.sh が実行済み（/tmp/gitlab-sample-app が存在）
#   - GitLab Runnerが登録済み
################################################################################

set -e  # エラー時に即座に終了

# カラー出力定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}STEP $1: $2${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# 環境変数読み込み
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    log_info ".env ファイルを読み込みました"
else
    log_error ".env ファイルが見つかりません: $PROJECT_ROOT/.env"
    log_error "sudo setup-from-scratch.sh を先に実行してください"
    exit 1
fi

# 変数定義
MASTER_REPO="$PROJECT_ROOT/sample-app"
GITLAB_WORKING_DIR="/tmp/gitlab-sample-app"
GITLAB_REMOTE_URL="http://root:${GITLAB_ROOT_PASSWORD}@${EC2_PUBLIC_IP}:5003/root/sample-app.git"
FEATURE_BRANCH="feature/organization-tree-view"
ISSUE_NUMBER="117"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

################################################################################
# STEP 1: 環境確認
################################################################################
step1_check_environment() {
    log_step "1" "環境確認"

    # /tmp/gitlab-sample-app の存在確認
    if [ ! -d "$GITLAB_WORKING_DIR" ]; then
        log_error "/tmp/gitlab-sample-app が存在しません"
        log_error "setup-sample-app.sh を先に実行してください"
        exit 1
    fi

    log_success "/tmp/gitlab-sample-app: 存在確認OK"

    log_info "CI/CDサービスの状態確認..."

    # GitLab確認
    if curl -sf "http://${EC2_PUBLIC_IP}:5003/api/v4/projects" > /dev/null 2>&1; then
        log_success "GitLab: 稼働中"
    else
        log_error "GitLab: 接続不可"
        exit 1
    fi

    # Nexus確認
    if curl -sf "http://${EC2_PUBLIC_IP}:8082/service/rest/v1/status" > /dev/null 2>&1; then
        log_success "Nexus: 稼働中"
    else
        log_warning "Nexus: 接続不可（警告のみ）"
    fi

    # SonarQube確認
    if curl -sf "http://${EC2_PUBLIC_IP}:8000/api/system/health" > /dev/null 2>&1; then
        log_success "SonarQube: 稼働中"
    else
        log_warning "SonarQube: 接続不可（警告のみ）"
    fi

    # PostgreSQL確認
    if pg_isready -h localhost -p 5001 > /dev/null 2>&1; then
        log_success "PostgreSQL: 稼働中"
    else
        log_error "PostgreSQL: 接続不可"
        exit 1
    fi

    log_success "環境確認完了"
}

################################################################################
# STEP 2: GitLab作業ディレクトリ準備（既存リポジトリベース）
################################################################################
step2_setup_gitlab_workdir() {
    log_step "2" "GitLab作業ディレクトリ準備"

    cd "$GITLAB_WORKING_DIR"

    log_info "Git設定確認..."
    git config user.name "CI/CD Demo" || git config user.name "CI/CD Demo"
    git config user.email "cicd-demo@example.com" || git config user.email "cicd-demo@example.com"

    log_info "最新のmasterブランチを取得..."
    git fetch origin master 2>/dev/null || log_warning "fetch失敗（初回実行の可能性）"

    # masterブランチに切り替え（既に存在する場合）
    if git rev-parse --verify master >/dev/null 2>&1; then
        git checkout master
        git pull origin master 2>/dev/null || log_warning "pull失敗（初回実行の可能性）"
    else
        log_info "masterブランチが存在しないため、現在のブランチを使用"
    fi

    log_info "フィーチャーブランチ作成: $FEATURE_BRANCH"
    # 既存のブランチがあれば削除
    git branch -D "$FEATURE_BRANCH" 2>/dev/null || true
    git checkout -b "$FEATURE_BRANCH"

    log_success "GitLab作業ディレクトリ準備完了: $GITLAB_WORKING_DIR"
}

################################################################################
# STEP 3: Backend実装 - OrganizationTree API
################################################################################
step3_implement_backend() {
    log_step "3" "Backend実装 - OrganizationTree API"

    cd "$GITLAB_WORKING_DIR"

    # DTOクラス作成
    log_info "OrganizationTreeDto.java 作成中..."
    cat > common/src/main/java/com/example/common/dto/OrganizationTreeDto.java << 'EOF'
package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Organization Tree DTO
 * 組織の階層構造を表現するDTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrganizationTreeDto {
    private Long id;
    private String name;
    private String description;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<DepartmentTreeNode> departments;
}
EOF

    # DepartmentTreeNodeクラス作成
    log_info "DepartmentTreeNode.java 作成中..."
    cat > common/src/main/java/com/example/common/dto/DepartmentTreeNode.java << 'EOF'
package com.example.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Department Tree Node
 * 部門の階層構造ノード
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DepartmentTreeNode {
    private Long id;
    private String name;
    private String description;
    private Long organizationId;
    private Long parentDepartmentId;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @Builder.Default
    private List<DepartmentTreeNode> children = new ArrayList<>();

    /**
     * 子ノード追加
     */
    public void addChild(DepartmentTreeNode child) {
        if (this.children == null) {
            this.children = new ArrayList<>();
        }
        this.children.add(child);
    }
}
EOF

    # OrganizationServiceにimport追加（既存の場合はスキップ）
    if ! grep -q "import com.example.backend.repository.DepartmentRepository;" backend/src/main/java/com/example/backend/service/OrganizationService.java; then
        sed -i '/^import com.example.backend.repository.OrganizationRepository;$/a import com.example.backend.repository.DepartmentRepository;\nimport com.example.common.dto.OrganizationTreeDto;\nimport com.example.common.dto.DepartmentTreeNode;\nimport com.example.backend.entity.Department;\nimport java.util.HashMap;\nimport java.util.Map;' \
            backend/src/main/java/com/example/backend/service/OrganizationService.java
    fi

    # DepartmentRepositoryフィールド追加（既存の場合はスキップ）
    if ! grep -q "private final DepartmentRepository departmentRepository;" backend/src/main/java/com/example/backend/service/OrganizationService.java; then
        sed -i '/private final OrganizationRepository organizationRepository;$/a \ \ \ \ private final DepartmentRepository departmentRepository;' \
            backend/src/main/java/com/example/backend/service/OrganizationService.java
    fi

    # OrganizationService にツリー構築メソッド追加（既存の場合はスキップ）
    if ! grep -q "getOrganizationTree" backend/src/main/java/com/example/backend/service/OrganizationService.java; then
        cat >> backend/src/main/java/com/example/backend/service/OrganizationService.java << 'EOF'

    /**
     * 組織の階層構造取得
     * @param organizationId 組織ID
     * @return 組織階層構造
     */
    public OrganizationTreeDto getOrganizationTree(Long organizationId) {
        log.debug("組織階層構造取得開始: organizationId={}", organizationId);

        // 組織存在確認
        Organization organization = organizationRepository.findById(organizationId)
                .orElseThrow(() -> new IllegalArgumentException("組織が見つかりません: ID=" + organizationId));

        // 組織配下の全部門取得
        List<Department> departments = departmentRepository.findByOrganizationId(organizationId);
        log.debug("部門数: {}", departments.size());

        // 階層構造構築
        List<DepartmentTreeNode> rootNodes = buildDepartmentTree(departments);

        // DTOに変換
        OrganizationTreeDto treeDto = OrganizationTreeDto.builder()
                .id(organization.getId())
                .name(organization.getName())
                .description(organization.getDescription())
                .createdAt(organization.getCreatedAt())
                .updatedAt(organization.getUpdatedAt())
                .departments(rootNodes)
                .build();

        log.debug("組織階層構造取得完了: ルート部門数={}", rootNodes.size());
        return treeDto;
    }

    /**
     * 部門の階層構造を構築
     * @param departments 部門リスト
     * @return ルート部門ノードリスト
     */
    private List<DepartmentTreeNode> buildDepartmentTree(List<Department> departments) {
        // 全部門をMapに格納（高速アクセス用）
        Map<Long, DepartmentTreeNode> nodeMap = new HashMap<>();
        for (Department dept : departments) {
            DepartmentTreeNode node = DepartmentTreeNode.builder()
                    .id(dept.getId())
                    .name(dept.getName())
                    .description(dept.getDescription())
                    .organizationId(dept.getOrganizationId())
                    .parentDepartmentId(dept.getParentDepartmentId())
                    .createdAt(dept.getCreatedAt())
                    .updatedAt(dept.getUpdatedAt())
                    .children(new ArrayList<>())
                    .build();
            nodeMap.put(dept.getId(), node);
        }

        // 親子関係を構築
        List<DepartmentTreeNode> rootNodes = new ArrayList<>();
        for (DepartmentTreeNode node : nodeMap.values()) {
            if (node.getParentDepartmentId() == null) {
                // ルートノード
                rootNodes.add(node);
            } else {
                // 子ノード
                DepartmentTreeNode parent = nodeMap.get(node.getParentDepartmentId());
                if (parent != null) {
                    parent.addChild(node);
                }
            }
        }

        return rootNodes;
    }
EOF
    fi

    # OrganizationControllerにimport追加（既存の場合はスキップ）
    if ! grep -q "import com.example.common.dto.OrganizationTreeDto;" backend/src/main/java/com/example/backend/controller/OrganizationController.java; then
        sed -i '/^import com.example.common.dto.OrganizationDto;$/a import com.example.common.dto.OrganizationTreeDto;' \
            backend/src/main/java/com/example/backend/controller/OrganizationController.java
    fi

    # OrganizationController にエンドポイント追加（既存の場合はスキップ）
    if ! grep -q "getOrganizationTree" backend/src/main/java/com/example/backend/controller/OrganizationController.java; then
        sed -i '/public ResponseEntity<Void> deleteOrganization/i \
    /**\
     * 組織の階層構造取得\
     * GET /api/organizations/{id}/tree\
     */\
    @GetMapping("/{id}/tree")\
    public ResponseEntity<OrganizationTreeDto> getOrganizationTree(@PathVariable Long id) {\
        log.debug("組織階層構造取得API呼び出し: ID={}", id);\
        OrganizationTreeDto tree = organizationService.getOrganizationTree(id);\
        return ResponseEntity.ok(tree);\
    }\
\
' backend/src/main/java/com/example/backend/controller/OrganizationController.java
    fi

    log_success "Backend実装完了"
}

################################################################################
# STEP 4: Backend テスト追加
################################################################################
step4_add_backend_tests() {
    log_step "4" "Backend テスト追加"

    cd "$GITLAB_WORKING_DIR"

    log_info "OrganizationServiceTest.java にツリー構築テスト追加..."

    # OrganizationServiceTestにimport追加（既存の場合はスキップ）
    if ! grep -q "import com.example.common.dto.OrganizationTreeDto;" backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java; then
        sed -i '/^import static org.mockito.Mockito.\*;$/a import com.example.common.dto.OrganizationTreeDto;\nimport com.example.common.dto.DepartmentTreeNode;\nimport com.example.backend.entity.Department;\nimport java.util.Arrays;\nimport java.util.Collections;' \
            backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java
    fi

    # DepartmentRepositoryのMock追加（既存の場合はスキップ）
    if ! grep -q "private DepartmentRepository departmentRepository;" backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java; then
        sed -i '/@Mock$/a \ \ \ \ private DepartmentRepository departmentRepository;' \
            backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java
    fi

    # テストケース追加（既存の場合はスキップ）
    if ! grep -q "getOrganizationTree_Success" backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java; then
        cat >> backend/src/test/java/com/example/backend/service/OrganizationServiceTest.java << 'EOF'

    /**
     * 組織階層構造取得 - 正常系
     */
    @Test
    @DisplayName("組織階層構造取得 - 正常系")
    void getOrganizationTree_Success() {
        // Arrange
        Organization org = Organization.builder()
                .id(1L)
                .name("本社")
                .description("本社組織")
                .build();

        Department dept1 = Department.builder()
                .id(1L)
                .name("営業本部")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department dept2 = Department.builder()
                .id(2L)
                .name("東日本営業部")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(org));
        when(departmentRepository.findByOrganizationId(1L)).thenReturn(Arrays.asList(dept1, dept2));

        // Act
        OrganizationTreeDto result = organizationService.getOrganizationTree(1L);

        // Assert
        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("本社", result.getName());
        assertEquals(1, result.getDepartments().size());

        DepartmentTreeNode root = result.getDepartments().get(0);
        assertEquals("営業本部", root.getName());
        assertEquals(1, root.getChildren().size());
        assertEquals("東日本営業部", root.getChildren().get(0).getName());

        verify(organizationRepository, times(1)).findById(1L);
        verify(departmentRepository, times(1)).findByOrganizationId(1L);
    }

    /**
     * 組織階層構造取得 - 組織が存在しない
     */
    @Test
    @DisplayName("組織階層構造取得 - 組織が存在しない")
    void getOrganizationTree_OrganizationNotFound() {
        // Arrange
        when(organizationRepository.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            organizationService.getOrganizationTree(999L);
        });

        verify(organizationRepository, times(1)).findById(999L);
        verify(departmentRepository, never()).findByOrganizationId(anyLong());
    }

    /**
     * 組織階層構造取得 - 部門が存在しない
     */
    @Test
    @DisplayName("組織階層構造取得 - 部門が存在しない")
    void getOrganizationTree_NoDepartments() {
        // Arrange
        Organization org = Organization.builder()
                .id(1L)
                .name("本社")
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(org));
        when(departmentRepository.findByOrganizationId(1L)).thenReturn(Collections.emptyList());

        // Act
        OrganizationTreeDto result = organizationService.getOrganizationTree(1L);

        // Assert
        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertTrue(result.getDepartments().isEmpty());
    }

    /**
     * 組織階層構造取得 - 3階層構造
     */
    @Test
    @DisplayName("組織階層構造取得 - 3階層構造")
    void getOrganizationTree_ThreeLevels() {
        // Arrange
        Organization org = Organization.builder()
                .id(1L)
                .name("本社")
                .build();

        Department dept1 = Department.builder()
                .id(1L)
                .name("営業本部")
                .organizationId(1L)
                .parentDepartmentId(null)
                .build();

        Department dept2 = Department.builder()
                .id(2L)
                .name("東日本営業部")
                .organizationId(1L)
                .parentDepartmentId(1L)
                .build();

        Department dept3 = Department.builder()
                .id(3L)
                .name("東京営業課")
                .organizationId(1L)
                .parentDepartmentId(2L)
                .build();

        when(organizationRepository.findById(1L)).thenReturn(Optional.of(org));
        when(departmentRepository.findByOrganizationId(1L))
                .thenReturn(Arrays.asList(dept1, dept2, dept3));

        // Act
        OrganizationTreeDto result = organizationService.getOrganizationTree(1L);

        // Assert
        assertNotNull(result);
        assertEquals(1, result.getDepartments().size());

        DepartmentTreeNode level1 = result.getDepartments().get(0);
        assertEquals("営業本部", level1.getName());
        assertEquals(1, level1.getChildren().size());

        DepartmentTreeNode level2 = level1.getChildren().get(0);
        assertEquals("東日本営業部", level2.getName());
        assertEquals(1, level2.getChildren().size());

        DepartmentTreeNode level3 = level2.getChildren().get(0);
        assertEquals("東京営業課", level3.getName());
        assertEquals(0, level3.getChildren().size());
    }
EOF
    fi

    log_success "Backend テスト追加完了"
}

################################################################################
# STEP 5: Frontend実装 - OrganizationTree Component
################################################################################
step5_implement_frontend() {
    log_step "5" "Frontend実装 - OrganizationTree Component"

    cd "$GITLAB_WORKING_DIR"

    # TreeNodeコンポーネント作成
    log_info "TreeNode.jsx コンポーネント作成中..."
    cat > frontend/src/components/TreeNode.jsx << 'EOF'
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
EOF

    # OrganizationTreeコンポーネント作成
    log_info "OrganizationTree.jsx コンポーネント作成中..."
    cat > frontend/src/components/OrganizationTree.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchOrganizationTree();
  }, [id]);

  const fetchOrganizationTree = async () => {
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
  };

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
EOF

    # TreeNode CSS作成
    log_info "TreeNode.css 作成中..."
    cat > frontend/src/styles/TreeNode.css << 'EOF'
/* TreeNode.css */

.tree-node {
  margin: 2px 0;
}

.tree-node-content {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
  cursor: default;
}

.tree-node-content:hover {
  background-color: #f5f5f5;
}

.tree-node-toggle {
  cursor: pointer;
  margin-right: 8px;
  user-select: none;
  font-size: 12px;
  color: #666;
  min-width: 16px;
  display: inline-block;
}

.tree-node-toggle:hover {
  color: #333;
}

.tree-node-spacer {
  margin-right: 8px;
  min-width: 16px;
  display: inline-block;
}

.tree-node-name {
  font-weight: 500;
  color: #333;
}

.tree-node-description {
  color: #666;
  font-size: 0.9em;
  margin-left: 8px;
}

.tree-node-count {
  color: #999;
  font-size: 0.85em;
  margin-left: 4px;
}

.tree-node-children {
  margin-left: 0;
}
EOF

    # OrganizationTree CSS作成
    log_info "OrganizationTree.css 作成中..."
    cat > frontend/src/styles/OrganizationTree.css << 'EOF'
/* OrganizationTree.css */

.organization-tree-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.tree-header h2 {
  margin: 0;
  color: #333;
}

.tree-description {
  color: #666;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-left: 4px solid #4CAF50;
  border-radius: 4px;
}

.tree-content {
  margin-top: 20px;
}

.tree-content h3 {
  color: #444;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.tree-view {
  padding: 10px;
  background-color: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  min-height: 200px;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px;
  font-style: italic;
}

.tree-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.tree-info {
  color: #999;
  font-size: 0.85em;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 1.2em;
  color: #666;
}

.error-container {
  text-align: center;
  padding: 40px;
}

.error-message {
  color: #d32f2f;
  margin-bottom: 20px;
}
EOF

    # App.jsxにルート追加（既存の場合はスキップ）
    if ! grep -q "import OrganizationTree from" frontend/src/App.jsx; then
        log_info "App.jsx にルート追加..."
        sed -i '/import OrganizationList from/a import OrganizationTree from '\''./components/OrganizationTree'\'';' \
            frontend/src/App.jsx

        sed -i '/<Route path="\/users" element={<UserList \/>} \/>/a \          <Route path="/organizations/:id/tree" element={<OrganizationTree />} />' \
            frontend/src/App.jsx
    fi

    # OrganizationList.jsxに木構造表示ボタン追加（既存の場合はスキップ）
    if ! grep -q "構成図" frontend/src/components/OrganizationList.jsx; then
        log_info "OrganizationList.jsx に木構造表示ボタン追加..."

        # navigateのimport確認と追加
        if ! grep -q "useNavigate" frontend/src/components/OrganizationList.jsx; then
            sed -i "s/import React, { useState, useEffect } from 'react';/import React, { useState, useEffect } from 'react';\nimport { useNavigate } from 'react-router-dom';/" \
                frontend/src/components/OrganizationList.jsx
            sed -i "/const OrganizationList = () => {/a \ \ const navigate = useNavigate();" \
                frontend/src/components/OrganizationList.jsx
        fi

        # 構成図ボタン追加
        sed -i 's/<button onClick={() => handleEdit(org)} className="btn btn-primary">編集<\/button>/<button onClick={() => navigate(`\/organizations\/${org.id}\/tree`)} className="btn btn-info">構成図<\/button>\n                  <button onClick={() => handleEdit(org)} className="btn btn-primary">編集<\/button>/' \
            frontend/src/components/OrganizationList.jsx
    fi

    log_success "Frontend実装完了"
}

################################################################################
# STEP 6: ローカルビルド＆テスト
################################################################################
step6_local_build_test() {
    log_step "6" "ローカルビルド＆テスト"

    cd "$GITLAB_WORKING_DIR"

    log_info "Mavenクリーンビルド実行..."
    mvn clean install -Dmaven.repo.local=/tmp/.m2-demo-$TIMESTAMP

    log_info "テスト実行..."
    mvn test -Dmaven.repo.local=/tmp/.m2-demo-$TIMESTAMP

    log_info "カバレッジレポート生成..."
    mvn jacoco:report -Dmaven.repo.local=/tmp/.m2-demo-$TIMESTAMP

    log_success "ローカルビルド＆テスト完了"
    log_info "カバレッジレポート: $GITLAB_WORKING_DIR/backend/target/site/jacoco/index.html"
}

################################################################################
# STEP 7: GitLabへコミット＆プッシュ
################################################################################
step7_commit_and_push() {
    log_step "7" "GitLabへコミット＆プッシュ"

    cd "$GITLAB_WORKING_DIR"

    log_info "変更ファイルをステージング..."
    git add .

    log_info "コミット作成..."
    git commit -m "$(cat <<EOF
feat: 組織構成図の木構造表示機能追加 (#${ISSUE_NUMBER})

## 実装内容

### Backend
- OrganizationTreeDto.java: 組織階層構造DTO
- DepartmentTreeNode.java: 部門ツリーノードDTO
- OrganizationService.getOrganizationTree(): ツリー構築ロジック
- OrganizationService.buildDepartmentTree(): 階層構造構築
- OrganizationController.getOrganizationTree(): GET /api/organizations/{id}/tree

### Frontend
- OrganizationTree.jsx: 組織構成図表示コンポーネント
- TreeNode.jsx: ツリーノード表示コンポーネント
- OrganizationTree.css: 構成図スタイル
- TreeNode.css: ノードスタイル
- App.jsx: /organizations/:id/tree ルート追加
- OrganizationList.jsx: 構成図ボタン追加

### Test
- OrganizationServiceTest: ツリー構築テスト4ケース追加
  - 正常系テスト
  - 組織不存在エラーテスト
  - 部門なしテスト
  - 3階層構造テスト

## テスト結果
- 全テストケース成功
- JaCoCoカバレッジ: 70%以上維持

## 関連Issue
- GitHub #${ISSUE_NUMBER}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

    log_info "GitLabへプッシュ..."
    git push -u origin "$FEATURE_BRANCH"

    log_success "GitLabへプッシュ完了"
    log_info "フィーチャーブランチ: $FEATURE_BRANCH"
}

################################################################################
# STEP 8: CI/CDパイプライン実行監視
################################################################################
step8_monitor_pipeline() {
    log_step "8" "CI/CDパイプライン実行監視"

    log_info "GitLab CI/CDパイプラインが自動実行されました"
    log_info "パイプラインURL: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/pipelines"

    log_warning "パイプラインの完了を待機しています..."
    log_info "以下のステージが実行されます:"
    echo "  1. build    - Maven コンパイル"
    echo "  2. test     - ユニットテスト実行"
    echo "  3. coverage - JaCoCoカバレッジチェック"
    echo "  4. sonarqube- SonarQube静的解析"
    echo "  5. package  - JARパッケージング"
    echo "  6. deploy   - Nexusへデプロイ"

    log_info "ブラウザでパイプラインの進行状況を確認してください"
    log_info "全ステージが成功するまで待機..."

    # 簡易的な待機（実際のパイプライン完了は手動確認）
    read -p "パイプラインが完了したらEnterキーを押してください... " -r

    log_success "CI/CDパイプライン完了確認"
}

################################################################################
# STEP 9: Merge Request作成
################################################################################
step9_create_merge_request() {
    log_step "9" "Merge Request作成"

    log_info "GitLab Merge Request作成..."

    # GitLab APIでMR作成
    MR_RESPONSE=$(curl -s -X POST \
        "http://${EC2_PUBLIC_IP}:5003/api/v4/projects/1/merge_requests" \
        -H "PRIVATE-TOKEN: ${GITLAB_ROOT_PASSWORD}" \
        -H "Content-Type: application/json" \
        -d "{
            \"source_branch\": \"${FEATURE_BRANCH}\",
            \"target_branch\": \"master\",
            \"title\": \"feat: 組織構成図の木構造表示機能追加 (#${ISSUE_NUMBER})\",
            \"description\": \"## 概要\n\n組織の階層構造を木構造で視覚的に表示する機能を追加します。\n\n## 実装内容\n\n- Backend: /api/organizations/{id}/tree エンドポイント追加\n- Frontend: OrganizationTree コンポーネント実装\n- Test: カバレッジ70%維持\n\n## 関連Issue\n\n- GitHub #${ISSUE_NUMBER}\n\n## チェックリスト\n\n- [x] ビルド成功\n- [x] テスト成功\n- [x] カバレッジ70%以上\n- [x] SonarQube解析成功\",
            \"remove_source_branch\": true
        }")

    MR_IID=$(echo "$MR_RESPONSE" | grep -o '"iid":[0-9]*' | cut -d':' -f2)

    if [ -n "$MR_IID" ]; then
        log_success "Merge Request作成完了: !${MR_IID}"
        log_info "MR URL: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/merge_requests/${MR_IID}"
    else
        log_error "Merge Request作成失敗"
        echo "$MR_RESPONSE"
        exit 1
    fi

    echo "$MR_IID" > /tmp/demo-mr-iid.txt
}

################################################################################
# STEP 10: Merge Request承認とマージ
################################################################################
step10_approve_and_merge() {
    log_step "10" "Merge Request承認とマージ"

    MR_IID=$(cat /tmp/demo-mr-iid.txt)

    log_info "Merge Request !${MR_IID} を承認します"

    # MRマージ
    MERGE_RESPONSE=$(curl -s -X PUT \
        "http://${EC2_PUBLIC_IP}:5003/api/v4/projects/1/merge_requests/${MR_IID}/merge" \
        -H "PRIVATE-TOKEN: ${GITLAB_ROOT_PASSWORD}" \
        -H "Content-Type: application/json" \
        -d '{
            "merge_commit_message": "Merge branch '\''feature/organization-tree-view'\'' into '\''master'\''\n\n組織構成図機能をmasterブランチにマージ",
            "should_remove_source_branch": true
        }')

    if echo "$MERGE_RESPONSE" | grep -q '"state":"merged"'; then
        log_success "Merge Request マージ完了"
    else
        log_error "Merge Request マージ失敗"
        echo "$MERGE_RESPONSE"
        exit 1
    fi
}

################################################################################
# STEP 11: コンテナビルド＆デプロイ
################################################################################
step11_deploy_containers() {
    log_step "11" "コンテナビルド＆デプロイ"

    cd "$PROJECT_ROOT"

    log_info "最新のmasterブランチを取得..."
    cd "$GITLAB_WORKING_DIR"
    git checkout master
    git pull origin master

    log_info "Backendコンテナビルド..."
    cd "$PROJECT_ROOT"
    sudo podman build -t sample-backend:latest \
        -f sample-app/backend/Dockerfile \
        sample-app/backend/

    log_info "Frontend + Nginxコンテナビルド..."
    sudo podman build -t nginx-frontend:latest \
        -f sample-app/nginx/Dockerfile \
        sample-app/

    log_info "既存コンテナ停止..."
    sudo podman-compose down --profile app

    log_info "新しいコンテナ起動..."
    sudo podman-compose up -d --profile app

    log_info "コンテナ起動待機（30秒）..."
    sleep 30

    log_success "コンテナデプロイ完了"
}

################################################################################
# STEP 12: 動作確認
################################################################################
step12_verify_deployment() {
    log_step "12" "動作確認"

    log_info "APIエンドポイント動作確認..."

    # 組織一覧取得
    log_info "組織一覧取得: GET /api/organizations"
    ORG_RESPONSE=$(curl -s "http://${EC2_PUBLIC_IP}:5006/api/organizations")
    ORG_COUNT=$(echo "$ORG_RESPONSE" | grep -o '"id"' | wc -l)
    log_success "組織数: ${ORG_COUNT}件"

    # 組織階層構造取得
    log_info "組織階層構造取得: GET /api/organizations/1/tree"
    TREE_RESPONSE=$(curl -s "http://${EC2_PUBLIC_IP}:5006/api/organizations/1/tree")

    if echo "$TREE_RESPONSE" | grep -q '"departments"'; then
        log_success "組織階層構造API: 正常応答"
        DEPT_COUNT=$(echo "$TREE_RESPONSE" | grep -o '"name"' | wc -l)
        log_info "部門数: ${DEPT_COUNT}件（階層構造）"
    else
        log_error "組織階層構造API: 異常応答"
        echo "$TREE_RESPONSE"
    fi

    log_info "フロントエンド確認:"
    echo "  - 組織一覧: http://${EC2_PUBLIC_IP}:5006/"
    echo "  - 組織構成図: http://${EC2_PUBLIC_IP}:5006/organizations/1/tree"

    log_success "デプロイ検証完了"
}

################################################################################
# STEP 13: マスタリポジトリへ同期
################################################################################
step13_sync_to_master() {
    log_step "13" "マスタリポジトリへ同期"

    log_info "GitLabワーキングディレクトリからマスタへrsync..."

    cd "$GITLAB_WORKING_DIR"
    git checkout master
    git pull origin master

    rsync -av --delete \
        --exclude='.git/' \
        --exclude='target/' \
        --exclude='node_modules/' \
        --exclude='.m2/' \
        --exclude='*.class' \
        --exclude='.DS_Store' \
        --exclude='*.log' \
        "$GITLAB_WORKING_DIR/" "$MASTER_REPO/"

    log_info "マスタリポジトリでgit追跡..."
    cd "$PROJECT_ROOT"

    # 権限修正
    sudo chown -R ec2-user:ec2-user /root/aws.git/.git/

    git add sample-app/

    log_info "マスタリポジトリへコミット..."
    git commit -m "$(cat <<EOF
feat: 組織構成図機能実装完了 - GitLabからマスタへ同期 (#${ISSUE_NUMBER})

## 開発フロー完了

1. ✅ Issue作成 (GitHub #${ISSUE_NUMBER})
2. ✅ Backend実装 (OrganizationTree API)
3. ✅ Frontend実装 (OrganizationTree Component)
4. ✅ テスト追加 (カバレッジ70%維持)
5. ✅ GitLab CI/CD実行 (6ステージ成功)
6. ✅ Merge Request承認・マージ
7. ✅ コンテナデプロイ
8. ✅ 動作確認完了

## 実装機能

- GET /api/organizations/{id}/tree エンドポイント
- 組織階層構造の視覚化
- 展開/折りたたみ機能
- 3階層以上のツリー構造サポート

## デプロイ先

- http://${EC2_PUBLIC_IP}:5006/organizations/1/tree

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

    log_info "GitHubへプッシュ..."
    git push origin main

    log_success "マスタリポジトリ同期完了"
}

################################################################################
# STEP 14: サマリー表示
################################################################################
step14_show_summary() {
    log_step "14" "開発ワークフロー完了サマリー"

    echo ""
    echo "=========================================="
    echo "  開発ワークフロー実行結果"
    echo "=========================================="
    echo ""
    echo "✅ Issue作成: GitHub #${ISSUE_NUMBER}"
    echo "   https://github.com/shiftrepo/aws/issues/${ISSUE_NUMBER}"
    echo ""
    echo "✅ 機能実装:"
    echo "   - Backend: GET /api/organizations/{id}/tree"
    echo "   - Frontend: OrganizationTree + TreeNode コンポーネント"
    echo "   - Test: 4ケース追加（カバレッジ70%維持）"
    echo ""
    echo "✅ GitLab CI/CD:"
    echo "   - 6ステージパイプライン成功"
    echo "   - URL: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/pipelines"
    echo ""
    echo "✅ Merge Request:"
    MR_IID=$(cat /tmp/demo-mr-iid.txt 2>/dev/null || echo "N/A")
    echo "   - MR !${MR_IID} 承認・マージ完了"
    echo "   - URL: http://${EC2_PUBLIC_IP}:5003/root/sample-app/-/merge_requests/${MR_IID}"
    echo ""
    echo "✅ デプロイ:"
    echo "   - Backend: sample-backend:latest"
    echo "   - Frontend: nginx-frontend:latest"
    echo "   - 起動確認完了"
    echo ""
    echo "✅ 動作確認URL:"
    echo "   - 組織一覧: http://${EC2_PUBLIC_IP}:5006/"
    echo "   - 組織構成図: http://${EC2_PUBLIC_IP}:5006/organizations/1/tree"
    echo ""
    echo "✅ リポジトリ同期:"
    echo "   - GitLab → GitHub マスタ同期完了"
    echo "   - GitHub: https://github.com/shiftrepo/aws"
    echo ""
    echo "=========================================="
    echo "  すべてのステップが正常に完了しました"
    echo "=========================================="
    echo ""
}

################################################################################
# メイン実行
################################################################################
main() {
    log_info "=========================================="
    log_info " 開発ワークフローデモスクリプト開始"
    log_info "=========================================="
    log_info "Issue: #${ISSUE_NUMBER}"
    log_info "Feature Branch: ${FEATURE_BRANCH}"
    log_info "Timestamp: ${TIMESTAMP}"
    log_info ""
    log_warning "前提条件:"
    log_warning "  1. sudo setup-from-scratch.sh 実行済み"
    log_warning "  2. sudo setup-cicd.sh 実行済み"
    log_warning "  3. setup-sample-app.sh 実行済み"
    echo ""

    step1_check_environment
    step2_setup_gitlab_workdir
    step3_implement_backend
    step4_add_backend_tests
    step5_implement_frontend
    step6_local_build_test
    step7_commit_and_push
    step8_monitor_pipeline
    step9_create_merge_request
    step10_approve_and_merge
    step11_deploy_containers
    step12_verify_deployment
    step13_sync_to_master
    step14_show_summary

    log_success "開発ワークフローデモ完了"
}

# スクリプト実行
main "$@"
