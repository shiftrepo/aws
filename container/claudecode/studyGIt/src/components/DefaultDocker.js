// DefaultDocker.js
// Dockerコンテナのサンプルデータ

const DEFAULT_DOCKER_STATE = {
  containers: [
    {
      id: 'abc123def456',
      name: 'git-playground',
      image: 'git-playground:latest',
      status: 'running',
      ports: [
        {
          host: '3000',
          container: '3000'
        }
      ],
      volumes: [
        {
          host: '.',
          container: '/app'
        },
        {
          host: '/app/node_modules',
          container: '/app/node_modules'
        }
      ],
      networks: ['git-playground_default']
    },
    {
      id: '789ghi101112',
      name: 'postgres-db',
      image: 'postgres:13',
      status: 'running',
      ports: [
        {
          host: '5432',
          container: '5432'
        }
      ],
      volumes: [
        {
          host: 'postgres-data',
          container: '/var/lib/postgresql/data'
        }
      ],
      networks: ['git-playground_default']
    },
    {
      id: '131415jkl',
      name: 'redis-cache',
      image: 'redis:alpine',
      status: 'exited',
      ports: [
        {
          host: '6379',
          container: '6379'
        }
      ],
      volumes: [],
      networks: ['git-playground_default']
    }
  ],
  networks: ['git-playground_default', 'bridge'],
  images: ['git-playground:latest', 'postgres:13', 'redis:alpine', 'node:16'],
  volumes: ['postgres-data', 'node_modules']
};

export default DEFAULT_DOCKER_STATE;