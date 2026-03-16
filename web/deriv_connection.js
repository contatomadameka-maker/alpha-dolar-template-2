/**
 * ALPHA DOLAR 2.0 - Sistema de Conexão Deriv Persistente
 * Gerencia conexão WebSocket com Deriv que persiste entre páginas
 */

class DerivConnection {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.accountType = 'demo';
        this.balance = 0;
        this.currency = 'USD';
        this.loginId = '';
        this.email = '';
        this.token = '';
        this.tradeHistory = [];
        this.activeContract = null;
    }

    // =====================================================
    // PERSISTÊNCIA
    // =====================================================

    loadSavedConnection() {
        const saved = localStorage.getItem('derivConnection');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                this.token = data.token;
                this.accountType = data.accountType;
                this.balance = data.balance || 0;
                this.currency = data.currency || 'USD';
                this.loginId = data.loginId || '';
                this.email = data.email || '';
                return true;
            } catch (e) {
                console.error('Erro ao carregar conexão salva:', e);
                return false;
            }
        }
        return false;
    }

    saveConnection() {
        const data = {
            token: this.token,
            accountType: this.accountType,
            balance: this.balance,
            currency: this.currency,
            loginId: this.loginId,
            email: this.email,
            timestamp: Date.now()
        };
        localStorage.setItem('derivConnection', JSON.stringify(data));
    }

    clearConnection() {
        localStorage.removeItem('derivConnection');
        this.token = '';
        this.isConnected = false;
    }

    // =====================================================
    // HISTÓRICO DE TRADES
    // =====================================================

    loadTradeHistory() {
        const saved = localStorage.getItem('tradeHistory');
        if (saved) {
            try {
                this.tradeHistory = JSON.parse(saved);
            } catch (e) {
                this.tradeHistory = [];
            }
        }
    }

    saveTradeHistory() {
        // Mantém apenas últimos 100 trades
        if (this.tradeHistory.length > 100) {
            this.tradeHistory = this.tradeHistory.slice(-100);
        }
        localStorage.setItem('tradeHistory', JSON.stringify(this.tradeHistory));
    }

    addTradeToHistory(trade) {
        this.tradeHistory.unshift({
            ...trade,
            timestamp: Date.now()
        });
        this.saveTradeHistory();

        // Dispara evento
        window.dispatchEvent(new CustomEvent('tradeHistoryUpdated', {
            detail: this.tradeHistory
        }));
    }

    // =====================================================
    // CONEXÃO
    // =====================================================

    async connect(token, accountType = 'demo') {
        this.token = token;
        this.accountType = accountType;

        const app_id = '1089'; // App ID público Deriv
        const ws_url = `wss://ws.derivws.com/websockets/v3?app_id=${app_id}`;

        this.ws = new WebSocket(ws_url);

        return new Promise((resolve, reject) => {
            this.ws.onopen = () => {
                console.log('✅ WebSocket conectado');
                this.ws.send(JSON.stringify({ authorize: token }));
            };

            this.ws.onmessage = (msg) => {
                const data = JSON.parse(msg.data);
                this.handleMessage(data, resolve, reject);
            };

            this.ws.onerror = (error) => {
                console.error('❌ Erro WebSocket:', error);
                reject(error);
            };

            this.ws.onclose = () => {
                console.log('🔌 WebSocket desconectado');
                this.isConnected = false;
                window.dispatchEvent(new Event('derivDisconnected'));
            };
        });
    }

    handleMessage(data, resolve = null, reject = null) {
        // Autorização
        if (data.authorize) {
            this.isConnected = true;
            this.balance = data.authorize.balance;
            this.currency = data.authorize.currency;
            this.loginId = data.authorize.loginid;
            this.email = data.authorize.email;
            this.saveConnection();

            console.log('✅ Autorizado:', this.loginId);

            if (resolve) resolve(data.authorize);

            window.dispatchEvent(new CustomEvent('derivConnected', {
                detail: data.authorize
            }));
        }

        // Erro
        if (data.error) {
            console.error('❌ Erro Deriv:', data.error);
            if (reject) reject(data.error);

            window.dispatchEvent(new CustomEvent('derivError', {
                detail: data.error
            }));
        }

        // Atualização de saldo
        if (data.balance) {
            this.balance = data.balance.balance;
            this.saveConnection();

            window.dispatchEvent(new CustomEvent('balanceUpdated', {
                detail: data.balance
            }));
        }

        // Compra (trade executado)
        if (data.buy) {
            console.log('✅ Trade executado:', data.buy);
            this.activeContract = data.buy.contract_id;

            window.dispatchEvent(new CustomEvent('tradeExecuted', {
                detail: data.buy
            }));
        }

        // Proposta (cotação)
        if (data.proposal) {
            window.dispatchEvent(new CustomEvent('proposalReceived', {
                detail: data.proposal
            }));
        }

        // Resultado do contrato
        if (data.proposal_open_contract) {
            const contract = data.proposal_open_contract;

            // Verifica se finalizou
            if (contract.is_sold || contract.status === 'sold') {
                const profit = contract.profit;
                const result = {
                    contractId: contract.contract_id,
                    profit: profit,
                    buyPrice: contract.buy_price,
                    sellPrice: contract.sell_price,
                    won: profit > 0,
                    direction: contract.contract_type,
                    symbol: contract.underlying,
                    entrySpot: contract.entry_tick,
                    exitSpot: contract.exit_tick
                };

                this.addTradeToHistory(result);

                window.dispatchEvent(new CustomEvent('contractFinished', {
                    detail: result
                }));
            }

            window.dispatchEvent(new CustomEvent('contractUpdate', {
                detail: contract
            }));
        }

        // Tick stream
        if (data.tick) {
            window.dispatchEvent(new CustomEvent('tickUpdate', {
                detail: data.tick
            }));
        }

        // Qualquer mensagem
        window.dispatchEvent(new CustomEvent('derivMessage', {
            detail: data
        }));
    }

    // =====================================================
    // DESCONEXÃO
    // =====================================================

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        this.clearConnection();
        this.isConnected = false;
        console.log('✅ Desconectado');
    }

    // =====================================================
    // TRADING
    // =====================================================

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
            return true;
        } else {
            console.error('❌ WebSocket não está conectado');
            return false;
        }
    }

    // Obter proposta (cotação)
    getProposal(params) {
        const message = {
            proposal: 1,
            amount: params.stake,
            basis: 'stake',
            contract_type: params.direction === 'rise' ? 'CALL' : 'PUT',
            currency: this.currency,
            duration: params.duration,
            duration_unit: params.durationUnit || 't',
            symbol: params.market
        };

        this.send(message);
    }

    // Executar trade
    async executeTrade(params) {
        if (!this.isConnected) {
            throw new Error('Não conectado à Deriv');
        }

        // Primeiro, pega a proposta
        return new Promise((resolve, reject) => {
            let proposalId = null;

            const proposalHandler = (event) => {
                const proposal = event.detail;
                if (proposal.id) {
                    proposalId = proposal.id;

                    // Compra usando a proposta
                    this.send({
                        buy: proposalId,
                        price: params.stake
                    });
                }
            };

            const buyHandler = (event) => {
                window.removeEventListener('proposalReceived', proposalHandler);
                window.removeEventListener('tradeExecuted', buyHandler);
                resolve(event.detail);
            };

            window.addEventListener('proposalReceived', proposalHandler);
            window.addEventListener('tradeExecuted', buyHandler);

            // Timeout de 10 segundos
            setTimeout(() => {
                window.removeEventListener('proposalReceived', proposalHandler);
                window.removeEventListener('tradeExecuted', buyHandler);
                reject(new Error('Timeout ao executar trade'));
            }, 10000);

            // Envia proposta
            this.getProposal(params);
        });
    }

    // Subscrever a ticks
    subscribeTicks(market) {
        this.send({
            ticks: market,
            subscribe: 1
        });
    }

    // Desinscrever de ticks
    unsubscribeTicks() {
        this.send({
            forget_all: 'ticks'
        });
    }

    // Obter histórico de ticks
    getTickHistory(market, count = 1000) {
        this.send({
            ticks_history: market,
            count: count,
            end: 'latest',
            style: 'ticks'
        });
    }
}

// =====================================================
// INSTÂNCIA GLOBAL
// =====================================================

if (typeof window !== 'undefined') {
    window.derivConn = new DerivConnection();

    // Carrega histórico ao inicializar
    window.derivConn.loadTradeHistory();

    console.log('✅ DerivConnection inicializado');
}