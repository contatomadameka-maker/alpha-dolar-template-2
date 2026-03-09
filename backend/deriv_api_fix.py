# Adicione na função get_proposal, após receber a proposta:

# No _on_message, quando msg_type == "proposal":
# DEPOIS DE:
# proposal = data.get("proposal", {})
# self.log(f"Proposta recebida: ID {proposal.get('id')}", "INFO")

# ADICIONE:
# Auto-compra
proposal_id = proposal.get('id')
price = proposal.get('ask_price')
if proposal_id and price:
    self.buy_contract(proposal_id, price)
# Adicione na função get_proposal, após receber a proposta:

# No _on_message, quando msg_type == "proposal":
# DEPOIS DE:
# proposal = data.get("proposal", {})
# self.log(f"Proposta recebida: ID {proposal.get('id')}", "INFO")

# ADICIONE:
# Auto-compra
proposal_id = proposal.get('id')
price = proposal.get('ask_price')
if proposal_id and price:
    self.buy_contract(proposal_id, price)
# Adicione na função get_proposal, após receber a proposta:

# No _on_message, quando msg_type == "proposal":
# DEPOIS DE:
# proposal = data.get("proposal", {})
# self.log(f"Proposta recebida: ID {proposal.get('id')}", "INFO")

# ADICIONE:
# Auto-compra
proposal_id = proposal.get('id')
price = proposal.get('ask_price')
if proposal_id and price:
    self.buy_contract(proposal_id, price)
