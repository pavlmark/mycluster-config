# mycluster-config

GitOps project

Kubernetes Cluster v1.36.0 runs on 3 Virtual machines in VBox.

NAME   VERSION   OS-IMAGE                         KERNEL-VERSION           CONTAINER-RUNTIME
cp-01  v1.36.0  Debian GNU/Linux 12 (bookworm)   6.1.0-47-amd64 (amd64)   containerd://2.2.3
wn-01  v1.36.0  Debian GNU/Linux 12 (bookworm)   6.1.0-47-amd64 (amd64)   containerd://2.2.3
wn-02  v1.36.0  Debian GNU/Linux 12 (bookworm)   6.1.0-47-amd64 (amd64)   containerd://2.2.3

Name  CPU RAM STORAGE
cp-01 2   2GB 20GB
wn-01 1   2GB 20GB
wn-02 1   2GB 20GB
   
In cluster runs simple app writed on Python(Flask).
FluxCD monitors GitHub repo, FluxCD compare the repo state with the cluster state, if there are some updates or delete something, FLuxCD ensures that the deployed environment matches Git repo.

Plan:

Build solid platform with monitoring and security.
