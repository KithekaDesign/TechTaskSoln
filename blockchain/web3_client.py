import json
import os
from pathlib import Path
from web3 import Web3

ABI_PATH = Path(__file__).resolve().parent / 'abi' / 'TechTaskEscrow.json'

def get_web3():
    rpc_url = os.environ.get('ETHEREUM_RPC_URL')
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum node.")
    return w3

def get_contract():
    w3 = get_web3()
    with open(ABI_PATH) as f:
        artifact = json.load(f)
    abi = artifact['abi']
    address = Web3.to_checksum_address(os.environ.get('CONTRACT_ADDRESS'))
    return w3.eth.contract(address=address, abi=abi)

def get_escrow_status(project_id: str) -> dict:
    """Read escrow state from blockchain for a given project ID."""
    try:
        contract = get_contract()
        result = contract.functions.getEscrow(project_id).call()
        status_map = {0: 'EMPTY', 1: 'FUNDED', 2: 'RELEASED', 3: 'REFUNDED', 4: 'DISPUTED'}
        return {
            'client': result[0],
            'freelancer': result[1],
            'amount_wei': result[2],
            'amount_eth': float(Web3.from_wei(result[2], 'ether')),
            'status': status_map.get(result[3], 'UNKNOWN'),
            'created_at': result[4],
        }
    except Exception as e:
        return {'error': str(e)}