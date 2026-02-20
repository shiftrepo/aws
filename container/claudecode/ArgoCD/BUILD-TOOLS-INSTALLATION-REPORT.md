# ビルドツールインストールレポート

**インストール日時**: 2026-02-20T04:57:17Z
**ステータス**: ✅ 完了

---

## インストールされたツール

### Java
- **Version**: OpenJDK 21
- **Path**: /usr/bin/java
- **Status**: Installed

### Maven
- **Version**: 3.9.6
- **Path**: /opt/maven
- **Environment**: /etc/profile.d/maven.sh
- **Status**: Installed

### Node.js
- **Version**: v20.20.0
- **Path**: /usr/bin/node
- **Status**: Installed

### NPM
- **Version**: 10.8.2
- **Path**: /usr/bin/npm
- **Status**: Installed

---

## 環境変数

Maven環境変数は `/etc/profile.d/maven.sh` で設定されています:

```bash
export MAVEN_HOME=/opt/maven
export PATH=$MAVEN_HOME/bin:$PATH
```

新しいシェルセッションで自動的に読み込まれます。
現在のセッションで使用する場合:

```bash
source /etc/profile.d/maven.sh
```

---

## 次のステップ

ビルドツールのインストールが完了しました。
次のコマンドでアプリケーションをビルド・デプロイできます:

```bash
ansible-playbook -i inventory/hosts.yml playbooks/build_and_deploy_artifacts.yml
```

---

**レポート生成**: 2026-02-20T04:57:17Z
