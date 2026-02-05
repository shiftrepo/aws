# GitLab Configuration File
# This file is managed by the infrastructure setup

## External URL Configuration
external_url 'http://localhost:5003'
registry_external_url 'http://localhost:5005'

## GitLab Shell SSH Configuration
gitlab_rails['gitlab_shell_ssh_port'] = 2222

## GitLab Registry Configuration
registry['enable'] = true
gitlab_rails['registry_enabled'] = true
gitlab_rails['registry_host'] = "localhost"
gitlab_rails['registry_port'] = "5005"
gitlab_rails['registry_path'] = "/var/opt/gitlab/gitlab-rails/shared/registry"

## Performance Tuning for Container Environment
puma['worker_processes'] = 2
puma['min_threads'] = 4
puma['max_threads'] = 4

sidekiq['max_concurrency'] = 10

## Disable Monitoring Services to Save Resources
prometheus_monitoring['enable'] = false
grafana['enable'] = false
alertmanager['enable'] = false

## GitLab Email Configuration (Optional)
# gitlab_rails['smtp_enable'] = true
# gitlab_rails['smtp_address'] = "smtp.server"
# gitlab_rails['smtp_port'] = 587
# gitlab_rails['smtp_user_name'] = "smtp user"
# gitlab_rails['smtp_password'] = "smtp password"
# gitlab_rails['smtp_domain'] = "example.com"
# gitlab_rails['smtp_authentication'] = "login"
# gitlab_rails['smtp_enable_starttls_auto'] = true
# gitlab_rails['gitlab_email_from'] = 'gitlab@example.com'
# gitlab_rails['gitlab_email_reply_to'] = 'noreply@example.com'

## GitLab Backup Configuration
gitlab_rails['backup_keep_time'] = 604800  # 7 days

## GitLab Container Registry Storage
registry['storage'] = {
  'filesystem' => {
    'rootdirectory' => '/var/opt/gitlab/gitlab-rails/shared/registry'
  }
}

## GitLab Pages (Disabled)
pages_external_url "http://pages.localhost"
gitlab_pages['enable'] = false

## GitLab Mattermost (Disabled)
mattermost['enable'] = false

## GitLab Packages
gitlab_rails['packages_enabled'] = true
gitlab_rails['packages_storage_path'] = "/var/opt/gitlab/gitlab-rails/shared/packages"

## GitLab Dependency Proxy
gitlab_rails['dependency_proxy_enabled'] = true

## GitLab Time Zone
gitlab_rails['time_zone'] = 'UTC'

## Database Connection Pool
postgresql['max_connections'] = 200
gitlab_rails['db_pool'] = 10

## Nginx Configuration
nginx['listen_port'] = 5003
nginx['listen_https'] = false

## GitLab Workhorse
gitlab_workhorse['listen_network'] = "tcp"
gitlab_workhorse['listen_addr'] = "0.0.0.0:8181"

## Unicorn/Puma Workers
# Set this based on available memory
# Memory = puma_workers * (memory_per_worker) + shared_memory
# Recommended: 1 worker per GB of RAM

## GitLab KAS (Kubernetes Agent Server) - Optional
# gitlab_kas['enable'] = true
# gitlab_kas['listen_address'] = '0.0.0.0:8150'

## Disable automatic database migrations
gitlab_rails['auto_migrate'] = true

## Custom Nginx Configuration
# nginx['custom_gitlab_server_config'] = "location ^~ /foo-namespace/bar-project/raw/ {\n deny all;\n}\n"

## GitLab Geo (Disabled for single instance)
gitlab_rails['geo_registry_replication_enabled'] = false

## Logging
logging['logrotate_frequency'] = "daily"
logging['logrotate_size'] = nil  # Rotate by time, not size
logging['logrotate_rotate'] = 7  # Keep 7 days of logs
logging['logrotate_compress'] = "compress"
logging['logrotate_method'] = "copytruncate"
