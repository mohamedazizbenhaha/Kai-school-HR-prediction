# Kubernetes Deployment Documentation: Employee Turnover Prediction API

## Overview

This document details the deployment of the Employee Turnover Prediction API on Kubernetes using Helm. Designed for scalability, reliability, and security, this setup supports both educational use and production-grade environments. It assumes basic Kubernetes and Helm knowledge but includes explanations for key terms.

---

## Table of Contents

- [1. Architecture Overview](#1-architecture-overview)
- [2. Helm Chart Structure](#2-helm-chart-structure)
- [3. Kubernetes Resources](#3-kubernetes-resources)
  - [3.1 Namespace](#31-namespace)
  - [3.2 Deployment](#32-deployment)
  - [3.3 Service](#33-service)
  - [3.4 Network Policy](#34-network-policy)
- [4. Configuration](#4-configuration)
- [5. Deployment Steps](#5-deployment-steps)
- [6. Security Considerations](#6-security-considerations)
- [7. Best Practices](#7-best-practices)
- [8. Troubleshooting](#8-troubleshooting)

---

## 1. Architecture Overview

The API is deployed on Kubernetes, a platform for orchestrating containerized workloads. Key components include:

- **Pods**: Smallest deployable units, each running the Flask API container with the ML model.
- **Services**: Expose the API to clients, providing load balancing and a stable endpoint.
- **Namespaces**: Isolate resources, enhancing organization and security.
- **Network Policies**: Restrict traffic for improved security.

This setup leverages Helm, a package manager for Kubernetes, to streamline deployment and configuration.

---

## 2. Helm Chart Structure

The Helm chart, located in `Kai-school-chart/`, packages all Kubernetes resources. Its structure is:

```
Kai-school-chart/
├── Chart.yaml          # Metadata (name, version, description)
├── values.yaml         # Configurable values (image, replicas, etc.)
└── templates/          # Kubernetes resource templates
    ├── deployment.yaml    # Pod and replica management
    ├── namespace.yaml     # Resource isolation
    ├── networkpolicy.yaml # Traffic control
    ├── service.yaml       # API exposure
```

Each file’s purpose is detailed in subsequent sections.

---

## 3. Kubernetes Resources

### 3.1 Namespace

- **Purpose**: Isolates the API’s resources within the cluster.
- **File**: `templates/namespace.yaml`
- **Benefits**: Prevents naming conflicts, supports resource quotas, and enables role-based access control (RBAC).

### 3.2 Deployment

- **Purpose**: Ensures the desired number of API pods are running and updated.
- **File**: `templates/deployment.yaml`
- **Features**:
  - Uses a specified Docker image (e.g., `myregistry/turnover-api:1.0`).
  - Defines CPU/memory requests and limits.
  - Supports rolling updates for zero downtime.
  - Scales via replica count adjustments.

### 3.3 Service

- **Purpose**: Provides a stable endpoint for accessing the API.
- **File**: `templates/service.yaml`
- **Types**:
  - `ClusterIP`: Default, for internal cluster access.
  - `NodePort`: Exposes the API on a node’s port (e.g., 30000-32767).
  - `LoadBalancer`: For cloud providers with external IPs.
- **Benefit**: Balances traffic across pods.

### 3.4 Network Policy

- **Purpose**: Controls pod traffic, allowing only authorized communication.
- **File**: `templates/networkpolicy.yaml`
- **Example**: Permits ingress from a monitoring service on port 5000.

---

## 4. Configuration

- **Chart.yaml**: Defines chart metadata (e.g., `name: turnover-api`, `version: 1.0.0`).
- **values.yaml**: Sets defaults (e.g., `replicaCount: 2`, `image: myregistry/turnover-api:1.0`).
- **Customization**: Override values during installation:
  ```bash
  helm install turnover-api ./Kai-school-chart --set replicaCount=3
  ```

---

## 5. Deployment Steps

1. **Build and Push Docker Image**  
   ```bash
   docker build -t myregistry/turnover-api:1.0 .
   docker push myregistry/turnover-api:1.0
   ```

2. **Update `values.yaml`**  
   - Set `image.repository` and `image.tag` to match your registry.

3. **Install the Helm Chart**  
   ```bash
   helm install turnover-api ./Kai-school-chart --namespace kai-school --create-namespace
   ```

4. **Verify Deployment**  
   ```bash
   kubectl get pods,svc -n kai-school
   ```

5. **Access the API**  
   - **NodePort**: `http://<node-ip>:<node-port>`
   - **Port Forwarding**:  
     ```bash
     kubectl port-forward svc/turnover-api 5000:5000 -n kai-school
     ```

---

## 6. Security Considerations

- **Network Policy**: Limits traffic to/from pods (e.g., allow only port 5000).
- **Namespace Isolation**: Restricts resource access via RBAC.
- **Resource Limits**: Prevents overuse (e.g., `cpu: 500m`, `memory: 512Mi`).
- **Secrets**: Store sensitive data (e.g., API keys):  
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: api-secrets
  data:
    key: <base64-value>
  ```

---

## 7. Best Practices

- **Resource Management**: Set requests/limits for predictable scheduling.
- **Health Checks**: Use liveness/readiness probes:
  ```yaml
  livenessProbe:
    httpGet:
      path: /health
      port: 5000
  ```
- **Rolling Updates**: Ensure zero-downtime deployments.
- **Monitoring**: Integrate Prometheus for metrics and Fluentd for logs.

---

## 8. Troubleshooting

- **Pods Not Starting**:  
  - Check logs: `kubectl logs <pod-name> -n kai-school`  
  - Verify image pull: `kubectl describe pod <pod-name> -n kai-school`
- **Service Unreachable**:  
  - Confirm endpoints: `kubectl get ep -n kai-school`  
  - Test connectivity: `curl <service-ip>:5000`
- **Network Issues**: Review `networkpolicy.yaml` for restrictive rules.
- **High Latency**: Increase replicas or resource limits.

---

## Summary

This Helm-based Kubernetes deployment ensures the API is scalable, secure, and maintainable, serving as a reliable foundation for both learning and production scenarios.