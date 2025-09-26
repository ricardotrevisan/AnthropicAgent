import os
import requests
from typing import Dict, Any
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
import json
import math
from dotenv import load_dotenv

# Configuração da API Key do Claude
load_dotenv()

class CalculadoraTool(BaseTool):
    """Ferramenta para realizar cálculos matemáticos"""
    
    name: str = "calculadora"
    description: str = """
    Útil para realizar cálculos matemáticos básicos e avançados.
    Input deve ser uma expressão matemática válida como string.
    Exemplos: '2+2', '(10*5)/2', 'sqrt(16)', 'sin(3.14159/2)'
    """
    
    def _run(self, query: str) -> str:
        """Executa o cálculo matemático"""
        try:
            # Substituições para funções matemáticas
            query = query.replace('sqrt', 'math.sqrt')
            query = query.replace('sin', 'math.sin')
            query = query.replace('cos', 'math.cos')
            query = query.replace('tan', 'math.tan')
            query = query.replace('log', 'math.log')
            query = query.replace('pi', 'math.pi')
            query = query.replace('e', 'math.e')
            
            # Avalia a expressão de forma segura
            allowed_names = {
                k: v for k, v in math.__dict__.items() 
                if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(query, {"__builtins__": {}}, allowed_names)
            return f"Resultado: {result}"
            
        except Exception as e:
            return f"Erro no cálculo: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Versão assíncrona da ferramenta"""
        return self._run(query)

class InformacoesCidadeTool(BaseTool):
    """Ferramenta para buscar informações sobre cidades"""
    
    name: str = "info_cidade"
    description: str = """
    Útil para obter informações sobre uma cidade específica.
    Input deve ser o nome da cidade.
    Retorna informações como população, país, coordenadas, etc.
    """
    
    def _run(self, cidade: str) -> str:
        """Busca informações sobre a cidade"""
        try:
            # Simulação de uma API de cidades (substitua por uma API real)
            # Exemplo usando uma API pública gratuita
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            
            # Base de dados simulada para demonstração
            cidades_db = {
                "são paulo": {
                    "pais": "Brasil",
                    "populacao": "12.3 milhões",
                    "area": "1.521 km²",
                    "coordenadas": "(-23.5505, -46.6333)",
                    "info": "Maior cidade do Brasil e centro financeiro"
                },
                "rio de janeiro": {
                    "pais": "Brasil", 
                    "populacao": "6.7 milhões",
                    "area": "1.200 km²",
                    "coordenadas": "(-22.9068, -43.1729)",
                    "info": "Cidade maravilhosa, ex-capital do Brasil"
                },
                "paris": {
                    "pais": "França",
                    "populacao": "2.1 milhões",
                    "area": "105 km²",
                    "coordenadas": "(48.8566, 2.3522)",
                    "info": "Capital da França, cidade luz"
                },
                "tokyo": {
                    "pais": "Japão",
                    "populacao": "13.9 milhões",
                    "area": "2.194 km²", 
                    "coordenadas": "(35.6762, 139.6503)",
                    "info": "Capital do Japão, maior área metropolitana do mundo"
                }
            }
            
            cidade_lower = cidade.lower()
            if cidade_lower in cidades_db:
                info = cidades_db[cidade_lower]
                resultado = f"""
                    Informações sobre {cidade.title()}:
                    • País: {info['pais']}
                    • População: {info['populacao']}
                    • Área: {info['area']}
                    • Coordenadas: {info['coordenadas']}
                    • Info adicional: {info['info']}
                                    """.strip()
                return resultado
            else:
                return f"Informações para '{cidade}' não encontradas na base de dados."
                
        except Exception as e:
            return f"Erro ao buscar informações da cidade: {str(e)}"
    
    async def _arun(self, cidade: str) -> str:
        """Versão assíncrona da ferramenta"""
        return self._run(cidade)

class AgenteClaudeDemo:
    """Classe principal do agente"""
    
    def __init__(self, api_key: str):
        """Inicializa o agente com Claude e as ferramentas"""
        
        # Configurar o modelo Claude
        self.llm = ChatAnthropic(
            anthropic_api_key=api_key,
            model="claude-3-7-sonnet-latest",
            temperature=0.1,
            max_tokens=1000
        )
        
        # Inicializar as ferramentas
        self.tools = [
            CalculadoraTool(),
            InformacoesCidadeTool()
        ]
        
        # Criar o agente
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def executar(self, pergunta: str) -> str:
        """Executa uma pergunta no agente"""
        try:
            response = self.agent.run(pergunta)
            return response
        except Exception as e:
            return f"Erro na execução: {str(e)}"
    
    def listar_ferramentas(self) -> str:
        """Lista as ferramentas disponíveis"""
        info = "Ferramentas disponíveis:\n"
        for tool in self.tools:
            info += f"• {tool.name}: {tool.description}\n"
        return info

def main():
    """Função principal para demonstração"""
    
    # Criar o agente
    print("🤖 Inicializando agente com Claude...")
    agente = AgenteClaudeDemo(os.getenv("ANTHROPIC_API_KEY"))
    
    # Mostrar ferramentas disponíveis
    print("\n" + agente.listar_ferramentas())
    
    # Exemplos de uso
    exemplos = [
        "Quanto é 2 + 2?",
        "Calcule a raiz quadrada de 144",
        "Me dê informações sobre São Paulo",
        "Qual é a população do Rio de Janeiro?",
        "Calcule (10 * 5) + sqrt(25) e depois me diga sobre Paris"
    ]
        
    print("\n🔍 Exemplos de perguntas:")
    for i, exemplo in enumerate(exemplos, 1):
        print(f"{i}. {exemplo}")
    
    # Interface interativa
    print("\n" + "="*50)
    print("💬 Chat interativo (digite 'sair' para terminar)")
    print("="*50)
    
    while True:
        try:
            pergunta = input("\n👤 Você: ").strip()
            
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
            
            if not pergunta:
                continue
                
            print("\n🤖 Claude pensando...")
            resposta = agente.executar(pergunta)
            print(f"\n🤖 Claude: {resposta}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()