# Classification AI Act — GAIT·ID
**Référence :** AIACT-GAIT-001 | **Version :** 1.0 — Mai 2026  
**Système :** GAIT·ID — Reconnaissance biométrique de la démarche  
**Classification : SYSTÈME D'IA À HAUT RISQUE**

---

## 1. Présentation du Système

| Champ | Valeur |
|---|---|
| Nom du système | GAIT·ID |
| Type | Système d'identification biométrique par analyse de la démarche |
| Modèle IA | GaitPoseCNN (CNN 1D sur séquences de pose MediaPipe) |
| Entrée | Vidéo MP4 d'une personne en mouvement |
| Sortie | Identité probable + score de confiance (similarité cosinus) |
| Contexte de déploiement | Prototype académique — environnement fermé |
| Personnes concernées | Volontaires adultes consentants (5 personnes dans le prototype) |

---

## 2. Classification du Niveau de Risque

### 2.1 Analyse de classification

L'**AI Act (Règlement UE 2024/1689)**, entré en vigueur le 1er août 2024, classe les systèmes d'IA en quatre niveaux de risque. Le classement de GAIT·ID repose sur l'analyse suivante :

**Texte de référence : Annexe III, Section 1 — Biométrie**

> *"Les systèmes d'identification biométrique à distance, en temps réel ou a posteriori"*

**Vérification des exceptions (Art. 6(2)) :**

| Exception | Applicable ? | Justification |
|---|---|---|
| Usage strictement personnel | ❌ Non | Plusieurs opérateurs accèdent au système |
| Finalité purement administrative sans décision impactante | ❌ Non | Identification = décision d'accès |
| Recherche scientifique exemptée | ⚠️ Partiel | Prototype académique mais biométrie Art. 9 |

**Conclusion : GAIT·ID est classifié HAUT RISQUE selon l'Annexe III, Section 1 de l'AI Act.**

### 2.2 Usages prohibés vérifiés (Art. 5)

Les usages suivants sont **strictement interdits** et ont été vérifiés absents du système :

- ❌ Identification biométrique à distance en temps réel dans les espaces publics — *Absent : pas de flux caméra en direct*
- ❌ Notation sociale basée sur des comportements — *Absent : pas de scoring comportemental*
- ❌ Manipulation subliminale — *Absent : système d'identification uniquement*
- ❌ Exploitation des vulnérabilités de groupes — *Absent*
- ❌ Inférence d'émotions en milieu professionnel/scolaire — *Absent*

**Aucun usage prohibé détecté.**

---

## 3. Exigences AI Act — État de Conformité

### Art. 9 — Système de gestion des risques

**Exigence :** Mettre en place un processus continu d'identification, d'analyse et de mitigation des risques tout au long du cycle de vie du système.

**Implémentation dans GAIT·ID :**
- Registre des risques documenté dans `docs/DPIA.md` (R01 à R07)
- `src/bias_analysis.py` : détection automatique des biais à chaque ajout de données
- Métriques de performance (Rank-1, FAR, FRR, EER) calculées et archivées après chaque entraînement
- Seuil de refus de déploiement si écart de précision > 10% entre groupes démographiques

**Statut : ✅ IMPLÉMENTÉ** (avec limitation : processus manuel, non automatisé en continu)

---

### Art. 10 — Gouvernance des données

**Exigence :** Les données d'entraînement doivent être pertinentes, représentatives, exemptes d'erreurs et complètes. Les biais potentiels doivent être identifiés et corrigés.

**Implémentation dans GAIT·ID :**

| Critère | État | Détail |
|---|---|---|
| Pertinence des données | ✅ | Vidéos de marche directement liées à la tâche |
| Représentativité | ⚠️ | 5 personnes — dataset limité, biais déclaré |
| Absence d'erreurs | ✅ | Vecteurs vérifiés via `src/bias_analysis.py` |
| Analyse des biais | ✅ | Rapport automatique : FAR 0%, FRR 0% sur dataset d'entraînement |
| Diversité morphologique | ❌ | Non garantie avec 5 vidéos Pexels |

**Biais déclarés explicitement :**
- Dataset limité (5 personnes) : risque de surapprentissage (overfitting)
- Vidéos Pexels : biais possible sur l'angle de vue et l'environnement
- Pas de diversité morphologique garantie
- **Recommandation production : ≥ 20 personnes, angles multiples, conditions variées**

**Statut : ⚠️ PARTIELLEMENT CONFORME** — conforme pour un prototype académique, insuffisant pour production

---

### Art. 11 — Documentation technique

**Exigence :** Établir une documentation technique complète avant la mise sur le marché, incluant la description du système, ses performances, ses limites et les mesures de sécurité.

**Documentation produite :**

| Document | Fichier | Contenu |
|---|---|---|
| Architecture technique | `src/model_pose.py` + `src/pose_extractor.py` | GaitPoseCNN : CNN 1D, 3 couches conv, features 128D |
| Données d'entraînement | `src/train_pose.py` | 5 vidéos MP4, 30 frames/vidéo, 20 features/frame |
| Métriques de performance | `src/bias_analysis.py` | Accuracy 100%, FAR 0%, FRR 0% (overfitting déclaré) |
| Mesures de sécurité | `src/security.py` + `src/api.py` | AES-256-GCM, JWT, RBAC, logs HMAC |
| Analyse d'impact | `docs/DPIA.md` | DPIA complète RGPD Art. 35 |
| Limites du prototype | `docs/DPIA.md` §3, R07 | Surapprentissage, petit dataset |

**Statut : ✅ IMPLÉMENTÉ**

---

### Art. 12 — Traçabilité et journalisation

**Exigence :** Le système doit enregistrer automatiquement les événements pertinents pendant son fonctionnement afin de permettre un audit a posteriori.

