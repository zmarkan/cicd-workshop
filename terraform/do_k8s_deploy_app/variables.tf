variable "do_token" {
  type        = string
  description = "Your DigitalOcean API token. See https://cloud.digitalocean.com/account/api/tokens to generate a token."
}

variable "cluster_name" {
  type  = string
  description = "Name for Kubernetes Cluster"
  validation {
    condition     = can(regex("^[0-9A-Za-z_-]+$", var.cluster_name))
    error_message = "Enter a valid group number. Tip: it doesnt strictly need to be a number, but it must only contain letters, numbers, underscores and dashes."
  }  
}

variable "docker_image" {
  type        = string
  description = "name of the docker image to deploy"
  default     = "ariv3ra/nodejs-circleci:latest"
}

