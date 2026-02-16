## 1. Disparadores do Pipeline

```yaml
on:
  push:
    branches: [ main, teste-infra ]
  pull_request:
    branches: [ main, teste-infra ]
```

**O que faz:**

* O workflow é executado em **push** ou **pull request** para as branches `main` e `teste-infra`.
* Permite testar mudanças antes de mesclar para a branch principal.

---

## 2️. Job: build-and-test

```yaml
runs-on: ubuntu-latest
```

**O que faz:**

* Executa em um runner Ubuntu na nuvem do GitHub Actions.

### 2.1 Serviço MySQL

```yaml
services:
  mysql:
    image: mysql:8
    env:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: oficina_test
    ports:
      - 3306:3306
    options: --health-cmd="mysqladmin ping -h localhost -proot" ...
```

**O que faz:**

* Cria um container MySQL 8 para testes.
* Define senha root e database `oficina_test`.
* Configura **health check** para garantir que o banco esteja pronto antes de rodar os testes.

---

### 2.2 Etapas do job

1. **Checkout do código**

```yaml
- uses: actions/checkout@v4
```

* Obtém o código da branch atual para o runner.

2. **Setup Python**

```yaml
- uses: actions/setup-python@v5
```

* Instala Python 3.12 no runner.

3. **Instalação de dependências**

```yaml
pip install -r requirements.txt 
pip install pytest pytest-cov pymysql coverage
```

* Instala bibliotecas do projeto e ferramentas de teste e cobertura.

4. **Espera o MySQL ficar pronto**

```yaml
for i in {1..30}; do
  mysqladmin ping -h 127.0.0.1 -proot --silent && break
  sleep 2
done
```

* Evita que testes falhem por tentativa de conexão antes do banco estar ativo.

5. **Inicializa schema do banco**

```yaml
mysql -h 127.0.0.1 -uroot -proot oficina_test < scripts/create_db_oficina.sql
```

* Cria tabelas e dados necessários para testes automatizados.

6. **Executa testes com cobertura**

```yaml
pytest --cov=./ --cov-report=xml --cov-report=html ...
```

* Executa testes unitários.
* Gera relatório em **HTML** e **XML**.
* Falha o job se cobertura < 80%.

7. **Upload do relatório**

```yaml
uses: actions/upload-artifact@v4
```

* Salva a pasta `htmlcov/` como artefato do workflow, podendo ser baixado depois.

8. **Verifica cobertura**

```yaml
python -c "import xml.etree.ElementTree as ET ..."
```

* Lê o arquivo `coverage.xml`.
* Garante que a cobertura seja pelo menos 80%.
* Falha o pipeline caso a cobertura seja menor.

9. **Build e push da imagem Docker**

```yaml
docker build -t lamequesao/oficina-api:${{ github.sha }} .
docker push lamequesao/oficina-api:${{ github.sha }}
```

* Cria a imagem Docker da aplicação.
* Tagueia com o commit SHA atual.
* Faz push para Docker Hub, usando `DOCKERHUB_TOKEN` armazenado como secret.

---

## 3 Job: deploy

```yaml
needs: build-and-test
if: github.ref == 'refs/heads/main'
```

**O que faz:**

* Só roda após `build-and-test` com sucesso.
* Só executa na branch `main`.

### Etapas do deploy

1. **Checkout do código**

* Necessário para aplicar manifests Kubernetes.

2. **Configura AWS credentials**

```yaml
aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

* Permite interagir com AWS (EKS, S3, RDS, etc).

3. **Atualiza kubeconfig**

```bash
aws eks update-kubeconfig --name oficina-fase2
```

* Configura kubectl para acessar o cluster EKS.

4. **Cria secrets no Kubernetes**

```bash
kubectl create secret generic app-secrets ...
```

* Cria segredos com credenciais do banco e variáveis da aplicação.

5. **Deploy de recursos Kubernetes**

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment-api.yaml
kubectl set image deployment/fastapi-app fastapi=lamequesao/oficina-api:${{ github.sha }}
kubectl apply -f k8s/service-api.yaml
kubectl apply -f k8s/hpa.yaml
```

* Aplica ConfigMaps, Deployment, Service e HPA (Horizontal Pod Autoscaler).
* Atualiza imagem Docker do Deployment com a nova versão do commit.

6. **Deploy do banco**

```bash
echo "Banco de dados gerenciado pelo Terraform"
```

* RDS já é provisionado pelo Terraform; não precisa criar via K8s.

7. **Restart do deployment**

```bash
kubectl rollout restart deployment/fastapi-app
```

* Garante que pods usem a última imagem.

---

### Resumo do CI/CD

| Etapa             | Função                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------------- |
| build-and-test    | Testa código localmente, inicializa MySQL, executa testes, gera cobertura                |
| docker build/push | Cria imagem Docker e envia para Docker Hub                                               |
| deploy            | Atualiza cluster EKS, aplica manifests, atualiza imagem do Deployment, configura secrets |

