# Revue M. Sauthier — octobre 2026 (re-gel 50)

Registre de traitement de la relecture de M. Sauthier reçue le 2026-10-06 : deux
fichiers Word corrigés, le papier et le supplément, en modifications suivies. Les
fichiers eux-mêmes restent locaux et ne sont jamais commités : ils sont protégés
par `.gitignore` et par `.githooks/pre-commit`.

**Base.** Les deux fichiers partent de la version envoyée le 2026-09-28 (re-gel 50,
source `bf6f6fe`). C'est vérifié en reconstruisant le texte « avant modifications »
de chaque paragraphe et en le comparant à
`preprint_npj/build/sent_2026-09-28_refreeze50/*.docx` :
- les paragraphes sont identiques, à deux différences près sans contenu : les
  signes moins U+2212 sont devenus des traits d'union partout, et la mise en
  forme des listes de références change ;
- **une seule modification n'est pas suivie** : les deux paragraphes de §4.7
  (« S.N. and M.S. », « all the authors »).

`paper.tex` et `supplement.tex` n'ont pas changé depuis `bf6f6fe` : chaque
modification proposée correspond donc ligne pour ligne au texte actuel.

**Volume.**
- Papier : 81 paragraphes modifiés, 10 commentaires.
- Supplément : 181 paragraphes modifiés, 7 commentaires.
- Le texte modifié porte l'auteur « Author », c'est-à-dire l'assistant IA de M.S.
  Les marques à son propre nom sont des marques vides dans les formules.
- Aucun texte masqué, surlignage ou changement de mise en forme. Notes vides.
  Images identiques aux nôtres (SHA-256).

