-- Primeiro verifica se o usuário já existe antes de criar
DROP USER IF EXISTS 'lameque'@'localhost';
DROP USER IF EXISTS 'lameque'@'%';

CREATE USER 'lameque'@'localhost' IDENTIFIED BY 'lameque123';

GRANT ALL PRIVILEGES ON *.* TO 'lameque'@'localhost' WITH GRANT OPTION;

CREATE USER 'lameque'@'%' IDENTIFIED BY 'lameque123';

GRANT ALL PRIVILEGES ON *.* TO 'lameque'@'%' WITH GRANT OPTION;


FLUSH PRIVILEGES;

-- Cria o banco de dados se não existir
CREATE DATABASE IF NOT EXISTS oficina_ordem_servico;
USE oficina_ordem_servico;

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET collation_connection = 'utf8mb4_unicode_ci';

-- oficina_ordem_servico.usuario definição
CREATE TABLE `usuario` (
  `usuario_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `dta_cadastro` datetime DEFAULT NULL,
  `ativo` boolean NOT NULL DEFAULT true,
  PRIMARY KEY (`usuario_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- oficina_ordem_servico.cliente definição
CREATE TABLE `cliente` (
  `cliente_id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `cpf_cnpj` varchar(14) NOT NULL,
  `tipo_cliente` enum('PF','PJ') NOT NULL,
  PRIMARY KEY (`cliente_id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  UNIQUE KEY `cpf_cnpj` (`cpf_cnpj`),
  CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`usuario_id`) 
      REFERENCES `usuario` (`usuario_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- oficina_ordem_servico.funcionario definição
CREATE TABLE `funcionario` (
  `funcionario_id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `matricula` int NOT NULL,
  `cpf` varchar(11) NOT NULL,
  `tipo_funcionario` enum('ADMINISTRADOR','MECANICO') NOT NULL,
  PRIMARY KEY (`funcionario_id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  UNIQUE KEY `matricula` (`matricula`),
  CONSTRAINT `funcionario_ibfk_1` FOREIGN KEY (`usuario_id`) 
      REFERENCES `usuario` (`usuario_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- oficina_ordem_servico.veiculo definição
CREATE TABLE `veiculo` (
  `veiculo_id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `placa` varchar(7) NOT NULL,
  `modelo` varchar(255) NOT NULL,
  `ano` int NOT NULL,
  `dta_cadastro` datetime DEFAULT NULL,
  PRIMARY KEY (`veiculo_id`),
  UNIQUE KEY `placa` (`placa`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `veiculo_ibfk_1` FOREIGN KEY (`cliente_id`) 
      REFERENCES `cliente` (`cliente_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- oficina_ordem_servico.ordem_servico definição
CREATE TABLE `ordem_servico` (
  `ordem_servico_id` int NOT NULL AUTO_INCREMENT,
  `veiculo_id` int NOT NULL,
  `status` enum('RECEBIDA','EM_DIAGNOSTICO','AGUARDANDO_APROVACAO','EM_EXECUCAO','FINALIZADA','ENTREGUE') NOT NULL,
  `obsercacoes` varchar(255) DEFAULT NULL,
  `dta_criacao` datetime DEFAULT NULL,
  `dta_finalizacao` datetime DEFAULT NULL,
  PRIMARY KEY (`ordem_servico_id`),
  KEY `veiculo_id` (`veiculo_id`),
  CONSTRAINT `ordem_servico_ibfk_1` FOREIGN KEY (`veiculo_id`) 
      REFERENCES `veiculo` (`veiculo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
