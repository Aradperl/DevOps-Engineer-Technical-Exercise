terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "0.13.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
  }
}

provider "kind" {}

# Helm reads the API address and certificates from the cluster resource.
# Those values exist only after kind creates the cluster, so the first
# apply can create the cluster and install the charts together.
# kubectl uses terraform/kubeconfig, written by kind_cluster.exercise.
provider "helm" {
  kubernetes {
    host                   = kind_cluster.exercise.endpoint
    client_certificate     = kind_cluster.exercise.client_certificate
    client_key             = kind_cluster.exercise.client_key
    cluster_ca_certificate = kind_cluster.exercise.cluster_ca_certificate
  }
}
