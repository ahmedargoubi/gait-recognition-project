# DPIA — Analyse d'Impact Relative à la Protection des Données
**Référence :** DPIA-GAIT-001 | **Version :** 1.0 — Mai 2026  
**Système :** GAIT·ID — Reconnaissance biométrique de la démarche  
**Base légale :** RGPD Art. 35 | **Conclusion : PROCÉDER AVEC LES MESURES IDENTIFIÉES**

---

## 1. Contexte et Description du Traitement

### 1.1 Contexte du projet

GAIT·ID est un prototype académique d'identification biométrique basé sur la reconnaissance de la démarche (*gait recognition*). Le système extrait des caractéristiques de marche depuis des vidéos, les encode en vecteurs 128D via un CNN (GaitPoseCNN + MediaPipe), et les stocke de manière chiffrée pour identification ultérieure.

### 1.2 Pipeline de traitement

1. **Acquisition** : vidéo MP4 uploadée via l'interface web Flask
2. **Prétraitement** : extraction de silhouettes MOG2 (OpenCV) — en mémoire uniquement
3. **Extraction de pose** : 33 landmarks squelettiques via MediaPipe PoseLandmarker
4. **Feature engineering** : 20 valeurs invariantes/frame (10 angles articulaires + 6 ratios de distances + 4 asymétries G/D) × 30 frames → vecteur 600D → 128D via CNN
5. **Identification** : similarité cosinus entre vecteur probe et base chiffrée
6. **Stockage** : templates AES-256-GCM, séparés des identités civiles

### 1.3 Données traitées

| Type de donnée | Catégorie RGPD | Traitement |
|---|---|---|
| Vidéo de marche | **Art. 9 — Biométrique** | Lecture seule — non stockée |
| Silhouettes intermédiaires | Dérivée biométrique | En mémoire uniquement |
| Vecteur de features 128D | **Art. 9 — Biométrique** | Stocké chiffré AES-256-GCM |
| Identifiant civil (hash SHA-256) | Pseudonymisé | Hash unidirectionnel non réversible |
| Logs d'accès | Ordinaire | Pseudonymisés — actions système uniquement |

**Données NON traitées (Privacy by Design) :** images faciales, localisation, empreintes digitales, identité civile en clair.

---

## 2. Nécessité et Proportionnalité

### 2.1 Base légale

**Consentement explicite — Art. 6(1)(a) + Art. 9(2)(a) RGPD**

Les données biométriques relèvent de l'Art. 9. La base légale retenue est le consentement explicite, qui doit être :
- **Libre** : aucune contrainte liée à un accès conditionnel
- **Spécifique** : limité à la finalité d'identification par démarche
- **Éclairé** : notice explicative présentée avant validation
- **Univoque** : flag `consent=True` obligatoire dans l'API — pas de consentement implicite

### 2.2 Finalité

**Finalité unique :** identification biométrique d'une personne par analyse de sa démarche — usage académique en environnement fermé.

Sont explicitement interdits : profilage comportemental, surveillance continue, croisement avec d'autres systèmes biométriques, usage commercial.

### 2.3 Minimisation des données

| Approche naïve (évitée) | Notre approche | Gain |
|---|---|---|
| Stockage de la vidéo brute | Vecteur 128D chiffré uniquement | **99,9% de réduction** |
| Conservation indéfinie | Purge automatique après 180 jours | Conforme Art. 5(1)(e) |
| Identité en clair dans la BDD | Pseudonyme PSE-XXXX séparé | Réidentification impossible sans clé |

---

## 3. Identification et Évaluation des Risques

| ID | Risque | Vraisemblance | Impact | Gravité | Mesures de mitigation |
|---|---|---|---|---|---|
| R01 | Réidentification à partir du vecteur | Faible | Élevé | **MOYEN** | AES-256-GCM + séparation identité/biométrie |
| R02 | Accès non autorisé à la base | Faible | Élevé | **MOYEN** | JWT 15 min + RBAC + rate limiting + logs HMAC |
| R03 | Biais algorithmique | Moyen | Moyen | **MOYEN** | bias_analysis.py obligatoire; refus si écart > 10% |
| R04 | Violation de données (fuite chiffrée) | Très faible | Élevé | **FAIBLE** | Chiffrement bout-en-bout + notification CNIL 72h |
| R05 | Détournement de finalité (surveillance) | Faible | Très élevé | **ÉLEVÉ** | Pas d'API temps réel; finalité verrouillée; PIMS |
| R06 | Collecte sans consentement valide | Faible | Élevé | **MOYEN** | `consent=True` obligatoire + audit log |
| R07 | Surapprentissage (petit dataset) | Élevé | Faible | **FAIBLE** | Documenté comme limite prototype; EER = 7,14% |

