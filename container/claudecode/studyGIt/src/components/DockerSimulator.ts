/**
 * DockerSimulator.ts
 * Docker操作のシミュレーションエンジン
 */

// コンテナの状態タイプ
export type ContainerStatus = 'running' | 'exited' | 'created' | 'paused';

// ポートマッピングインターフェース
export interface PortMapping {
  host: string;
  container: string;
}

// ボリュームマッピングインターフェース
export interface VolumeMapping {
  host: string;
  container: string;
}

// コンテナインターフェース
export interface Container {
  id: string;
  name: string;
  image: string;
  status: ContainerStatus;
  ports: PortMapping[];
  volumes: VolumeMapping[];
  networks: string[];
  env?: Record<string, string>;
  command?: string;
  created: string;
}

// イメージインターフェース
export interface DockerImage {
  id: string;
  repository: string;
  tag: string;
  size: string;
  created: string;
}

// Dockerfileコマンドインターフェース
export interface DockerfileCommand {
  instruction: string;
  arguments: string;
  comment?: string;
}

// Dockerfileインターフェース
export interface Dockerfile {
  path: string;
  commands: DockerfileCommand[];
}

// Docker状態インターフェース
export interface DockerState {
  containers: Container[];
  images: string[];
  volumes: string[];
  networks: string[];
}

// 難易度レベル
export enum DifficultyLevel {
  BEGINNER = 1,
  BASIC = 2,
  INTERMEDIATE = 3,
  ADVANCED = 4
}

// コマンド実行結果インターフェース
export interface CommandResult {
  success: boolean;
  message: string;
  data?: any;
}

// Docker Compose サービス定義
export interface DockerComposeService {
  image?: string;
  build?: {
    context: string;
    dockerfile?: string;
  };
  ports?: string[];
  volumes?: string[];
  environment?: Record<string, string> | string[];
  depends_on?: string[];
  networks?: string[];
}

// Docker Compose 設定
export interface DockerComposeConfig {
  version: string;
  services: Record<string, DockerComposeService>;
  networks?: Record<string, any>;
  volumes?: Record<string, any>;
}

/**
 * DockerSimulator クラス
 * Docker コマンドのシミュレーションを行う
 */
export class DockerSimulator {
  private state: DockerState;
  private level: DifficultyLevel;
  private dockerfiles: Record<string, Dockerfile>;
  private composeConfigs: Record<string, DockerComposeConfig>;

  /**
   * コンストラクタ
   * @param initialState 初期Docker状態（オプション）
   * @param level 難易度レベル（デフォルト：初心者）
   */
  constructor(initialState?: DockerState, level: DifficultyLevel = DifficultyLevel.BEGINNER) {
    this.state = initialState || {
      containers: [],
      images: [],
      volumes: [],
      networks: ['bridge', 'host', 'none']
    };
    this.level = level;
    this.dockerfiles = {};
    this.composeConfigs = {};
  }

  /**
   * コマンドの実行
   * @param command 実行するコマンド文字列
   * @returns コマンド実行結果
   */
  executeCommand(command: string): CommandResult {
    // コマンドを解析
    const parts = command.split(' ').filter(part => part.trim() !== '');
    
    // 'docker'で始まるコマンドのみ処理
    if (parts[0] !== 'docker') {
      return {
        success: false,
        message: 'Unknown command. Use docker commands.'
      };
    }

    const subCommand = parts[1];

    // 現在の難易度レベルで利用可能なコマンドかチェック
    if (!this.isCommandAvailable(subCommand)) {
      return {
        success: false,
        message: `Command 'docker ${subCommand}' is not available at your current level. Level up to unlock this command.`
      };
    }

    // 各種dockerコマンドのシミュレーション実行
    switch (subCommand) {
      case 'ps':
        return this.handleDockerPs(parts.slice(2));
      case 'run':
        return this.handleDockerRun(parts.slice(2));
      case 'images':
        return this.handleDockerImages();
      case 'pull':
        return this.handleDockerPull(parts.slice(2));
      case 'stop':
        return this.handleDockerStop(parts.slice(2));
      case 'start':
        return this.handleDockerStart(parts.slice(2));
      case 'rm':
        return this.handleDockerRm(parts.slice(2));
      case 'rmi':
        return this.handleDockerRmi(parts.slice(2));
      case 'build':
        return this.handleDockerBuild(parts.slice(2));
      case 'network':
        return this.handleDockerNetwork(parts.slice(2));
      case 'volume':
        return this.handleDockerVolume(parts.slice(2));
      case 'logs':
        return this.handleDockerLogs(parts.slice(2));
      case 'exec':
        return this.handleDockerExec(parts.slice(2));
      case 'compose':
        return this.handleDockerCompose(parts.slice(2));
      case 'help':
        return this.handleDockerHelp();
      default:
        return {
          success: false,
          message: `Unknown docker command: ${subCommand}`
        };
    }
  }

