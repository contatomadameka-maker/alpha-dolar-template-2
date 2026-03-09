"""
ALPHA DOLAR 2.0 - ML Addon
Adiciona suporte a Machine Learning no IA Avançado
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MLStrategy:
    """Estratégia usando Machine Learning"""

    def __init__(self, model_path: str = None):
        self.model_path = model_path or 'models/rf_predictor.pkl'
        self.ml_predictor = None
        self.ml_enabled = False

        # Tenta carregar modelo
        self.load_model()

    def load_model(self):
        """Carrega modelo treinado"""
        try:
            from ml import MLPredictor

            model_file = Path(self.model_path)

            if model_file.exists():
                self.ml_predictor = MLPredictor()
                self.ml_predictor.load(str(model_file))
                self.ml_enabled = True

                print(f"✅ Modelo ML carregado!")
                print(f"   Tipo: {self.ml_predictor.model_type}")
                print(f"   Acurácia: {self.ml_predictor.accuracy:.2%}")
            else:
                print(f"⚠️ Modelo não encontrado: {model_file}")
                print(f"   Execute: python3 scripts/train_ml.py")
                self.ml_enabled = False

        except Exception as e:
            print(f"⚠️ Erro ao carregar ML: {e}")
            self.ml_enabled = False

    def analyze(self, ticks, config):
        """Analisa usando ML"""
        if not self.ml_enabled:
            return {
                'should_trade': False,
                'reason': 'ML não disponível'
            }

        try:
            from ml import prepare_features

            # Prepara features
            features = prepare_features(ticks, window_size=10)

            if features is None:
                return {
                    'should_trade': False,
                    'reason': 'Dados insuficientes para ML'
                }

            # Prediz
            prediction, confidence = self.ml_predictor.predict_even_odd(features)

            if prediction is None:
                return {
                    'should_trade': False,
                    'reason': 'Erro na predição ML'
                }

            # Determina tipo de contrato baseado na predição
            contract_type = config.get('contract_type', 'DIGITEVEN')

            # Se predição bate com o tipo configurado
            should_trade = False

            if contract_type == 'DIGITEVEN' and prediction == 'EVEN':
                should_trade = True
            elif contract_type == 'DIGITODD' and prediction == 'ODD':
                should_trade = True

            return {
                'should_trade': should_trade,
                'contract_type': contract_type,
                'confidence': confidence,
                'reason': f'ML prediz: {prediction} (conf: {confidence:.1%})',
                'ml_prediction': prediction
            }

        except Exception as e:
            print(f"❌ Erro no ML: {e}")
            return {
                'should_trade': False,
                'reason': f'Erro: {e}'
            }

    def get_info(self):
        """Info sobre ML"""
        if self.ml_enabled and self.ml_predictor:
            return self.ml_predictor.get_info()
        return {'ml_enabled': False}


# Função helper para usar no bot
def create_ml_strategy(model_path=None):
    """Cria estratégia ML"""
    return MLStrategy(model_path=model_path)


# Função para integrar no ia_avancado_real.py
def integrate_ml_into_bot(bot_instance):
    """
    Integra ML no bot existente

    Uso:
        bot = IAAvancadoReal()
        integrate_ml_into_bot(bot)
        bot.menu_principal()
    """
    # Adiciona estratégia ML
    bot_instance.ml_strategy = create_ml_strategy()

    # Salva método original
    original_analise_veloz = bot_instance.analise_veloz

    # Sobrescreve para usar ML se disponível
    def analise_com_ml(ticks):
        # Tenta usar ML primeiro
        if bot_instance.ml_strategy.ml_enabled:
            decision = bot_instance.ml_strategy.analyze(ticks, bot_instance.config)

            # Se ML não quis operar, usa estratégia original
            if not decision.get('should_trade'):
                return original_analise_veloz(ticks)

            return decision
        else:
            # Sem ML, usa estratégia original
            return original_analise_veloz(ticks)

    # Substitui método
    bot_instance.analise_veloz = analise_com_ml

    print("✅ ML integrado ao bot!")
    if bot_instance.ml_strategy.ml_enabled:
        print(f"   Modelo: {bot_instance.ml_strategy.ml_predictor.model_type}")
        print(f"   Acurácia: {bot_instance.ml_strategy.ml_predictor.accuracy:.2%}")
    else:
        print("   ⚠️ ML não disponível, usando estratégias padrão")


if __name__ == "__main__":
    # Teste
    print("=" * 60)
    print("TESTE ML STRATEGY")
    print("=" * 60)

    # Cria estratégia
    ml_strategy = create_ml_strategy()

    if ml_strategy.ml_enabled:
        # Ticks de teste
        ticks = [10000 + i * 0.5 for i in range(20)]

        config = {'contract_type': 'DIGITEVEN'}

        # Analisa
        decision = ml_strategy.analyze(ticks, config)

        print(f"\n📊 Decisão ML:")
        print(f"   Operar: {decision['should_trade']}")
        print(f"   Confiança: {decision.get('confidence', 0):.2%}")
        print(f"   Motivo: {decision['reason']}")
    else:
        print("\n⚠️ ML não disponível")
        print("   Execute: python3 scripts/train_ml.py")

    print("\n✅ Teste concluído!")