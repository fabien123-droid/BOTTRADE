# 🚀 Agent de Trading Scalping Multi-Utilisateur Intelligent

Ce projet est un bot Telegram de trading automatique optimisé pour le scalping, utilisant l'IA **DeepSeek-R1** via Groq pour la validation des signaux. Il est conçu pour être déployé gratuitement sur **Vercel** en utilisant des fonctions serverless.

## 🛠 Architecture Technique

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Framework** | FastAPI (Python) | Gestion des requêtes Webhook et API |
| **Hébergement** | Vercel | Déploiement Serverless gratuit |
| **Base de Données** | Supabase (PostgreSQL) | Stockage des utilisateurs et clés API |
| **Intelligence Artificielle** | Groq (DeepSeek-R1) | Analyse et décision finale de trading |
| **Trading** | CCXT | Connexion aux exchanges (Binance/Bybit) |
| **Sécurité** | AES-256 | Chiffrement des clés API sensibles |

## 📋 Prérequis

1.  **Telegram** : Créez un bot via [@BotFather](https://t.me/botfather) pour obtenir votre `TELEGRAM_TOKEN`.
2.  **Groq** : Obtenez une clé API sur [Groq Cloud](https://console.groq.com/).
3.  **Supabase** : Créez un projet et récupérez l'URL et la clé API.
4.  **Vercel** : Un compte pour le déploiement.

## 🚀 Instructions de Déploiement

### 1. Configuration de la Base de Données
Exécutez le script `schema.sql` fourni dans l'éditeur SQL de votre tableau de bord Supabase pour initialiser les tables nécessaires.

### 2. Variables d'Environnement
Configurez les variables suivantes dans les paramètres de votre projet Vercel :

*   `TELEGRAM_TOKEN` : Token de votre bot Telegram.
*   `SUPABASE_URL` : URL de votre projet Supabase.
*   `SUPABASE_KEY` : Clé API Supabase.
*   `GROQ_API_KEY` : Clé API Groq.
*   `ENCRYPTION_KEY` : Une chaîne de 32 caractères pour le chiffrement AES.

### 3. Déploiement sur Vercel
Poussez le code sur un dépôt GitHub et connectez-le à Vercel. Le fichier `vercel.json` s'occupera de la configuration automatique.

### 4. Configuration du Webhook
Une fois déployé, définissez l'URL du webhook Telegram en ouvrant cette URL dans votre navigateur :
`https://api.telegram.org/bot<VOTRE_TOKEN>/setWebhook?url=https://<VOTRE_URL_VERCEL>/webhook`

## 🛡 Sécurité
Les clés API des utilisateurs sont chiffrées avant d'être stockées dans Supabase. Seule votre instance de bot possédant la `ENCRYPTION_KEY` peut les déchiffrer pour exécuter des trades.

## 📈 Stratégie de Trading
Le bot scanne le Top 20 des volumes sur Binance. Il calcule le RSI et les Bandes de Bollinger sur des unités de temps de 1m et 5m. Les données sont ensuite envoyées à DeepSeek-R1 qui valide si une opportunité de scalping est présente.
