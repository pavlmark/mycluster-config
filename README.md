# mycluster-config

## Kubernetes Cluster v1.36.0 runs on 3 Virtual machines in VBox.

| NAME  | VERSION | OS IMAGE | KERNEL VERSION | CONTAINER RUNTIME |
|---|---|---|---|---|
| cp-01 | v1.36.0 | Debian GNU/Linux 12 (bookworm) | 6.1.0-47-amd64 | containerd://2.2.3 |
| wn-01 | v1.36.0 | Debian GNU/Linux 12 (bookworm) | 6.1.0-47-amd64 | containerd://2.2.3 |
| wn-02 | v1.36.0 | Debian GNU/Linux 12 (bookworm) | 6.1.0-47-amd64 | containerd://2.2.3 |

## Virtual Machine Resources

| Name | CPU | RAM | Storage |
|---|---|---|---|
| cp-01 | 2 | 4GB | 20GB |
| wn-01 | 2 | 4GB | 20GB |
| wn-02 | 2 | 4GB | 20GB |
   
In cluster runs simple app writed on Python(Flask).
FluxCD monitors GitHub repo, FluxCD compare the repo state with the cluster state, if there are some updates or delete something, FLuxCD ensures that the deployed environment matches Git repo.
Also, there are monitoring apps like Prometheus, Grafana(dasboard for Prometheus).
There is app Argo CD for Deploy in GUI.


Tasks:
1. I need to polish CI/CD pipeline in GitHub Action. For now, there doesn't work tag update Docker Image from repo on my app to DockerHub.
2. Hide Prometheus behind VPN or create authentication, because by default it doesn't have authentication. Need to find info, and inverstigate this moment.
3. Add PV in cluster for data.
4. Migrate or copy date to cloud (AWS S3)
5. Learn how write documentation on GitHub:)

Plan:

Build solid platform with monitoring and security.
