resource "kubernetes_service" "app" {
  metadata {
    name = var.cluster_name
  }
  spec {
    selector = {
      app = kubernetes_deployment.app.metadata.0.labels.app
    }
    port {
      port        = 80
      target_port = 3232
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name = var.cluster_name
    labels = {
      app = var.cluster_name
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = var.cluster_name
      }
    }

    template {
      metadata {
        labels = {
          app = var.cluster_name
        }
      }

      spec {
        container {
          image = var.docker_image
          name  = var.cluster_name
          port {
            name           = "port-5000"
            container_port = 5000
          }
        }
      }
    }
  }
}