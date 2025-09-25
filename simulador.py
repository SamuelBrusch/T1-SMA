import simpy
import random
import statistics
import yaml

# ----------------------------
# Função para carregar modelo
# ----------------------------
def carregar_modelo(path_yml):
    try:
        with open(path_yml, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path_yml}")
    except yaml.YAMLError as e:
        raise ValueError(f"Erro ao processar arquivo YAML: {e}")

# ----------------------------
# Processo de cliente
# ----------------------------
def cliente(env, nome, servidores, taxas_servico, tempos_espera):
    chegada = env.now
    for i, servidor in enumerate(servidores):
        with servidor.request() as req:
            yield req
            tempo_servico = random.expovariate(taxas_servico[i])
            yield env.timeout(tempo_servico)
    saida = env.now
    tempos_espera.append(saida - chegada)

# ----------------------------
# Gerador de clientes
# ----------------------------
def gerador_clientes(env, num_clientes, taxa_chegada, servidores, taxas_servico, tempos_espera):
    for i in range(num_clientes):
        yield env.timeout(random.expovariate(taxa_chegada))
        env.process(cliente(env, f"Cliente {i}", servidores, taxas_servico, tempos_espera))

# ----------------------------
# Função principal
# ----------------------------
def simular(config_path):
    # Carrega config do YAML
    config = carregar_modelo(config_path)

    # Configuração
    random.seed(config["seed"])
    num_clientes = config["num_clientes"]
    taxa_chegada = config["taxa_chegada"]

    # Ambiente
    env = simpy.Environment()
    
    # Servidores
    servidores = []
    taxas_servico = []
    for fila in config["filas"]:
        servidores.append(simpy.Resource(env, capacity=fila["capacidade"]))
        taxas_servico.append(fila["taxa_servico"])

    tempos_espera = []
    env.process(gerador_clientes(env, num_clientes, taxa_chegada, servidores, taxas_servico, tempos_espera))

    # Executa
    env.run()

    # Resultados
    print("\n=== RESULTADOS ===")
    print(f"Clientes atendidos: {len(tempos_espera)}")
    print(f"Tempo médio no sistema: {statistics.mean(tempos_espera):.2f}")
    print(f"Tempo máximo no sistema: {max(tempos_espera):.2f}")
    print("==================")

# ----------------------------
# Execução
# ----------------------------
if __name__ == "__main__":
    simular("modelo.yml")