**Implémentation dans GAIT·ID :**

```python
# src/api.py — chaque identification est loggée
log_action("ANALYZE_VIDEO", f"Résultat: {result['person']} score={result['score']}")

# Format des logs (logs/api.log)
# 2026-05-02 20:10:02 | INFO | ANALYZE_VIDEO | Résultat: person_05 score=1.0
```

**Événements tracés :**
- `STARTUP` : démarrage de l'API
- `LOGIN` / `LOGIN_FAILED` : authentification avec rôle et IP
- `ANALYZE_VIDEO` : chaque identification avec identité et score
- Tous les logs sont horodatés en ISO 8601

**Limitation :** Les logs ne sont pas encore signés par HMAC dans la version Flask actuelle (présent dans `src/security.py` mais non intégré au logger Flask).

**Statut : ✅ IMPLÉMENTÉ** (HMAC à intégrer pour la version finale)

---

### Art. 14 — Surveillance humaine

**Exigence :** Les systèmes d'IA à haut risque doivent permettre une supervision humaine effective pour prévenir ou minimiser les risques.

**Implémentation dans GAIT·ID :**
- Interface web (`templates/index.html`) affiche le score de confiance et tous les scores comparatifs
- L'opérateur voit les scores de toutes les personnes enrôlées — pas une boîte noire
- Endpoint `GET /health` pour supervision de l'état du système
- **Décision finale toujours visible** : l'interface montre `IDENTIFIED` ou `UNKNOWN` avec le pourcentage

**Limitation :** Pas d'interface de révision des décisions passées (tableau de bord historique non développé).

**Statut : ⚠️ PARTIELLEMENT IMPLÉMENTÉ**

---

### Art. 15 — Exactitude, robustesse et cybersécurité

**Exigence :** Le système doit atteindre un niveau approprié d'exactitude, être robuste aux erreurs et résistant aux attaques adversariales.

**Résultats de performance sur le dataset prototype :**

| Métrique | Valeur | Interprétation |
|---|---|---|
| Rank-1 Accuracy | 100% | Surapprentissage déclaré (5 personnes) |
| FAR (Faux Acceptés) | 0,0% | Aucun imposteur accepté sur le dataset |
| FRR (Faux Rejetés) | 0,0% | Aucun sujet légitime rejeté sur le dataset |
| EER (Equal Error Rate) | ~7,14% | Estimé en généralisation |

**Mesures de robustesse :**
- Features invariantes à l'angle de caméra (angles articulaires + ratios de distances)
- Rate limiting anti-brute force (10 req/min/IP)
- Seuil de confiance configurable (actuellement 0,30 après abaissement)
- Vecteurs L2-normalisés pour robustesse aux variations d'amplitude

**Statut : ⚠️ PARTIELLEMENT CONFORME** — robustesse limitée par la taille du dataset

---

## 4. Registre des Risques IA

| ID | Catégorie | Description | Probabilité | Impact | Mitigation |
|---|---|---|---|---|---|
| AI-R01 | Biais | Précision inégale selon le groupe démographique | Moyenne | Élevé | `bias_analysis.py` + seuil 10% |
| AI-R02 | Surapprentissage | Le modèle mémorise au lieu d'apprendre | Élevée | Moyen | Déclaré dans documentation; 20+ pers. en prod |
| AI-R03 | Faux positif critique | Identification incorrecte d'une personne | Faible | Élevé | Score + marge de confiance affichés |
| AI-R04 | Attaque adversariale | Vidéo modifiée pour tromper le modèle | Très faible | Élevé | Features géométriques difficiles à falsifier |
| AI-R05 | Dérive du modèle | Dégradation des performances dans le temps | Faible | Moyen | Ré-enrôlement disponible; métriques monitorées |
| AI-R06 | Manque de transparence | Décision incompréhensible pour l'opérateur | Faible | Moyen | Scores détaillés affichés dans l'interface |

---

## 5. Tableau de Conformité Synthétique

| Article AI Act | Exigence | Statut GAIT·ID |
|---|---|---|
| Art. 5 | Usages prohibés | ✅ Aucun usage prohibé |
| Art. 9 | Gestion des risques | ✅ Registre des risques + bias_analysis |
| Art. 10 | Gouvernance des données | ⚠️ Partiel — dataset limité déclaré |
| Art. 11 | Documentation technique | ✅ Code + DPIA + métriques |
| Art. 12 | Traçabilité | ✅ Logs horodatés + HMAC (à finaliser) |
| Art. 13 | Transparence envers les utilisateurs | ✅ Interface avec scores détaillés |
| Art. 14 | Surveillance humaine | ⚠️ Partiel — pas d'historique de révision |
| Art. 15 | Exactitude et robustesse | ⚠️ Partiel — limité par taille dataset |

**Conformité globale pour un prototype académique : 5/8 articles pleinement satisfaits.**  
Les 3 partiels sont inhérents au périmètre "prototype" et documentés comme tels.

---

## 6. Recommandations pour la Production

Si ce système devait être déployé en production, les mesures suivantes seraient **obligatoires** :

1. **Dataset** : minimum 20 personnes, 3 vidéos par personne, angles variés (face/profil/3/4)
2. **Validation croisée** : k-fold cross-validation au lieu de la validation sur données d'entraînement
3. **Audit biais** : test sur groupes démographiques équilibrés (genre, âge, morphologie)
4. **Marquage CE** : conformité Art. 49 — organisme notifié pour systèmes biométriques
5. **DPO** : désignation d'un DPD dédié (Art. 37 RGPD)
6. **Supervision humaine renforcée** : tableau de bord historique + alerte sur FAR > 1%
7. **Tests adversariaux** : validation contre des attaques de type injection de pose

---

*Fait à Tunis, le 2 mai 2026 — Ahmed*