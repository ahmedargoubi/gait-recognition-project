# Registre des Traitements — GAIT·ID

**Référence :** REG-TRAIT-001 | **Version :** 1.0 — Mai 2026  
**Responsable de traitement :** Ahmed (Étudiant — Projet académique)  
**Base légale :** RGPD Art. 30 — Obligation de tenue d'un registre

---

## 1. Traitement Principal — Identification Biométrique par Démarche

### 1.1 Identification du traitement

| Champ | Valeur |
|---|---|
| **Nom du traitement** | GAIT·ID — Reconnaissance biométrique de la démarche |
| **Responsable de traitement** | Ahmed (étudiant, prototype académique) |
| **Délégué à la protection des données (DPO)** | Non désigné (facultatif pour prototype) |
| **Date de création** | Mai 2026 |
| **Date de mise à jour** | Mai 2026 |

---

### 1.2 Finalités du traitement

**Finalité principale :** Identification d'une personne par analyse biométrique de sa démarche.

**Finalités secondaires :**
- Évaluation des performances du modèle d'IA
- Recherche académique sur la reconnaissance de démarche
- Démonstration de conformité RGPD et AI Act

**Finalités expressément interdites :**
- ❌ Surveillance continue ou tracking
- ❌ Profilage comportemental
- ❌ Croisement avec d'autres systèmes biométriques
- ❌ Usage commercial ou publicitaire

---

### 1.3 Base légale

**Base légale principale : Consentement explicite (Art. 6(1)(a) + Art. 9(2)(a) RGPD)**

Les données biométriques relèvent de l'**Art. 9 RGPD** (catégories particulières de données). Le consentement doit être :
- **Libre** : aucune contrainte, aucun accès conditionnel
- **Spécifique** : limité à l'identification par démarche
- **Éclairé** : notice explicative présentée avant validation
- **Univoque** : upload volontaire de vidéo = consentement actif

**Preuve du consentement :** Upload volontaire via l'interface web `templates/index.html` après affichage de la notice.

---

### 1.4 Catégories de personnes concernées

| Catégorie | Description | Nombre estimé |
|---|---|---|
| Volontaires enrôlés | Personnes ayant fourni une vidéo de marche pour enrôlement | 5 (prototype) |
| Utilisateurs testés | Personnes uploadant une vidéo pour identification | ~10 (tests) |

**Critères d'inclusion :**
- Adultes consentants (≥18 ans)
- Capacité de marcher sans aide
- Consentement explicite documenté

**Critères d'exclusion :**
- Mineurs (<18 ans)
- Personnes vulnérables sans représentant légal
- Absence de consentement

---

### 1.5 Catégories de données traitées

| Catégorie de données | Type RGPD | Description technique | Conservation |
|---|---|---|---|
| **Vidéo de marche** | Art. 9 — Biométrique | Fichier MP4 uploadé (5-10 sec) | Non stockée (mémoire uniquement) |
| **Vecteur biométrique 128D** | Art. 9 — Biométrique | Empreinte de démarche chiffrée AES-256 | 180 jours max |
| **Pseudonyme PSE-XXXX** | Pseudonymisé | Hash SHA-256 de l'identité civile | 180 jours max |
| **Logs d'accès** | Ordinaire | Date, heure, action, résultat | 90 jours max |

**Données NON collectées (Privacy by Design) :**
- ❌ Visage (MediaPipe Pose ignore le visage)
- ❌ Adresse IP complète (pseudonymisée)
- ❌ Localisation géographique
- ❌ Historique de navigation
- ❌ Identité civile en clair

---

### 1.6 Destinataires des données

| Destinataire | Type | Données partagées | Base légale |
|---|---|---|---|
| **Système GAIT·ID** | Interne | Vecteur 128D chiffré | Finalité principale |
| **Logs système** | Interne | Pseudonyme + action | Sécurité et traçabilité |

**Aucun transfert à des tiers.**  
**Aucun transfert international.**

---

### 1.7 Transferts hors UE

**Aucun transfert hors Union Européenne.**

