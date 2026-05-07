/**
 * TechTaskSoln — Blockchain / MetaMask Integration
 * Handles wallet connection, escrow funding, release, refund, and dispute.
 */

const CONTRACT_ADDRESS = '0x299823DD8cE0003F88383E2e75bBc34e426C5435';

const CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "projectId", "type": "string"},
            {"internalType": "address", "name": "freelancer", "type": "address"}
        ],
        "name": "fundEscrow",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "projectId", "type": "string"}],
        "name": "releaseFunds",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "projectId", "type": "string"}],
        "name": "refundClient",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "projectId", "type": "string"}],
        "name": "raiseDispute",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "projectId", "type": "string"}],
        "name": "getEscrow",
        "outputs": [
            {"internalType": "address", "name": "client", "type": "address"},
            {"internalType": "address", "name": "freelancer", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "uint8", "name": "status", "type": "uint8"},
            {"internalType": "uint256", "name": "createdAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
];

const ESCROW_STATUS = {
    0: 'EMPTY',
    1: 'FUNDED',
    2: 'RELEASED',
    3: 'REFUNDED',
    4: 'DISPUTED'
};

/* ── Wallet connection ── */
async function connectWallet() {
    if (typeof window.ethereum === 'undefined') {
        showAlert('MetaMask is not installed. Please install it from metamask.io', 'error');
        return null;
    }
    try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        await switchToSepolia();
        return accounts[0];
    } catch (err) {
        showAlert('Wallet connection rejected.', 'error');
        return null;
    }
}

async function getConnectedWallet() {
    if (typeof window.ethereum === 'undefined') return null;
    const accounts = await window.ethereum.request({ method: 'eth_accounts' });
    return accounts.length > 0 ? accounts[0] : null;
}

async function switchToSepolia() {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0xaa36a7' }]  // Sepolia chain ID
        });
    } catch (err) {
        if (err.code === 4902) {
            await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [{
                    chainId: '0xaa36a7',
                    chainName: 'Sepolia test network',
                    nativeCurrency: { name: 'SepoliaETH', symbol: 'ETH', decimals: 18 },
                    rpcUrls: ['https://rpc.sepolia.org'],
                    blockExplorerUrls: ['https://sepolia.etherscan.io']
                }]
            });
        }
    }
}

/* ── Get contract instance ── */
async function getContract() {
    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    return new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);
}

/* ── Fund escrow (client pays) ── */
async function fundEscrow(projectId, freelancerWallet, amountEth) {
    try {
        const wallet = await connectWallet();
        if (!wallet) return null;

        const contract = await getContract();
        const amountWei = ethers.parseEther(amountEth.toString());

        showAlert('Confirm the transaction in MetaMask...', 'info');

        const tx = await contract.fundEscrow(projectId, freelancerWallet, { value: amountWei });
        showAlert('Transaction submitted. Waiting for confirmation...', 'info');

        const receipt = await tx.wait();
        showAlert('Escrow funded successfully!', 'success');

        // Sync with Django backend
        await syncEscrowStatus(projectId, receipt.hash, 'funded');
        return receipt;

    } catch (err) {
        showAlert(`Transaction failed: ${err.reason || err.message}`, 'error');
        return null;
    }
}

/* ── Release funds (client approves work) ── */
async function releaseFunds(projectId) {
    try {
        const wallet = await connectWallet();
        if (!wallet) return null;

        const contract = await getContract();
        showAlert('Confirm the release in MetaMask...', 'info');

        const tx = await contract.releaseFunds(projectId);
        showAlert('Waiting for confirmation...', 'info');

        const receipt = await tx.wait();
        showAlert('Funds released to freelancer!', 'success');

        await syncEscrowStatus(projectId, receipt.hash, 'released');
        return receipt;

    } catch (err) {
        showAlert(`Release failed: ${err.reason || err.message}`, 'error');
        return null;
    }
}

/* ── Refund client ── */
async function refundClient(projectId) {
    try {
        const wallet = await connectWallet();
        if (!wallet) return null;

        const contract = await getContract();
        showAlert('Confirm the refund in MetaMask...', 'info');

        const tx = await contract.refundClient(projectId);
        const receipt = await tx.wait();
        showAlert('Refund successful!', 'success');

        await syncEscrowStatus(projectId, receipt.hash, 'refunded');
        return receipt;

    } catch (err) {
        showAlert(`Refund failed: ${err.reason || err.message}`, 'error');
        return null;
    }
}

/* ── Raise dispute ── */
async function raiseDispute(projectId) {
    try {
        const wallet = await connectWallet();
        if (!wallet) return null;

        const contract = await getContract();
        showAlert('Submitting dispute...', 'info');

        const tx = await contract.raiseDispute(projectId);
        const receipt = await tx.wait();
        showAlert('Dispute raised. Platform admin will review.', 'success');

        await syncEscrowStatus(projectId, receipt.hash, 'disputed');
        return receipt;

    } catch (err) {
        showAlert(`Dispute failed: ${err.reason || err.message}`, 'error');
        return null;
    }
}

