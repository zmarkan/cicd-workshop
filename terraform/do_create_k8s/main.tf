terraform {

  required_version = ">= 0.13"

  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "1.13.3"
    }    
    local = {
      source = "hashicorp/local"
    }
  }

  backend "remote" {
    organization = "zmarkan-demos"
    workspaces {
      name = "iac-do"
    }
  }
}

# Set up the DO K8s cluster
provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_kubernetes_cluster" "k8s_cluster" {
  name   = var.cluster_name
  region = "nyc3"
  # Grab the latest version slug from `doctl kubernetes options versions`
  version = var.do_k8s_slug_ver

  node_pool {
    name       = var.cluster_name
    size       = "s-1vcpu-2gb"
    node_count = 2
    auto_scale = true
    min_nodes  = 2
    max_nodes  = 3
    tags       = [var.cluster_name]
  }
}

# resource "local_file" "k8s_config" {
#   content  = digitalocean_kubernetes_cluster.k8s_cluster.kube_config[0].raw_config
#   filename = pathexpand("~/.kube/${var.cluster_name}-config.yaml")
# }
