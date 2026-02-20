## 1. Backend do Terraform

```hcl
terraform {
  backend "s3" {
    bucket = "soap-fiap-teste"
    key    = "oficina-fase2/terraform.tfstate"
    region = "us-east-1"
  }
}
```

**O que faz:**

* Configura o **backend remoto do Terraform**, usando um bucket S3 para armazenar o estado (`.tfstate`).
* Isso permite que múltiplas pessoas trabalhem no mesmo projeto de forma segura e mantém histórico de alterações.

**Aplicação:**

* Antes de rodar `terraform apply`, o Terraform vai armazenar o estado nesse bucket, garantindo rastreabilidade e persistência.

---

## 2. Providers

```hcl
required_providers {
  aws = {...}
  kubernetes = {...}
  null = {...}
}

provider "aws" { region = var.aws_region }

provider "kubernetes" { ... }
```

**O que faz:**

* `aws`: Conecta o Terraform à AWS para criar recursos.
* `kubernetes`: Permite criar recursos dentro do cluster EKS.
* `null`: Permite executar scripts ou comandos locais (`local-exec`) quando necessário.

**Aplicação:**

* Os providers são necessários para todas as chamadas de recurso subsequentes.

---

## 3. Rede (VPC, subnets, etc.)

```hcl
module "vpc" { ... }

resource "aws_db_subnet_group" "public" { ... }
```

**O que faz:**

* **VPC:** Cria uma VPC com CIDR `10.0.0.0/16`, com subnets públicas e privadas.
* **NAT Gateway:** Permite que recursos em subnets privadas acessem a internet.
* **Subnets públicas/privadas:** Separação entre recursos que precisam de acesso externo (ALB, RDS público) e internos (nós do EKS).
* **DB Subnet Group:** Define um grupo de subnets para a RDS, neste caso usando as públicas.

**Aplicação:**

* RDS e EKS usam estas subnets para criar instâncias e nós.
* As tags configuram o cluster Kubernetes para reconhecer essas subnets.

---

## 4. Cluster Kubernetes (EKS)

```hcl
module "eks" { ... }
```

**O que faz:**

* Cria um **cluster EKS** na VPC definida.
* Configura **nós gerenciados** do EKS (`t3.medium`, 1 a 3 nós).
* Permite acesso público e privado ao endpoint do cluster.
* Concede permissões administrativas ao criador do cluster.

**Aplicação:**

* Recursos do Kubernetes (pods, serviços, ingress) podem ser aplicados usando `kubectl` ou provider Kubernetes do Terraform.

---

## 5. Banco de Dados (RDS MySQL)

```hcl
resource "aws_security_group" "rds_sg" { ... }

resource "aws_db_instance" "mysql" { ... }

resource "null_resource" "db_schema_init" { ... }
```

**O que faz:**

* **Security Group:** Permite acesso externo à porta MySQL 3306 (atenção: aberto para todo o IP `0.0.0.0/0`).
* **RDS Instance:** Cria instância MySQL 8.0 pública com 20 GB GP3.
* **Schema Init (null_resource):** Executa script SQL (`${var.sql_script_path}`) após a criação da RDS, aguardando até o banco estar disponível.

**Aplicação:**

* O banco pode ser acessado externamente ou pelo EKS.
* O script SQL inicializa tabelas e dados necessários para a aplicação.

---

## 6. Servidor de Email (AWS SES + SNS)

```hcl
resource "aws_ses_email_identity" "oficina_email" { ... }

resource "aws_ses_configuration_set" "oficina_config" { ... }

resource "aws_sns_topic" "email_notifications" { ... }

resource "aws_ses_event_destination" "oficina_events" { ... }
```

**O que faz:**

* **SES Email Identity:** Registra o endereço `noreply@oficina-lameque.com` como remetente válido.
* **Configuration Set:** Permite agrupar configurações de envio.
* **SNS Topic:** Recebe notificações de eventos de email (bounces, complaints, deliveries).
* **Event Destination:** Conecta SES → SNS, permitindo monitorar entregas e falhas de email.

**Aplicação:**

* Aplicações podem enviar emails via SES usando essa identidade.
* O SNS permite automatizar alertas ou auditoria sobre falhas de envio.

---

### Resumo da Aplicação de Recursos

| Recurso                       | Como aplicar/usar                                                  |
| ----------------------------- | ------------------------------------------------------------------ |
| Backend S3                    | Armazena o estado Terraform                                        |
| VPC + Subnets                 | Cria rede isolada para EKS e RDS                                   |
| DB Subnet Group               | Agrupa subnets para RDS                                            |
| EKS Cluster                   | Hospeda aplicações em Kubernetes                                   |
| RDS MySQL                     | Banco de dados acessível publicamente, inicializado com script SQL |
| Security Group RDS            | Controla acesso ao banco                                           |
| Null Resource                 | Executa comandos locais (inicialização DB)                         |
| SES Email Identity            | Permite enviar emails da aplicação                                 |
| SES Configuration Set         | Configura envio e eventos de email                                 |
| SNS Topic + Event Destination | Recebe notificações de email (falhas, entregas, rejeições)         |