/* ── Read escrow status from blockchain directly ── */
async function getEscrowStatus(projectId) {
    try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);
        const result = await contract.getEscrow(projectId);
        return {
            client: result[0],
            freelancer: result[1],
            amountEth: parseFloat(ethers.formatEther(result[2])),
            status: ESCROW_STATUS[Number(result[3])] || 'UNKNOWN',
            createdAt: new Date(Number(result[4]) * 1000).toLocaleString()
        };
    } catch (err) {
        return null;
    }
}

/* ── Sync transaction result to Django backend ── */
async function syncEscrowStatus(projectId, txHash, txType) {
    try {
        const res = await apiCall(`/blockchain/escrow/${projectId}/sync_status/`, 'POST', {
            tx_hash: txHash,
            tx_type: txType
        });
        if (res && res.ok) {
            console.log('Escrow status synced with backend.');
        }
    } catch (err) {
        console.warn('Failed to sync escrow status with backend:', err);
    }
}

/* ── Render escrow panel on project workspace page ── */
async function renderEscrowPanel(projectId, userRole, freelancerWallet, budgetEth) {
    const panel = document.getElementById('escrow-panel');
    if (!panel) return;

    const wallet = await getConnectedWallet();
    const chainStatus = wallet ? await getEscrowStatus(String(projectId)) : null;
    const escrowStatus = chainStatus ? chainStatus.status : 'EMPTY';

    let html = `
        <div style="border:1px solid var(--color-border-tertiary);border-radius:12px;padding:1.25rem;margin-top:1rem;">
            <h3 style="font-size:16px;font-weight:500;margin:0 0 12px;">Escrow Payment</h3>
    `;

    if (!wallet) {
        html += `
            <p style="color:var(--color-text-secondary);font-size:14px;margin:0 0 12px;">
                Connect your MetaMask wallet to manage escrow payments.
            </p>
            <button onclick="connectWallet().then(()=>renderEscrowPanel(${projectId},'${userRole}','${freelancerWallet}',${budgetEth}))"
                style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;">
                Connect Wallet
            </button>
        `;
    } else {
        html += `
            <p style="font-size:13px;color:var(--color-text-secondary);margin:0 0 8px;">
                Wallet: ${wallet.slice(0,6)}...${wallet.slice(-4)}
            </p>
            <p style="font-size:13px;margin:0 0 16px;">
                Status: <strong>${escrowStatus}</strong>
                ${chainStatus ? `&nbsp;·&nbsp; Amount: ${chainStatus.amountEth} ETH` : ''}
            </p>
        `;

        if (userRole === 'client') {
            if (escrowStatus === 'EMPTY') {
                html += `
                    <button onclick="fundEscrow('${projectId}','${freelancerWallet}',${budgetEth})"
                        style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;margin-right:8px;">
                        Fund Escrow (${budgetEth} ETH)
                    </button>
                `;
            } else if (escrowStatus === 'FUNDED') {
                html += `
                    <button onclick="releaseFunds('${projectId}')"
                        style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;margin-right:8px;">
                        Release Funds
                    </button>
                    <button onclick="refundClient('${projectId}')"
                        style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;margin-right:8px;">
                        Refund Me
                    </button>
                    <button onclick="raiseDispute('${projectId}')"
                        style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;">
                        Raise Dispute
                    </button>
                `;
            }
        } else if (userRole === 'freelancer') {
            if (escrowStatus === 'FUNDED') {
                html += `
                    <p style="font-size:13px;color:var(--color-text-secondary);">
                        Payment is secured in escrow. It will be released when the client approves your work.
                    </p>
                    <button onclick="raiseDispute('${projectId}')"
                        style="padding:8px 16px;border-radius:8px;border:1px solid var(--color-border-secondary);background:transparent;cursor:pointer;font-size:14px;">
                        Raise Dispute
                    </button>
                `;
            } else if (escrowStatus === 'RELEASED') {
                html += `<p style="color:var(--color-text-success);font-size:14px;">Payment has been released to your wallet.</p>`;
            }
        }
    }

    if (escrowStatus !== 'EMPTY' && chainStatus) {
        html += `
            <p style="font-size:12px;color:var(--color-text-tertiary);margin-top:12px;">
                <a href="https://sepolia.etherscan.io/address/${CONTRACT_ADDRESS}" target="_blank"
                   style="color:var(--color-text-info);">View contract on Etherscan</a>
            </p>
        `;
    }

    html += `</div>`;
    panel.innerHTML = html;
}