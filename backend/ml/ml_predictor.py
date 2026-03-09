"""
ALPHA DOLAR 2.0 - ML Model
Modelo de Machine Learning para predição de dígitos
Random Forest + XGBoost
"""

import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np


class MLPredictor:
    """Preditor usando Machine Learning"""

    def __init__(self, model_type: str = 'random_forest'):
        """
        Args:
            model_type: 'random_forest' ou 'xgboost'
        """
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.accuracy = 0.0
        self.training_date = None
        self.feature_importance = None

    def train(self, X: List, y: List, test_size: float = 0.2):
        """
        Treina o modelo

        Args:
            X: Features (janelas de dígitos)
            y: Labels (próximo dígito ou par/ímpar)
            test_size: Porcentagem para teste
        """
        print("\n" + "=" * 60)
        print("🧠 TREINANDO MODELO DE MACHINE LEARNING")
        print("=" * 60)

        # Converte para numpy
        X = np.array(X)
        y = np.array(y)

        print(f"📊 Dataset: {len(X)} amostras, {X.shape[1]} features")

        # Split train/test
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            print(f"🔀 Train: {len(X_train)} | Test: {len(X_test)}")

            # Treina modelo
            if self.model_type == 'random_forest':
                print("🌲 Treinando Random Forest...")
                from sklearn.ensemble import RandomForestClassifier

                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            else:  # xgboost
                print("🚀 Treinando XGBoost...")
                import xgboost as xgb

                self.model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )

            # Treina
            start_time = datetime.now()
            self.model.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()

            # Avalia
            y_pred = self.model.predict(X_test)
            self.accuracy = accuracy_score(y_test, y_pred)

            # Feature importance
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_

            self.is_trained = True
            self.training_date = datetime.now()

            print(f"\n✅ MODELO TREINADO!")
            print(f"⏱️  Tempo: {training_time:.2f}s")
            print(f"🎯 Acurácia: {self.accuracy:.2%}")

            # Relatório detalhado
            print(f"\n📊 Relatório de Classificação:")
            print(classification_report(y_test, y_pred))

            return self.accuracy

        except ImportError as e:
            print(f"❌ Erro: Bibliotecas de ML não instaladas!")
            print(f"   Instale: pip install scikit-learn xgboost --break-system-packages")
            return 0.0
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            return 0.0

    def predict(self, features: List) -> Tuple[int, float]:
        """
        Faz predição

        Args:
            features: Lista de features (janela de dígitos)

        Returns:
            (predição, confiança)
        """
        if not self.is_trained:
            return None, 0.0

        try:
            # Converte para numpy
            X = np.array([features])

            # Prediz
            prediction = self.model.predict(X)[0]

            # Confiança (probabilidade)
            if hasattr(self.model, 'predict_proba'):
                probas = self.model.predict_proba(X)[0]
                confidence = float(max(probas))
            else:
                confidence = 0.7  # Padrão

            return int(prediction), confidence

        except Exception as e:
            print(f"❌ Erro na predição: {e}")
            return None, 0.0

    def predict_even_odd(self, features: List) -> Tuple[str, float]:
        """
        Prediz se próximo será par ou ímpar

        Returns:
            ('EVEN' ou 'ODD', confiança)
        """
        prediction, confidence = self.predict(features)

        if prediction is None:
            return None, 0.0

        # Se modelo foi treinado para dígitos
        if prediction < 10:
            is_even = prediction % 2 == 0
        else:  # Modelo binário (0=ímpar, 1=par)
            is_even = prediction == 1

        return 'EVEN' if is_even else 'ODD', confidence

    def save(self, filename: str):
        """Salva modelo"""
        if not self.is_trained:
            print("⚠️ Modelo não treinado!")
            return

        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'accuracy': self.accuracy,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'feature_importance': self.feature_importance.tolist() if self.feature_importance is not None else None
        }

        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"💾 Modelo salvo em: {filename}")

    def load(self, filename: str):
        """Carrega modelo"""
        try:
            with open(filename, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.accuracy = model_data['accuracy']
            self.training_date = datetime.fromisoformat(model_data['training_date']) if model_data['training_date'] else None
            self.feature_importance = np.array(model_data['feature_importance']) if model_data['feature_importance'] else None
            self.is_trained = True

            print(f"✅ Modelo carregado!")
            print(f"   Tipo: {self.model_type}")
            print(f"   Acurácia: {self.accuracy:.2%}")
            print(f"   Treinado em: {self.training_date}")

        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")

    def get_info(self) -> Dict:
        """Informações do modelo"""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'accuracy': self.accuracy,
            'training_date': self.training_date.isoformat() if self.training_date else None
        }


def prepare_features(ticks: List[float], window_size: int = 10) -> List:
    """
    Prepara features para predição

    Args:
        ticks: Lista dos últimos ticks
        window_size: Tamanho da janela

    Returns:
        Lista de features
    """
    if len(ticks) < window_size:
        return None

    # Extrai últimos dígitos
    recent_ticks = ticks[-window_size:]
    digits = [int(str(float(t)).replace('.', '')[-1]) for t in recent_ticks]

    # Features básicas
    features = digits.copy()

    # Features extras
    even_count = sum(1 for d in digits if d % 2 == 0)
    odd_count = len(digits) - even_count
    features.append(even_count)
    features.append(odd_count)

    # Últimos 3 (mais peso)
    features.extend(digits[-3:])

    return features


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO MODELO ML")
    print("=" * 60)

    # Simula dados de treinamento
    print("\n📊 Gerando dados de teste...")
    import random

    # Simula 1000 amostras
    X = []
    y = []

    for i in range(1000):
        # Janela de 10 dígitos aleatórios
        window = [random.randint(0, 9) for _ in range(10)]

        # Features extras
        even_count = sum(1 for d in window if d % 2 == 0)
        odd_count = len(window) - even_count
        features = window + [even_count, odd_count] + window[-3:]

        # Label: próximo dígito (simulado com lógica)
        # Se mais pares, próximo será ímpar (correção)
        if even_count > odd_count:
            label = random.choice([1, 3, 5, 7, 9])
        else:
            label = random.choice([0, 2, 4, 6, 8])

        X.append(features)
        y.append(label)

    # Treina
    predictor = MLPredictor(model_type='random_forest')
    accuracy = predictor.train(X, y)

    # Testa predição
    print("\n🧪 TESTANDO PREDIÇÕES:")
    test_features = [5, 2, 7, 8, 1, 4, 6, 3, 9, 2, 4, 6, 2, 3, 9]
    prediction, confidence = predictor.predict(test_features)
    print(f"   Predição: {prediction}")
    print(f"   Confiança: {confidence:.2%}")

    # Prediz par/ímpar
    result, conf = predictor.predict_even_odd(test_features)
    print(f"   Par/Ímpar: {result} ({conf:.2%})")

    print("\n✅ Teste concluído!")