  /**
   * 特定のコマンドが現在の難易度レベルで利用可能かチェック
   * @param command コマンド名
   * @returns 利用可能な場合 true
   */
  private isCommandAvailable(command: string): boolean {
    // レベルに応じたコマンド制限
    const commandLevels: Record<string, DifficultyLevel> = {
      // BEGINNER レベル (Level 1) - 基本的なコンテナ管理
      'ps': DifficultyLevel.BEGINNER,
      'run': DifficultyLevel.BEGINNER,
      'images': DifficultyLevel.BEGINNER,
      'stop': DifficultyLevel.BEGINNER,
      'start': DifficultyLevel.BEGINNER,
      'help': DifficultyLevel.BEGINNER,

      // BASIC レベル (Level 2) - イメージ管理
      'pull': DifficultyLevel.BASIC,
      'rm': DifficultyLevel.BASIC,
      'rmi': DifficultyLevel.BASIC,
      'logs': DifficultyLevel.BASIC,

      // INTERMEDIATE レベル (Level 3) - ネットワークとボリューム
      'build': DifficultyLevel.INTERMEDIATE,
      'network': DifficultyLevel.INTERMEDIATE,
      'volume': DifficultyLevel.INTERMEDIATE,
      'exec': DifficultyLevel.INTERMEDIATE,

      // ADVANCED レベル (Level 4) - Docker-compose
      'compose': DifficultyLevel.ADVANCED
    };

    // コマンドが存在し、現在のレベル以下である場合に利用可能
    return commandLevels[command] !== undefined && commandLevels[command] <= this.level;
  }

  /**
   * 難易度レベルの変更
   * @param level 新しい難易度レベル
   */
  setDifficultyLevel(level: DifficultyLevel): void {
    this.level = level;
  }

  /**
   * 現在の難易度レベルの取得
   * @returns 現在の難易度レベル
   */
  getDifficultyLevel(): DifficultyLevel {
    return this.level;
  }

  /**
   * 現在のDockerの状態を取得
   * @returns Docker状態オブジェクト
   */
  getState(): DockerState {
    return {...this.state};
  }

  /**
   * Docker状態の更新
   * @param newState 新しいDocker状態
   */
  setState(newState: DockerState): void {
    this.state = {...newState};
  }

  /**
   * Dockerfileの追加
   * @param path Dockerfileのパス
   * @param dockerfile Dockerfileの内容
   */
  addDockerfile(path: string, dockerfile: Dockerfile): void {
    this.dockerfiles[path] = dockerfile;
  }

  /**
   * Docker Compose設定の追加
   * @param path docker-compose.ymlのパス
   * @param config Compose設定
   */
  addComposeConfig(path: string, config: DockerComposeConfig): void {
    this.composeConfigs[path] = config;
  }

  // 以下、各種Dockerコマンドハンドラーのスケルトン実装
  // 実際の実装では、もっと詳細なコマンドオプション解析と処理が必要

  /**
   * 'docker ps'コマンド処理
   */
  private handleDockerPs(args: string[]): CommandResult {
    // オプション解析（-a フラグの検出）
    const showAll = args.includes('-a') || args.includes('--all');
    
    // フィルターするコンテナ
    let containers = this.state.containers;
    if (!showAll) {
      containers = containers.filter(container => container.status === 'running');
    }
    
    return {
      success: true,
      message: this.formatPsOutput(containers),
      data: containers
    };
  }