**Risque résiduel global après mesures : FAIBLE**

---

## 4. Mesures de Sécurité Implémentées

### 4.1 Données au repos
- **AES-256-GCM** : chaque vecteur chiffré individuellement, nonce 96 bits aléatoire (NIST SP 800-38D)
- **Séparation** : `pseudonym_map` et `biometric_templates` dans tables distinctes
- **Pseudonymisation** : ID civil → hash SHA-256 → pseudonyme PSE-XXXX

### 4.2 Communications
- **TLS 1.3** : toutes les communications API chiffrées
- **CORS restrictif** : origine `https://localhost:3000` uniquement
- **JWT HS256** : expiration 15 minutes + JTI anti-rejeu

### 4.3 Contrôle d'accès
- **RBAC** : 4 rôles — admin / opérateur / auditeur / utilisateur
- **Rate limiting** : 10 requêtes/minute/IP anti-brute force
- **Logs HMAC** : chaîne de hachage — toute modification invalide les entrées suivantes

### 4.4 Droits des personnes concernées

| Droit RGPD | Implémentation | Article |
|---|---|---|
| Droit à l'effacement | `DELETE /admin/subject/{id}` — suppression immédiate complète | Art. 17 |
| Limitation de conservation | Purge automatique via `expires_at` (180 jours) | Art. 5(1)(e) |
| Consentement et retrait | Flag `consent=True` + DELETE = retrait complet | Art. 7 + 9 |

---

## 5. Mapping ISO/IEC 29100

| ID | Principe | Implémentation dans GAIT·ID | Statut |
|---|---|---|---|
| P1 | Consentement et choix | `consent=True` obligatoire + notice dans l'interface | ✅ Conforme |
| P2 | Légitimité de la finalité | Finalité unique documentée dans `processing_registry` | ✅ Conforme |
| P3 | Limitation de la collecte | Seul le vecteur 128D collecté; vidéo non stockée | ✅ Conforme |
| P4 | Minimisation des données | GEI → 128D (réduction 99,9%); pas de visage ni vêtements | ✅ Conforme |
| P5 | Limitation de l'utilisation | 180 jours max; purge auto; pas de transfert tiers | ✅ Conforme |
| P6 | Exactitude et qualité | Ré-enrôlement disponible; EER = 7,14% documenté | ⚠️ Partiel |
| P7 | Transparence | Notice explicative; API documentée; DPIA publique | ✅ Conforme |
| P8 | Participation individuelle | Endpoint effacement; logs consultables par auditeur | ⚠️ Partiel |
| P9 | Responsabilité | DPIA complète; logs HMAC; RACI définie; DPD consulté | ✅ Conforme |
| P10 | Sécurité de l'information | AES-256-GCM + TLS 1.3 + JWT + RBAC + rate limiting | ✅ Conforme |
| P11 | Conformité réglementaire | RGPD Art. 35 + AI Act Annexe III + ISO 27701 | ✅ Conforme |

**Bilan : 9/11 principes conformes.** Les 2 partiels (P6, P8) sont liés au périmètre académique du prototype.

---

## 6. Conclusion

| Critère | Résultat |
|---|---|
| Risque résiduel global | **FAIBLE** |
| Décision | **PROCÉDER AVEC LES MESURES IDENTIFIÉES** |
| Consultation autorité de contrôle | Non requise (Art. 36 non déclenché) |
| Révision prévue | Mai 2027 ou avant tout changement de finalité/architecture |

### Conditions de mise en œuvre
- Consentement explicite recueilli avant tout enrôlement
- Clés AES-256 et JWT dans variables d'environnement — jamais en clair dans le code
- `src/bias_analysis.py` exécuté à chaque ajout de personnes, résultat archivé
- Notification CNIL dans les 72 heures en cas d'incident (Art. 33 RGPD)
- Données supprimées dans les 30 jours suivant la fin de la recherche

---

*Fait à Tunis, le 2 mai 2026 — Ahmed*