Toutes les données sont stockées localement sur le serveur de développement :
- Localisation : `C:\Users\ahmed\Downloads\gait-recognition-project\`
- Pays : Tunisie
- Garanties : Chiffrement local AES-256-GCM

---

### 1.8 Durées de conservation

| Donnée | Durée | Justification | Purge |
|---|---|---|---|
| Vecteur biométrique | 180 jours | Durée du projet académique | Automatique (champ `expires_at`) |
| Logs d'accès | 90 jours | Traçabilité sécurité | Rotation automatique |
| Vidéo uploadée | 0 jour | Non stockée | Suppression immédiate après traitement |

**Politique de purge :**
- Les vecteurs expirent automatiquement après 180 jours
- Notification à la personne concernée 30 jours avant expiration
- Suppression définitive et irréversible (pas de sauvegarde)

---

### 1.9 Mesures de sécurité

| Domaine | Mesure | Technologie |
|---|---|---|
| **Chiffrement au repos** | AES-256-GCM | `src/security.py` (cryptography) |
| **Chiffrement en transit** | TLS 1.3 | Flask HTTPS |
| **Authentification** | JWT HS256 (15 min) | `flask-jwt-extended` |
| **Contrôle d'accès** | RBAC (4 rôles) | Défini, non implémenté (prototype) |
| **Pseudonymisation** | Hash SHA-256 unidirectionnel | `src/security.py` |
| **Logs** | Horodatage + HMAC (planifié) | `logs/api.log` |
| **Rate limiting** | 10 req/min/IP | Planifié (pas implémenté) |

**Analyse d'impact (DPIA) :** Réalisée — voir `docs/DPIA.md`

---

### 1.10 Droits des personnes concernées

| Droit RGPD | Endpoint API | Délai de réponse | Statut |
|---|---|---|---|
| **Droit d'accès (Art. 15)** | `GET /admin/subject/{id}` | 1 mois | ⚠️ Non exposé |
| **Droit de rectification (Art. 16)** | `POST /admin/re-enroll/{id}` | Immédiat | ✅ Implémenté |
| **Droit à l'effacement (Art. 17)** | `DELETE /admin/subject/{id}` | Immédiat | ⚠️ Non exposé |
| **Droit à la limitation (Art. 18)** | Flag `processing_paused` | 1 mois | ❌ Non implémenté |
| **Droit à la portabilité (Art. 20)** | Export JSON du vecteur | 1 mois | ❌ Non implémenté |
| **Droit d'opposition (Art. 21)** | Retrait consentement = suppression | Immédiat | ⚠️ Non exposé |

**Procédure de demande :** Contact par email (simulé pour prototype académique).

---

## 2. Sous-Traitants

**Aucun sous-traitant.**

Toutes les opérations sont effectuées localement par le système GAIT·ID :
- Hébergement : local (PC de développement)
- Stockage : local (dossier `data/`)
- Traitement : local (Flask + PyTorch)

**Aucune clause de sous-traitance (Art. 28 RGPD) nécessaire.**

---

## 3. Violations de Données Personnelles

### 3.1 Procédure de notification

**Délai de notification CNIL : 72 heures (Art. 33 RGPD)**

| Étape | Action | Délai |
|---|---|---|
| 1. Détection | Monitoring logs + alertes système | Temps réel |
| 2. Containment | Isolation du système compromis | < 1 heure |
| 3. Investigation | Analyse de l'incident | < 24 heures |
| 4. Notification CNIL | Formulaire en ligne | < 72 heures |
| 5. Notification personnes | Email si risque élevé | < 72 heures |

### 3.2 Scénarios de violation

| Scénario | Probabilité | Impact | Mesures préventives |
|---|---|---|---|
| Fuite de vecteurs chiffrés | Très faible | Faible | AES-256-GCM résistant |
| Accès non autorisé à la BDD | Faible | Élevé | JWT + rate limiting |
| Perte de la clé de chiffrement | Faible | Très élevé | Backup clé hors ligne |

### 3.3 Registre des violations

| Date | Type | Impact | Mesures | Notification |
|---|---|---|---|---|
| — | Aucune violation à ce jour | — | — | — |

---

## 4. Analyse d'Impact (DPIA)

**Statut DPIA : Réalisée (obligatoire Art. 35 RGPD)**

| Élément | Document | Conclusion |
|---|---|---|
| DPIA complète | `docs/DPIA.md` | Risque résiduel FAIBLE |
| Consultation autorité | Non requise (Art. 36 non déclenché) | N/A |
| Révision prévue | Mai 2027 ou modification majeure | Planifiée |

**Risque global après mesures : FAIBLE**  
**Décision : PROCÉDER avec les mesures identifiées**

---

## 5. Responsabilités (Matrice RACI)

### 5.1 Rôles définis

| Rôle | Personne | Responsabilités |
|---|---|---|
| **Responsable de traitement** | Ahmed | Conformité RGPD, décisions traitement |
| **Développeur IA** | Ahmed | Modèle CNN, feature engineering |
| **Administrateur sécurité** | Ahmed | Chiffrement, logs, accès |
| **Auditeur conformité** | Encadreur académique | Revue DPIA, validation juridique |

### 5.2 Matrice RACI — Activités clés

| Activité | Responsable | Approbateur | Consulté | Informé |
|---|---|---|---|---|
| **Enrôlement nouvelle personne** | Ahmed | Ahmed | — | Personne concernée |
| **Identification biométrique** | Système | Ahmed | — | Personne testée |
| **Modification DPIA** | Ahmed | Encadreur | DPD (si désigné) | — |
| **Réponse demande RGPD** | Ahmed | — | DPD (si désigné) | Personne concernée |
| **Notification violation** | Ahmed | Encadreur | CNIL | Personnes concernées |
| **Purge données expirées** | Système (cron) | Ahmed | — | — |

---

## 6. Documentation Associée

| Document | Fichier | Description |
|---|---|---|
| DPIA complète | `docs/DPIA.md` | Analyse d'impact Art. 35 RGPD |
| Classification AI Act | `docs/AI_Act_classification.md` | Système d'IA à haut risque |
| Mapping ISO | `docs/ISO_mapping.md` | ISO 29100 + ISO 27701 |
| Politique PII | `README.md` | Engagement protection vie privée |
| Architecture technique | `src/model_pose.py` | CNN GaitPoseCNN |
| Procédures sécurité | `src/security.py` | Chiffrement AES-256-GCM |

---

## 7. Historique des Modifications

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 02/05/2026 | Ahmed | Création initiale — prototype MediaPipe Pose |

---

## 8. Validation

| Rôle | Nom | Signature | Date |
|---|---|---|---|
| Responsable de traitement | Ahmed | [Signature électronique] | 02/05/2026 |
| Encadreur académique | [Nom] | [À compléter] | [À compléter] |

---

**Prochaine révision : Mai 2027 ou avant toute modification substantielle du traitement.**

---

*Registre conforme à l'Art. 30 RGPD — Fait à Tunis, le 2 mai 2026*