**Règle de traitement (consigne de l'auteur, 2026-10-06).**
1. Ce qui suit la correction est appliqué tel quel.
2. Tout écart par rapport à ce que demande M.S. est soumis à l'auteur **avant**
   application, puis consigné ici avec sa justification, pour pouvoir répondre
   à M.S.
3. L'information porteuse retirée du papier est reportée brièvement dans le
   supplément quand elle n'y est pas déjà.

**Contrôle des citations.** Chaque fragment cité ci-dessous, de sa version comme
de la nôtre, a été retrouvé mot pour mot dans sa source par un script : texte
révisé du docx pour lui, `.tex` actuel pour nous (25 fragments sur 25).

## 1. Décisions structurelles (auteur, 2026-10-06)

| # | Proposition de M.S. | Décision | Justification à donner à M.S. |
|---|---|---|---|
| Q1 | Renommer S1–S4 avec un nom qui rappelle le scénario (« S_healthy, S_mild… ») | **Suivie, sous la forme Healthy / Mild / Moderate / Severe**, cellules Healthy-M … Severe-F ; les identifiants de données (S1_F_0117, colonnes CSV) restent S1–S4, avec une note de correspondance dans la Table 1 | « S » sert déjà aux sections, tableaux et figures du supplément (§S1–S18, Table S1…) et aux expériences (S011, S021) ; des mots simples évitent ce troisième sens |
| Q2 | §4.7 : « S.N. and M.S. » pour la supervision et la décision des rondes ; « all the authors » | **Adaptée** : une phrase dédiée à sa relecture assistée par Claude (§4.7 + détail en §S18) ; « all the authors » repris | Telle quelle, la phrase attribuait à M.S. la supervision du code et la décision des rondes IA, ce qui ne décrit pas ce qui s'est passé |
| Q3 | Figure S5 déplacée près de son appel (§S3.12) | **Non suivie** : figure laissée en place | En LaTeX, la déplacer la renumérote en S1 et décale les cinq figures du supplément (registre d'audit, scripts, carte de la monographie). La numérotation ajoutée au Word permet au moins de l'identifier |
| Q4 | Erratum de §S3.4 : réduire ou supprimer | **Suivie : supprimé** | Aucun lecteur externe n'a vu la version fautive ; la trace reste dans `audit/cdc_weight_provenance_mismatch.md` |
| D2 | Mots-clés 13 → 8 | **Suivie** | — |

## 2. Écarts — VALIDÉS par l'auteur le 2026-10-06 (tous)

Validés en bloc par l'auteur le 2026-10-06, après revérification paranoïaque ; petits choix : D10b, D17, D26 selon la recommandation ; E5 et E6 selon la recommandation.
Force de l'écart : **F** = sa phrase est fausse ou contredit nos données ;
**R** = elle défait une réserve posée exprès par un commit antérieur ;
**P** = portée élargie.

### Papier

| # | Lieu | Sa version | Proposé | Force | Justification (vérifiée) |
|---|---|---|---|---|---|
| D1 | Résumé | réécriture | garder le résumé actuel | F | 174 mots (171 alphanumériques) pour un plafond npj de 150 ; le nôtre en fait 149/146. Sa phrase « Solver divergence occurs only on the male body » remet aussi au présent général un résultat que `64c39d1` a borné au balayage |
| D3 | Intro ¶1 | « simulator data **enriched in** infrequent adverse conditions » | « simulator data **that include** infrequent adverse conditions » | F | Hwang 2025, texte intégral relu le 2026-10-06 : *« generate synthetic patient profiles with systematic variability. This includes adverse and infrequent conditions »*, mis en contraste avec le sur-échantillonnage (SMOTE). L'article ne décrit pas d'enrichissement |
| D4 | Intro ¶3 | « each downstream user **must** establish a working envelope independently » | « may need to establish a use-case-specific working envelope independently » | R | Universel non soutenu, retiré exprès par `64c39d1` : un utilisateur peut avoir une ressource interne, sa propre validation ou l'aide des développeurs |
| D5 | Intro ¶3 | retire « and rank parameters by outcome correlation » (Webb) | garder | R | Phrase corrigée sur le texte intégral de Webb 2020 (`013bb44`) : ils ont classé des paramètres ; l'omettre sous-décrit un travail proche et fragilise notre affirmation de nouveauté |
| D6 | §2.2 | « The top of the rankings is robust… Rank 1 is therefore stable » | ouverture neutre + « Under this screen comparison, rank 1 was more stable than the ordering below it » | F | Contredit les données : le rang 1 change dans 7 des 18 combinaisons dont l'ensemble candidat diffère entre écrans ; 5 rangs 1 reposent sur une seule paire ; pas d'analyse de convergence (`a064d14`, `results/s034/rank_comparison.csv`) |
| D8 | Légende Fig. 5 | « so blood volume **cannot be equalised** between the two bodies » | « so a one-way blood-volume transplant cannot make the two reference bodies equal in blood volume » (texte actuel) | F | Faux d'après le code de Pulse : `SetupPatient.cpp` L535–536 borne chaque corps à ×0,85–×1,15 de sa propre valeur ; plancher mâle 4 082,24 mL < plafond femelle 4 595,50 mL, donc une valeur commune (par ex. 4 300 mL) est acceptée pour les deux |
| D9a | Discussion ¶1 | « across adult critical-care scenarios » | garder « several » | P | Quatre scénarios en VC-AC ne couvrent pas les scénarios de réanimation adulte en général (réserve ajoutée lors de la ronde P.J., `a09b490`) |
| D9b | Discussion ¶1 | « a … solver-divergence cluster **affects only the male body** » | « is confined to the male body in this input-extreme regime » ; *appliqué : « in **an** input-extreme regime » (aucun antécédent de « ce » régime dans la phrase ; écart relevé à l'audit du 2026-10-07, l'auteur garde « an »)* | R | `64c39d1` a borné le résultat « all-male » partout où le lecteur le rencontre ; aux entrées médianes, les deux corps divergent (§S5.4, Table S11 : femmes 14/19 contre hommes 5/19 dans (0.85, 0.91]) |
| D11 | Discussion | « closed-loop ventilation … **without changing** patient-centred outcomes » | garder « yet showed no difference in patient-centred outcomes » | P | Sinnige 2026 (registre des références, MATCH) : *« showed no difference in ventilator-free days or mortality »*. Ne pas montrer de différence n'est pas montrer l'absence d'effet |
| D12 | §4.1 | « **Every run** used the same pinned … Docker image, ensuring bit-identical engine binaries » | garder « pinned for the 1,280-run sweep so that every simulation runs against bit-identical engine binaries » | F | Faux : `engine/Dockerfile` a reçu le correctif S014 après le balayage (commit `2c1cbfa` du 2026-05-04, expérience S014 datée du 2026-04-28 ; balayage commité le 2026-04-26, `e068544`), et le journal S014 impose de reconstruire l'image pour les relances ; `:latest` a été reconstruite après le balayage (journal S032). *Corrigé le 2026-10-06 à la revérification : la première version citait `ae76ca0`, identifiant d'avant la réécriture de l'historique, absent de l'historique actuel.* |
| D13 | §4.4 | « Pulse … **only** stops a run for states far outside physiology » | garder « It does stop a run on some states far outside physiology » | F | Faux dans le code de Pulse : l'arrêt passe par `Fatal()`, appelé aussi pour « Unable to tune circuit » (`CardiovascularModel.cpp` L3647) et pour d'autres erreurs. « some states » vient d'une correction validée par l'auteur (`bcec0db`) |
| D15 | §4.8 | « recomputes the paper's **quantitative** claims » | garder « computed claims » | F | Le registre d'audit recalcule les nombres calculés à partir des sorties, pas les valeurs de la littérature (760 mmHg, poids CDC…), ni toutes les occurrences numériques (`e136118`) |
| D16 | §4.7 | modifications suivies de son assistant : retire « Verification was an iterative process of checks », « Although the atlas code was written with LLM assistance », « as applicable », « always », « in particular » ; ajoute « all AI-assisted outputs » ; reformule la dernière phrase | garder notre texte, plus la phrase M.S. et « all the authors » (Q2) | R | Formulations décidées par l'auteur (2026-09-27/28) ; « as applicable » est une réserve vraie ; dernière phrase gardée mot pour mot à la demande de l'auteur (`b7ff9b5`) |

### Supplément

| # | Lieu | Sa version | Proposé | Force | Justification (vérifiée) |
|---|---|---|---|---|---|
| D18 | §S3.10 | « 32 of the 34 … are **no longer flagged** » | garder « no longer exceed the widened PaO₂ plausibility bound » | F | L'analyse (`scripts/f003_physiological_reclassification.py` L77–80) ne compare que PaO₂ à 700 mmHg ; elle ne vérifie pas les autres drapeaux de ces runs |
| D20 | §S5.1 | « so **no headline result** depends on an external project » | garder « so a headline result no longer depends on an external project » | P | Seule cette calibration a été reproduite ici ; l'affirmation générale n'a pas été vérifiée pour tous les résultats principaux |
| D21 | §S5.4 | « impairment 0.879, **the low edge of** the (0.85, 0.91] bin » | « 0.879, **inside** the (0.85, 0.91] bin » | F | Le bord inférieur de la case est 0.85 (Table S11). ⚠️ Notre texte actuel est déjà ambigu sur ce point (« the low edge of the (0.85, 0.91] bin where the empirical signal first appears ») : la correction répare les deux |
| D22 | §S9.1 | « flags runs as implausible … **precisely because** the slow late-phase relaxation is not yet complete » | garder « under exactly the conditions where the slow late-phase relaxation has not yet completed » | F | Causalité inversée : pendant la relaxation, PaO₂ monte encore ; au plateau (médiane 643 mmHg), il dépasserait davantage le seuil de 600 |
| D24 | §S12.5 | « which **shows** empirically that bit-identity holds across CPU vendors and host operating systems » | garder « empirical evidence that bit-identity holds across CPU vendor and host operating system » | P | Deux machines seulement (Intel/Windows, AMD/WSL2) |
| D25 | Fig. S5 | déplacée | non déplacée (Q3) ; ses modifications de légende sont appliquées sur place | — | voir Q3 |
| D27 | §S3.11 | « The implemented rule therefore never produced a **more** favourable verdict » | garder « never converted a combination into a favourable verdict » | F | Faux tel quel : 26 combinaisons sont jaunes avec la règle appliquée et rouges en lecture littérale (Table S6 : 7/29/12 contre 7/3/38), donc plus favorables. La phrase d'origine parle du vert, qui est invariant |

### Petits choix (sans enjeu scientifique) — tranchés : recommandation retenue pour les trois

| # | Lieu | Sa version | Recommandé | Raison |
|---|---|---|---|---|
| D10b | Discussion ¶3 | retire la glose « (one the model performs by acting in a software environment) » après « agent task » | garder la glose | Ajoutée exprès par l'auteur (re-gel 32) pour un lecteur clinicien qui ne connaît pas les agents IA |
| D17 | Remerciements | fusion des phrases, « financial support » pour les quatre financeurs, virgule à la place du tiret dans la dédicace | garder les nôtres | Texte personnel de l'auteur ; les financeurs imposent parfois leur formulation |
| D26 | Organisation du supplément | index des résultats en tête, trois blocs, table des matières | une phrase en tête qui renvoie à l'index (Table S18) + table des matières dans le Word (le PDF en a déjà une) ; pas de regroupement | Regrouper renumérote toutes les sections du supplément, que le papier cite (« Supplement § S3.7 ») ; son assistant ne l'avait pas appliqué pour cette raison |

### Second lot — trouvés en recalant les gardes, tranchés par l'auteur le 2026-10-06

| # | Lieu | Sa version | Retenu | Force | Justification (vérifiée sur les artefacts, 2026-10-06) |
|---|---|---|---|---|---|
| D28 | Légende Table 3 | « nine of the sixteen retention values would fall on an exact rounding tie » | ajouter « at one or two decimals » | F | Le compte dépend de la précision : sur les 16 effectifs (`aggregated.parquet`), 4 tombent sur une égalité à l'entier, 4 à une décimale, 5 à deux décimales ; « nine » n'est vrai qu'à une ou deux décimales (13 valeurs tombent sur une égalité à l'une des trois précisions). *Dans la question posée à l'auteur, j'avais écrit « ce serait 13 à l'entier » : c'est 4 à l'entier, 13 toutes précisions confondues ; la décision n'en dépend pas.* |
| D29 | §2.1, audit d'instanciation | « The remaining 80 of the 10,240 contracts belong to the 20 runs… » | « …are the ventilator contracts of the 20 runs… » | F | `results/input_instantiation_long.csv` : 8 contrats par run (4 patient, 4 ventilateur) ; les 80 non ingérés sont tous des contrats ventilateur ; les 80 contrats patient de ces mêmes 20 runs ont été ingérés. Sans « ventilator », 20 × 8 = 160 ≠ 80 |
| D30 | §2.4 | « with a median of 643 mmHg » | « …over all 40 » | R | La médiane porte sur les 40 relances convergées, emballements compris (642,87 mmHg) ; sur les 37 physiologiques elle vaut 640,4. La phrase suivante introduit les 3 emballements (1 403–1 408 mmHg) : la population doit être dite (décision du 2026-09-08, point 3.6) |
| D31 | §2.2 | « under both screens » | **suivie** (pas d'écart) | — | Le §2.1 définit exactement deux filtres (« four-flag », « hard-failure-free », « The two screens ») ; la décision du 2026-09-23 de les nommer à nouveau ici est levée |

**Revérification finale (2026-10-06, demandée par l'auteur).** Les 34 décisions
de cette ronde ont été contrôlées une à une dans les fichiers (texte retenu
présent, texte refusé absent ; résumé et remerciements identiques à la version
envoyée). Sources primaires relues dans cette session : Hwang 2025 (texte
intégral, Europe PMC PMC12531325) pour D3 ; Sinnige 2026 (résumé, PMID 41361939)
pour D11 ; Webb 2020 (texte intégral, PMC7688119) pour D5 ; `SetupPatient.cpp`
et `CardiovascularModel.cpp` à `REL_4_3_1` pour D8 et D13 ;
`f003_physiological_reclassification.py` et son CSV pour D18 et E5 ; Table S6
pour D27. Une erreur trouvée et corrigée dans ce registre (D12, ci-dessus).

### Écarts envisagés puis retirés après vérification (on suit M.S.)

| # | Lieu | Raison du retrait |
|---|---|---|
| W7 | §2.5, « and differ only in absolute volume » | Dans la phrase, le sujet est le volume sanguin : sa lecture est juste |
| W10 | Discussion, « Unlike those stages » | Même sens que « One difference is that » |
| W14 | §4.5, retrait de « committed after preregistration » | Le titre garde « post hoc » ; le fait précis est **reporté en §S3.11** (règle 3), où il manquait |
| W19 | §S3.7, « corrects the denominator » | Diviser par le pas réellement appliqué corrige bien le dénominateur de ces transitions ; le paragraphe dit ensuite pourquoi l'indice n'est pas corrigé pour autant |
| W23 | §S9.2, retrait de « in this cohort » | « affected from unaffected runs » désigne déjà les runs de cette cohorte |

## 3. Information retirée du papier et reportée dans le supplément

| Retiré du papier | Couverture dans le supplément |
|---|---|
| Gloses du taux de fausses découvertes et de Spearman (§4.6) | **ajoutées** au glossaire §S3.14 |
| « or a still-drifting SpO₂ » (légende Fig. 3, cause des cases blanches en S4_F) | **ajouté** en §S2.1 (iv), qui ne disait que « severe hypoxemia » |
| « committed after preregistration » (§4.5) | **ajouté** en §S3.11 |
| « jointly » (bootstrap de σ/μ*, §4.6) | déjà en §S3.8 |
| Partition des six emballements (3 convergés, 3 non) | déjà en §S9.2 |
| Phrase des éléments préregistrés (§4.8) | déjà répartie : Intro ¶6, légende Table 2, §4.3, §4.5, §4.6 |
| Cornish « largely outside the six-output panel » | Discussion (80 sur 85) + §S7 |

## 4. Défauts trouvés chez nous pendant cette ronde

| # | Lieu | Défaut | Statut |
|---|---|---|---|
| E1 | §S13.1 | « tree-based **reference body** model » au lieu de « surrogate » : rechercher-remplacer du commit `1016087` (seule occurrence, contrôle positif fait) | signalé par M.S. ; on suit sa correction |
| E2 | Table S7, légende | `` ``excl.\'' `` : `\'` est un accent LaTeX, la coquille est visible aussi dans le PDF | signalé par M.S. ; on suit sa correction |
| E3 | Word (papier + supplément) | pas de numéros de figures, tableaux et sections ; titres `\bmhead` (Data availability, Acknowledgements…) et « References » absents | signalé par M.S. (citation retirée de l'historique public ; voir HISTORY.md) ; **corrigé** dans `scripts/tex_to_docx.py` (numéros pris dans les `.aux`, donc identiques au PDF ; « Contents » statique dans le supplément) et **gardé** dans `scripts/check_docx_structure.py` (contrôle positif : l'ancien Word échoue, 42 problèmes sur le papier) |
| E5 | §S9.2 vs §S3.10 | §S9.2 : le mode d'emballement apparaît « only at extended windows on healthy lungs at FiO₂ = 1.0 » ; §S3.10 : deux runs de femmes saines (S1_F_0118, S1_F_0119, **FiO₂ = 0,737**, `results/f003_physiological_reclassification.csv`) s'emballent **dans** la fenêtre de 120 s, « the same … solver instability ». Les deux phrases ne peuvent pas être vraies ensemble. M.S. garde le « only » | validé : correction appliquée (2026-10-06) |
| E6 | §S15 | « archived with the code and data in the Zenodo deposit » (présent) alors que le papier dit « will be deposited » | validé : correction appliquée (2026-10-06) |
| E7 | Monographie | « 32 of the 34 … become physiologically clean under the wider bound » : même excès que D18 | **aligné** : « no longer exceed the wider PaO2 bound » (le script ne compare que PaO₂ à 700 mmHg, relu le 2026-10-06, L77–80) ; libellé du registre d'audit `T2.f003.reclass` aligné |
| E8 | Word (papier Table 3, supplément Tables S7 et S10) | défaut introduit pendant cette ronde : les en-têtes et cellules sur deux lignes (`\shortstack`, ajoutés pour la mise en page du PDF) étaient lus par pandoc comme des fins de ligne ; dans le Word, chaque tableau gagnait des lignes et perdait le début des cellules (« hard-failure- », « not_steady_ », « 663 », « 1,134 », « n_clean », « Mild/Moderate/Severe ») ; présent dans les Word du re-gel 51, non envoyés | **corrigé** dans `scripts/tex_to_docx.py` (`unstack_cells` : une ligne dans le Word, PDF inchangé) et **gardé** dans `scripts/check_docx_structure.py` (lignes LaTeX = lignes Word, tableau par tableau ; contrôle positif : les 3 tableaux échouent sur l'ancien Word, 0 au re-gel 50) ; trouvé à l'audit du 2026-10-07 |
| ~~E4~~ | ~~§S3.11~~ | ~~retiré : j'avais cité notre texte de travers ; il dit « a favourable verdict » (vert) et il est juste. Le défaut est dans la version de M.S. → D27~~ | — |

## 5. Commentaires de M.S. et réponses

| Commentaire (résumé) | Réponse |
|---|---|
| Renommer S1–S4 (×2, dont tableaux et figures) | Fait (Q1) |
| Tableaux et figures non numérotés : voulu ? | Non : défaut de notre conversion Word (E3), corrigé |
| Fusionner la Table 4 dans la Table 3 | Fait : colonne « Hard-failure-free » ajoutée à la Table 3 |
| Mots-clés réduits de 13 à 8 | Suivi |
| Fusion des paragraphes sur le manque (FAQ, étude 2020, Cornish, Webb) | Fait (sauf D4, D5) |
| Paragraphe H1/σ-μ* découpé en trois | Fait (sauf D6) |
| Paragraphe volume sanguin découpé | Fait |
| Réorganisation de la Discussion | Fait : découpage du premier paragraphe (sauf D9) |
| Contraintes d'entrée déplacées vers les plages échantillonnées | Fait |
| Supplément : index en tête, trois blocs, table des matières | Fait selon D26 : phrase d'ouverture qui renvoie à l'index (Table S18) et table des matières dans le Word ; pas de regroupement en blocs |
| Erratum §S3.4 | Supprimé (Q4) |
| Figure S5 hors contexte | Q3 |
| Coquille « excl. » | Corrigée (E2) |
| Long paragraphe §S9.2 découpé en trois | Fait |
| Titre « Reviewer-relevant disambiguation » | Renommé comme proposé |
| « tree-based reference body model » | Corrigé (E1) |

## 6. Mise en œuvre du renommage (Q1) et choix de présentation

Choix sans enjeu scientifique, tranchés selon le pacte d'autonomie (choix retenu,
alternative écartée) :

| Point | Retenu | Écarté |
|---|---|---|
| Libellés | Healthy, Mild, Moderate, Severe ; cellules Healthy-M … Severe-F ; dans la prose « the Healthy scenario », « in Moderate » | minuscules descriptives partout (« in moderate ARDS »), qui ne se distinguent plus des descriptions cliniques |
| Correspondance avec les données | une phrase dans la Table 1 (« Data files and run identifiers code these four scenarios S1--S4, in this order ») et « Healthy-F (S1\_F in the data files) » ; identifiants de runs (S1\_F\_0117), ancres du registre (T2.sp.S2.*), numérotation du supplément (§S1–S18) inchangés | renommer aussi les identifiants de données (casserait le lien avec les fichiers publiés) |
| Figure 3 (heatmaps μ*) | axe à deux niveaux : M / F sous chaque colonne, scénario sous chaque paire ; remplace l'intitulé d'axe, hauteur inchangée | étiquettes inclinées (« Moderate-M » ne tient pas dans une colonne ; inclinées, elles agrandissent le panneau, dont la hauteur est contrainte) |
| Figure S2 (ρ de Spearman) | gardée telle quelle, avec ses codes S1–S4 ; la légende donne la correspondance | la redessiner (c'est la Figure 5 de la monographie, reproduite ; la redessiner la ferait diverger de sa source) |
| Clés de cellules des légendes (Table S7, Figure S5, Table S15) | renvoi à la Table 1 du papier ; la clé « Scenario key » de la Table S15 est retirée, les noms se lisant seuls | garder des clés qui ne traduisent plus rien |
| Mise en page | en-têtes sur deux lignes (Table 3, Table S7, Table S10), `\tabcolsep` réduit dans la Table 3, colonne de texte élargie dans la Table S18 (le flottant dépassait la page de 11 pt, défaut déjà vu le 2026-08-25) | police plus petite |
| Table des matières du Word | liste statique (numéros + titres) | champ TOC de Word, qui fait demander une mise à jour des champs à chaque ouverture |
| « main paper » dans le supplément | harmonisé en « main manuscript », la forme du reste du supplément : la version de M.S. gardait 7 occurrences sur les 15 du re-gel 50 (5 « main paper », 2 « main-paper ») ; 4 + 2 harmonisées, la 7ᵉ disparaît avec la clé de légende de la Table S7 ; 0 aujourd'hui dans le papier et le supplément (consigné à l'audit du 2026-10-07) | garder les deux formes |

Gardes recalés sur les nouveaux libellés, sans rien affaiblir (le fait vérifié
avant chaque chaîne) : `audit_claims.py` (gardes de phrases, 13 littéraux du
contrôle S033, table de correspondance : 30 lignes recalées, soit 22 à la
transposition, dont 3 sur le seul compte, et les 8 lignes de la Table 3 au
renommage ; 1 supprimée « 82 of 85 » ; 2 ajoutées ; donc 95 entrées),
`audit/backref_manifest.txt` (+1 renvoi : « Table 1 of the main manuscript
gives the correspondence »). La monographie n'est pas renommée : elle documente
les données, qui gardent S1–S4.

**Erratum (mesuré le 2026-10-06, `bf6f6fe` contre `HEAD`).** Ce paragraphe disait
d'abord « 23 lignes recalées » : 23 était le nombre de lignes en échec, pas de
lignes modifiées. Le message du commit `d0361de` porte la même erreur, et il dit
aussi « 14 S033 literals » : ce sont 13 littéraux distincts (14 remplacements,
un littéral figurant deux fois dans le code). Le commit n'est pas réécrit : le
journal d'envoi le cite comme source du re-gel 51.