  /**
   * 'docker run'コマンド処理
   */
  private handleDockerRun(args: string[]): CommandResult {
    // シンプルな実装のため、オプション解析は簡略化
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker run [OPTIONS] IMAGE [COMMAND] [ARG...]'
      };
    }

    // イメージ名の取得（オプションを除去して最初の引数を使用）
    let imageName = '';
    let detached = false;
    let name = '';
    let ports: PortMapping[] = [];
    let volumes: VolumeMapping[] = [];
    let command = '';
    let networks: string[] = ['bridge'];

    // 非常に単純なオプション解析
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '-d' || args[i] === '--detach') {
        detached = true;
      } else if (args[i] === '--name' && i + 1 < args.length) {
        name = args[i + 1];
        i++;
      } else if (args[i] === '-p' && i + 1 < args.length) {
        const portMapping = args[i + 1].split(':');
        if (portMapping.length === 2) {
          ports.push({
            host: portMapping[0],
            container: portMapping[1]
          });
        }
        i++;
      } else if (args[i] === '-v' && i + 1 < args.length) {
        const volumeMapping = args[i + 1].split(':');
        if (volumeMapping.length === 2) {
          volumes.push({
            host: volumeMapping[0],
            container: volumeMapping[1]
          });
        }
        i++;
      } else if (args[i] === '--network' && i + 1 < args.length) {
        networks = [args[i + 1]];
        i++;
      } else if (!imageName) {
        imageName = args[i];
      } else {
        // イメージ名以降はコマンドと解釈
        command = args.slice(i).join(' ');
        break;
      }
    }

    // イメージが存在するかチェック
    if (!this.state.images.includes(imageName)) {
      return {
        success: false,
        message: `Unable to find image '${imageName}' locally`
      };
    }

    // ネットワークが存在するかチェック
    if (!this.state.networks.includes(networks[0])) {
      return {
        success: false,
        message: `Error: No such network: ${networks[0]}`
      };
    }

    // 一意のコンテナIDを生成
    const id = `container-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    
    // 名前が指定されていない場合はランダムな名前を生成
    if (!name) {
      // 形容詞と名詞のランダムな組み合わせ（Docker風）
      const adjectives = ['happy', 'jolly', 'dreamy', 'sad', 'angry', 'pensive', 'focused'];
      const nouns = ['einstein', 'newton', 'tesla', 'bohr', 'feynman', 'curie', 'darwin'];
      
      const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
      const noun = nouns[Math.floor(Math.random() * nouns.length)];
      
      name = `${adjective}_${noun}`;
    }
    
    // 新しいコンテナを作成
    const newContainer: Container = {
      id,
      name,
      image: imageName,
      status: 'running',
      ports,
      volumes,
      networks,
      command,
      created: new Date().toISOString()
    };
    
    // コンテナをステートに追加
    this.state.containers.push(newContainer);
    
    // 開始メッセージの生成
    const message = detached 
      ? `${id.substring(0, 12)}` 
      : `コンテナID: ${id}\n起動成功: ${name}\nステータス: running\nイメージ: ${imageName}${command ? `\nコマンド: ${command}` : ''}`;
    
    return {
      success: true,
      message,
      data: newContainer
    };
  }

  /**
   * 'docker images'コマンド処理
   */
  private handleDockerImages(): CommandResult {
    const message = this.formatImagesOutput();
    
    return {
      success: true,
      message,
      data: this.state.images
    };
  }

  /**
   * 'docker pull'コマンド処理
   */
  private handleDockerPull(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker pull [OPTIONS] NAME[:TAG|@DIGEST]'
      };
    }

    const image = args[0];
    
    // イメージが既に存在する場合
    if (this.state.images.includes(image)) {
      return {
        success: true,
        message: `Using cache\n${image}: Already exists`
      };
    }
    
    // 新しいイメージを追加
    this.state.images.push(image);
    
    return {
      success: true,
      message: `Pulling from ${image}\nStatus: Downloaded newer image for ${image}`
    };
  }

  /**
   * 'docker stop'コマンド処理
   */
  private handleDockerStop(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker stop [OPTIONS] CONTAINER [CONTAINER...]'
      };
    }

    const containerId = args[0];
    const containerIndex = this.state.containers.findIndex(
      container => container.id === containerId || container.id.startsWith(containerId) || container.name === containerId
    );
    
    if (containerIndex === -1) {
      return {
        success: false,
        message: `Error: No such container: ${containerId}`
      };
    }
    
    // コンテナの状態を更新
    if (this.state.containers[containerIndex].status === 'running') {
      this.state.containers[containerIndex].status = 'exited';
      
      return {
        success: true,
        message: containerId
      };
    } else {
      return {
        success: false,
        message: `Error: Container ${containerId} is not running`
      };
    }
  }

  /**
   * 'docker start'コマンド処理
   */
  private handleDockerStart(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker start [OPTIONS] CONTAINER [CONTAINER...]'
      };
    }

    const containerId = args[0];
    const containerIndex = this.state.containers.findIndex(
      container => container.id === containerId || container.id.startsWith(containerId) || container.name === containerId
    );
    
    if (containerIndex === -1) {
      return {
        success: false,
        message: `Error: No such container: ${containerId}`
      };
    }
    
    // コンテナの状態を更新
    if (this.state.containers[containerIndex].status !== 'running') {
      this.state.containers[containerIndex].status = 'running';
      
      return {
        success: true,
        message: containerId
      };
    } else {
      return {
        success: false,
        message: `Error: Container ${containerId} is already running`
      };
    }
  }

  /**
   * 'docker rm'コマンド処理
   */
  private handleDockerRm(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker rm [OPTIONS] CONTAINER [CONTAINER...]'
      };
    }

    const containerId = args[0];
    const forceRemove = args.includes('-f') || args.includes('--force');
    
    const containerIndex = this.state.containers.findIndex(
      container => container.id === containerId || container.id.startsWith(containerId) || container.name === containerId
    );
    
    if (containerIndex === -1) {
      return {
        success: false,
        message: `Error: No such container: ${containerId}`
      };
    }
    
    // 実行中のコンテナは削除できない（-fオプションがある場合を除く）
    if (this.state.containers[containerIndex].status === 'running' && !forceRemove) {
      return {
        success: false,
        message: `Error: You cannot remove a running container ${containerId}. Stop the container before attempting removal or use force`
      };
    }
    
    // コンテナを削除
    const removedContainer = this.state.containers.splice(containerIndex, 1)[0];
    
    return {
      success: true,
      message: removedContainer.id
    };
  }

  /**
   * 'docker rmi'コマンド処理
   */
  private handleDockerRmi(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker rmi [OPTIONS] IMAGE [IMAGE...]'
      };
    }

    const imageName = args[0];
    const forceRemove = args.includes('-f') || args.includes('--force');
    
    const imageIndex = this.state.images.indexOf(imageName);
    if (imageIndex === -1) {
      return {
        success: false,
        message: `Error: No such image: ${imageName}`
      };
    }
    
    // このイメージを使用しているコンテナをチェック
    const usedByContainers = this.state.containers.filter(container => container.image === imageName);
    if (usedByContainers.length > 0 && !forceRemove) {
      const containerIds = usedByContainers.map(container => container.id.substring(0, 12)).join(", ");
      return {
        success: false,
        message: `Error: conflict: unable to remove repository reference ${imageName} (must force) - container ${containerIds} is using its referenced image`
      };
    }
    
    // イメージを削除
    this.state.images.splice(imageIndex, 1);
    
    // 強制削除の場合は関連するコンテナも削除
    if (forceRemove) {
      this.state.containers = this.state.containers.filter(container => container.image !== imageName);
    }
    
    return {
      success: true,
      message: `Untagged: ${imageName}\nDeleted: ${imageName}`
    };
  }

  /**
   * 'docker build'コマンド処理
   */
  private handleDockerBuild(args: string[]): CommandResult {
    // 実際の実装では、Dockerfileを解析してイメージをビルドする
    let tagName = 'latest';
    let contextPath = '.';
    
    for (let i = 0; i < args.length; i++) {
      if ((args[i] === '-t' || args[i] === '--tag') && i + 1 < args.length) {
        tagName = args[i + 1];
        i++;
      } else if (args[i] === '-f' && i + 1 < args.length) {
        // Dockerfileパスは今回は無視
        i++;
      } else if (!args[i].startsWith('-')) {
        contextPath = args[i];
      }
    }
    
    // シミュレーション用に新しいイメージを追加
    const imageName = tagName.includes(':') ? tagName : `${tagName}:latest`;
    
    if (!this.state.images.includes(imageName)) {
      this.state.images.push(imageName);
    }
    
    return {
      success: true,
      message: `Successfully built image: ${imageName}\nContext: ${contextPath}`
    };
  }

  /**
   * 'docker network'コマンド処理
   */
  private handleDockerNetwork(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker network COMMAND'
      };
    }

    const subCommand = args[0];
    
    switch (subCommand) {
      case 'ls':
      case 'list':
        return {
          success: true,
          message: this.formatNetworkOutput(),
          data: this.state.networks
        };
      
      case 'create':
        if (args.length < 2) {
          return {
            success: false,
            message: 'Usage: docker network create [OPTIONS] NETWORK'
          };
        }
        
        const networkName = args[1];
        
        if (this.state.networks.includes(networkName)) {
          return {
            success: false,
            message: `Error: network with name ${networkName} already exists`
          };
        }
        
        this.state.networks.push(networkName);
        
        return {
          success: true,
          message: networkName
        };
      
      case 'rm':
      case 'remove':
        if (args.length < 2) {
          return {
            success: false,
            message: 'Usage: docker network rm NETWORK [NETWORK...]'
          };
        }
        
        const networkToRemove = args[1];
        
        if (!this.state.networks.includes(networkToRemove)) {
          return {
            success: false,
            message: `Error: No such network: ${networkToRemove}`
          };
        }
        
        // このネットワークを使用しているコンテナをチェック
        const usedByContainers = this.state.containers.filter(container => container.networks.includes(networkToRemove));
        if (usedByContainers.length > 0) {
          return {
            success: false,
            message: `Error: network ${networkToRemove} is in use by containers: ${usedByContainers.map(c => c.id.substring(0, 12)).join(', ')}`
          };
        }
        
        // 'bridge', 'host', 'none'は削除できない
        if (['bridge', 'host', 'none'].includes(networkToRemove)) {
          return {
            success: false,
            message: `Error: cannot remove built-in network: ${networkToRemove}`
          };
        }
        
        const networkIndex = this.state.networks.indexOf(networkToRemove);
        this.state.networks.splice(networkIndex, 1);
        
        return {
          success: true,
          message: networkToRemove
        };
      
      default:
        return {
          success: false,
          message: `Error: unknown network command: ${subCommand}`
        };
    }
  }

  /**
   * 'docker volume'コマンド処理
   */
  private handleDockerVolume(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker volume COMMAND'
      };
    }

    const subCommand = args[0];
    
    switch (subCommand) {
      case 'ls':
      case 'list':
        return {
          success: true,
          message: this.formatVolumeOutput(),
          data: this.state.volumes
        };
      
      case 'create':
        if (args.length < 2) {
          return {
            success: false,
            message: 'Usage: docker volume create [OPTIONS] [VOLUME]'
          };
        }
        
        const volumeName = args[1];
        
        if (this.state.volumes.includes(volumeName)) {
          return {
            success: false,
            message: `Error: volume with name ${volumeName} already exists`
          };
        }
        
        this.state.volumes.push(volumeName);
        
        return {
          success: true,
          message: volumeName
        };
      
      case 'rm':
      case 'remove':
        if (args.length < 2) {
          return {
            success: false,
            message: 'Usage: docker volume rm VOLUME [VOLUME...]'
          };
        }
        
        const volumeToRemove = args[1];
        
        if (!this.state.volumes.includes(volumeToRemove)) {
          return {
            success: false,
            message: `Error: No such volume: ${volumeToRemove}`
          };
        }
        
        // このボリュームを使用しているコンテナをチェック
        const usedByContainers = this.state.containers.filter(
          container => container.volumes.some(v => v.host === volumeToRemove || v.container === volumeToRemove)
        );
        
        if (usedByContainers.length > 0) {
          return {
            success: false,
            message: `Error: volume ${volumeToRemove} is in use by containers: ${usedByContainers.map(c => c.id.substring(0, 12)).join(', ')}`
          };
        }
        
        const volumeIndex = this.state.volumes.indexOf(volumeToRemove);
        this.state.volumes.splice(volumeIndex, 1);
        
        return {
          success: true,
          message: volumeToRemove
        };
      
      default:
        return {
          success: false,
          message: `Error: unknown volume command: ${subCommand}`
        };
    }
  }

  /**
   * 'docker logs'コマンド処理
   */
  private handleDockerLogs(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker logs [OPTIONS] CONTAINER'
      };
    }

    // 最後の引数をコンテナIDと見なす
    const containerId = args[args.length - 1];
    
    // コンテナが存在するか確認
    const container = this.state.containers.find(
      c => c.id === containerId || c.id.startsWith(containerId) || c.name === containerId
    );
    
    if (!container) {
      return {
        success: false,
        message: `Error: No such container: ${containerId}`
      };
    }
    
    // シミュレーションのため、固定のログメッセージを返す
    return {
      success: true,
      message: `[Container: ${container.name}]\n` +
               `Starting application...\n` +
               `Application started successfully.\n` +
               `Listening on port ${container.ports.map(p => p.container).join(', ') || 'unknown'}\n` +
               `Ready to accept connections.`
    };
  }

  /**
   * 'docker exec'コマンド処理
   */
  private handleDockerExec(args: string[]): CommandResult {
    if (args.length < 2) {
      return {
        success: false,
        message: 'Usage: docker exec [OPTIONS] CONTAINER COMMAND [ARG...]'
      };
    }

    // オプションを除外してコンテナIDとコマンドを取得
    let containerId = '';
    let command = '';
    let interactive = false;
    
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '-i' || args[i] === '--interactive' || args[i] === '-it') {
        interactive = true;
      } else if (!containerId) {
        containerId = args[i];
      } else {
        command = args.slice(i).join(' ');
        break;
      }
    }
    
    // コンテナが存在するか確認
    const container = this.state.containers.find(
      c => c.id === containerId || c.id.startsWith(containerId) || c.name === containerId
    );
    
    if (!container) {
      return {
        success: false,
        message: `Error: No such container: ${containerId}`
      };
    }
    
    // コンテナが実行中であることを確認
    if (container.status !== 'running') {
      return {
        success: false,
        message: `Error: Container ${containerId} is not running`
      };
    }
    
    // シミュレーションのため、コマンドに応じた固定レスポンスを返す
    if (command.includes('ls')) {
      return {
        success: true,
        message: 'app\nbin\netc\nhome\nlib\nmedia\nopt\nsbin\ntmp\nusr\nvar'
      };
    } else if (command.includes('echo')) {
      const echoText = command.split('echo ')[1]?.replace(/"/g, '') || '';
      return {
        success: true,
        message: echoText
      };
    } else if (command.includes('ps')) {
      return {
        success: true,
        message: 'PID   USER     TIME  COMMAND\n    1 root      0:00 /app/entrypoint.sh\n   20 root      0:00 node server.js'
      };
    } else {
      return {
        success: true,
        message: `Command executed: ${command}`
      };
    }
  }

  /**
   * 'docker compose'コマンド処理
   */
  private handleDockerCompose(args: string[]): CommandResult {
    if (args.length === 0) {
      return {
        success: false,
        message: 'Usage: docker compose [OPTIONS] COMMAND'
      };
    }

    const subCommand = args[0];
    
    switch (subCommand) {
      case 'up':
        // 非常に単純化されたdocker-compose up
        const detached = args.includes('-d') || args.includes('--detach');
        
        // シミュレーションのため、デフォルトのサービスを作成
        const serviceNames = ['app', 'db', 'redis'];
        
        // サービスごとにコンテナを作成
        const newContainers: Container[] = [];
        
        serviceNames.forEach(service => {
          const imageName = `${service}-image:latest`;
          
          // イメージが存在しなければ作成
          if (!this.state.images.includes(imageName)) {
            this.state.images.push(imageName);
          }
          
          // コンテナID生成
          const id = `container-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
          
          // コンテナ作成
          const container: Container = {
            id,
            name: `studygit-${service}-1`,
            image: imageName,
            status: 'running',
            ports: [],
            volumes: [],
            networks: ['studygit_default'],
            created: new Date().toISOString()
          };
          
          // サービスに応じたポートとボリュームの設定
          if (service === 'app') {
            container.ports.push({ host: '3000', container: '3000' });
            container.volumes.push({ host: './app', container: '/app' });
          } else if (service === 'db') {
            container.ports.push({ host: '5432', container: '5432' });
            container.volumes.push({ host: 'db-data', container: '/var/lib/postgresql/data' });
          } else if (service === 'redis') {
            container.ports.push({ host: '6379', container: '6379' });
          }
          
          // コンテナをステートに追加
          this.state.containers.push(container);
          newContainers.push(container);
        });
        
        // ネットワークがなければ作成
        if (!this.state.networks.includes('studygit_default')) {
          this.state.networks.push('studygit_default');
        }
        
        // ボリュームがなければ作成
        if (!this.state.volumes.includes('db-data')) {
          this.state.volumes.push('db-data');
        }
        
        // 応答メッセージの作成
        const message = detached
          ? 'Starting containers in detached mode'
          : `Creating network "studygit_default"\n` +
            `Creating volume "db-data"\n` +
            `Creating studygit-db-1     ... done\n` +
            `Creating studygit-redis-1  ... done\n` +
            `Creating studygit-app-1    ... done`;
        
        return {
          success: true,
          message,
          data: newContainers
        };
      
      case 'down':
        // シミュレーションのため、単純化したdown処理
        
        // docker-composeで作成したコンテナを削除
        const removedContainers = this.state.containers.filter(
          container => container.name.startsWith('studygit-')
        );
        
        this.state.containers = this.state.containers.filter(
          container => !container.name.startsWith('studygit-')
        );
        
        // studygit_defaultネットワークを削除
        const networkIndex = this.state.networks.indexOf('studygit_default');
        if (networkIndex !== -1) {
          this.state.networks.splice(networkIndex, 1);
        }
        
        return {
          success: true,
          message: `Stopping containers...\n` +
                  `Removing containers...\n` +
                  `Removing network studygit_default\n` +
                  `Removing volume db-data`,
          data: removedContainers
        };
      
      default:
        return {
          success: false,
          message: `Error: unknown compose command: ${subCommand}`
        };
    }
  }

  /**
   * 'docker help'コマンド処理
   */
  private handleDockerHelp(): CommandResult {
    let availableCommands: string[] = [];
    
    // 現在のレベルに基づいて利用可能なコマンドのリストを作成
    if (this.level >= DifficultyLevel.BEGINNER) {
      availableCommands.push('ps', 'run', 'images', 'stop', 'start', 'help');
    }
    
    if (this.level >= DifficultyLevel.BASIC) {
      availableCommands.push('pull', 'rm', 'rmi', 'logs');
    }
    
    if (this.level >= DifficultyLevel.INTERMEDIATE) {
      availableCommands.push('build', 'network', 'volume', 'exec');
    }
    
    if (this.level >= DifficultyLevel.ADVANCED) {
      availableCommands.push('compose');
    }
    
    const message = `
Docker コマンドシミュレーション ヘルプ
現在の難易度レベル: ${this.getLevelName(this.level)}

利用可能なコマンド:
${availableCommands.map(cmd => `  docker ${cmd}`).join('\n')}

各コマンドの詳細なヘルプは 'docker <コマンド> --help' で確認できます。

レベルアップすると、より高度なコマンドが利用可能になります。
`;
    
    return {
      success: true,
      message
    };
  }

  /**
   * 難易度レベルの名前を取得
   */
  private getLevelName(level: DifficultyLevel): string {
    switch (level) {
      case DifficultyLevel.BEGINNER:
        return '初心者 (Level 1)';
      case DifficultyLevel.BASIC:
        return '基本 (Level 2)';
      case DifficultyLevel.INTERMEDIATE:
        return '中級 (Level 3)';
      case DifficultyLevel.ADVANCED:
        return '上級 (Level 4)';
      default:
        return '不明';
    }
  }

  /**
   * docker ps コマンド出力フォーマット
   */
  private formatPsOutput(containers: Container[]): string {
    if (containers.length === 0) {
      return 'CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES';
    }
    
    const header = 'CONTAINER ID   IMAGE             COMMAND      CREATED          STATUS          PORTS                    NAMES';
    const lines = containers.map(container => {
      // 作成時間の相対表示
      const createdTime = this.getRelativeTimeString(new Date(container.created));
      
      // ポートマッピングの表示
      const ports = container.ports.map(p => `${p.host}:${p.container}`).join(', ');
      
      // ステータスの表示
      const status = container.status === 'running' 
        ? 'Up 2 hours'
        : container.status === 'exited'
          ? 'Exited (0)'
          : container.status;
      
      // コマンドの表示（最大20文字）
      const command = container.command && container.command.length > 20
        ? container.command.substring(0, 17) + '...'
        : container.command || '"/bin/sh"';
      
      return `${container.id.substring(0, 12)}   ${container.image.padEnd(16)}   "${command}"   ${createdTime.padEnd(15)}   ${status.padEnd(14)}   ${ports.padEnd(23)}   ${container.name}`;
    });
    
    return `${header}\n${lines.join('\n')}`;
  }

  /**
   * docker images コマンド出力フォーマット
   */
  private formatImagesOutput(): string {
    if (this.state.images.length === 0) {
      return 'REPOSITORY   TAG       IMAGE ID       CREATED        SIZE';
    }
    
    const header = 'REPOSITORY       TAG          IMAGE ID       CREATED          SIZE';
    const lines = this.state.images.map(image => {
      // イメージ名とタグの分離
      const [repo, tag] = image.includes(':') ? image.split(':') : [image, 'latest'];
      
      // ダミーのイメージID
      const imageId = `img-${Math.random().toString(36).substring(2, 10)}`;
      
      // ダミーのサイズとタイムスタンプ
      const size = `${Math.floor(Math.random() * 900) + 100}MB`;
      const created = this.getRelativeTimeString(new Date());
      
      return `${repo.padEnd(16)}   ${tag.padEnd(11)}   ${imageId.padEnd(14)}   ${created.padEnd(15)}   ${size}`;
    });
    
    return `${header}\n${lines.join('\n')}`;
  }

  /**
   * docker network コマンド出力フォーマット
   */
  private formatNetworkOutput(): string {
    if (this.state.networks.length === 0) {
      return 'NETWORK ID     NAME      DRIVER    SCOPE';
    }
    
    const header = 'NETWORK ID     NAME           DRIVER    SCOPE';
    const lines = this.state.networks.map(network => {
      // ダミーのネットワークID
      const networkId = `net-${Math.random().toString(36).substring(2, 10)}`;
      
      // ドライバとスコープの表示
      const driver = ['bridge', 'host', 'none'].includes(network) ? network : 'bridge';
      const scope = 'local';
      
      return `${networkId.padEnd(14)}   ${network.padEnd(14)}   ${driver.padEnd(9)}   ${scope}`;
    });
    
    return `${header}\n${lines.join('\n')}`;
  }

  /**
   * docker volume コマンド出力フォーマット
   */
  private formatVolumeOutput(): string {
    if (this.state.volumes.length === 0) {
      return 'DRIVER    VOLUME NAME';
    }
    
    const header = 'DRIVER    VOLUME NAME';
    const lines = this.state.volumes.map(volume => {
      return `local     ${volume}`;
    });
    
    return `${header}\n${lines.join('\n')}`;
  }

  /**
   * 相対時間の文字列を取得（「2 days ago」などの形式）
   */
  private getRelativeTimeString(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffDays > 0) {
      return `${diffDays} days ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hours ago`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minutes ago`;
    } else {
      return 'Just now';
    }
  }
}