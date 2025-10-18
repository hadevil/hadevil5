#!/usr/bin/env python3
"""
Cliente para interagir com agentes do Cursor
"""

from typing import Dict, Any

class CursorAgentClient:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.base_url = "https://cursor.com/agents"
        self.selected_agent_url = f"{self.base_url}?selectedBcId={agent_id}"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o agente específico
        """
        return {
            "agent_id": self.agent_id,
            "url": self.selected_agent_url,
            "base_url": self.base_url
        }
    
    def format_agent_url(self) -> str:
        """
        Retorna a URL formatada para o agente
        """
        return self.selected_agent_url

def main():
    # ID do agente fornecido no URL
    agent_id = "bc-6c968cce-1f32-4745-b655-c4f39e4d1406"
    
    # Criar cliente
    client = CursorAgentClient(agent_id)
    
    # Exibir informações
    print("=== Informações do Agente Cursor ===")
    info = client.get_agent_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nURL para acessar o agente: {client.format_agent_url()}")

if __name__ == "__main__":
    main()