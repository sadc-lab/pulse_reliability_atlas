# Revue A. Wiedemann — octobre 2026 (re-gel 54)

Registre de traitement de la relecture d'A. Wiedemann, reçue le 2026-10-09
sous forme de deux fichiers Word corrigés du papier. Les deux portent des
commentaires et aucune modification suivie. Les fichiers restent locaux
(`retours_chefs/2026-10-09_wiedemann/`, ignoré par git et refusé par
`.githooks/`) et ne sont jamais commités.

Règle de l'auteur (2026-10-09) : rien de ce qui vient d'un mail ou d'un
message n'est cité dans ce registre. Seuls les commentaires Word y sont
résumés, en termes neutres.

**Base.** Le re-gel 54, source `47ab3b8`, envoyé le 2026-10-07. Vérifications :
- création des fichiers à 22:32 UTC, comme le `paper.docx` envoyé ;
- les ajouts du 2026-10-07 sont présents, alors qu'ils sont absents du re-gel 50 ;
- les 10 images sont identiques (SHA-256) dans les deux fichiers ;
- `paper.tex` n'a pas changé depuis `47ab3b8`.

**Les deux fichiers.**
- 1er fichier : 20 commentaires, de l'Introduction au §2.6.
- 2e fichier :
  - les mêmes 20 commentaires à l'identique (texte, ancre, section) et 19
    nouveaux (identifiants 32–50), tous dans la Discussion ;
  - un seul changement de texte : « (PE-DIATRICS) » devient « (PEDIATRICS) »
    dans l'affiliation 2 ;
  - tout le reste est identique au 1er fichier ;
  - fils de réponses : 5→4, 21→20, 24→23, 28→27, 36→35, 39→38 ; aucun
    commentaire n'est marqué résolu.

## 1. Changements non signalés dans les fichiers

| Changement | Constat | Suite |
|---|---|---|
| Mise en page : tableaux puis figures en fin, avant les références ; mots-clés avant le résumé ; interligne 1,5 (62 paragraphes) ; titre « Table » ajouté ; « References » passé en style de texte | Le fichier soumis reste le PDF compilé ; npj accepte les figures et tableaux dans le texte à la première soumission (§4) | **Décision de l'auteur : tableaux et figures restent dans le texte** ; format final à l'acceptation |
| Affiliation d'A.W. : « 3,4,6 » | `paper.tex` L97, le PDF et `submission_metadata.txt` donnent 2,3,4,6. Tapé d'un bloc, sans suppression | Question à A.W. ; rien changé d'ici là |
| « PE-DIATRICS » → « PEDIATRICS » (2e fichier) | Recherche du 2026-10-09 (Europe PMC, champ affiliation) : « PE-DIATRICS » figure dans une affiliation publiée de 2024 (doi:10.3390/diagnostics14232763, dont l'auteur et A.W. sont coauteurs). Deux articles de 2026 du même groupe (doi:10.1177/21501351251386703 et doi:10.1177/21501351261418272) écrivent le nom du cluster sans sigle. Aucune source pour « PEDIATRICS ». Orthographe officielle non établie | Garder « PE-DIATRICS » ; demander à P.J. |
| Ligne « Corresponding author … » avec une adresse à compléter | Le PDF avait la ligne et l'adresse, le Word non | Convertisseur corrigé, `74c3765` |
| Section « Materials availability » supprimée | npj ne la demande pas (§4) | **Appliqué**, `7021cce` (D6) |
| Un espace retiré avant un appel de citation | Les 42 appels du papier et les 57 du supplément avaient ce défaut, dans le Word seulement | Convertisseur corrigé, `74c3765` |
| « § S9 » devenu « §S9 » ; italiques perdues (14 fragments, légendes du Tableau 3 et de la Figure 2) ; « − » devenu « - » dans les 8 formules ; un lien de citation devenu un champ | Artefacts de Word | Rien |

## 2. Commentaires 3–30 (Introduction → §2.6)

| # | Lieu | Sujet (résumé) | Réponse (source) | Suite |
|---|---|---|---|---|
| 3 | Intro ¶4 | La mention du but pédiatrique est-elle utile au lecteur ? | Voir C45/C47 | **En discussion avec l'auteur** |
| 4, 5 | Intro, dernier ¶ | Ce paragraphe relève-t-il des Méthodes ? | Les Méthodes sont à la fin (format npj) ; ce ¶ donne le plan avant les Résultats | Garder |
| 6 | Intro | Combien de runs pour une grille complète ? | 4 niveaux (§4.3) : 4⁷ = 16 384 par cellule, 131 072 pour 8 ; Morris en fait 160 par cellule (≈ 1 %) | Réponse |
| 7 | Intro, ¶ final | Des limites sont déjà dites dans l'Introduction | Réserves voulues (`a480b57`, gardées dans `d8d7b5b`, `629d3a0`) | Garder |
| 10 | §2.1 | Où sont définis Mild / Moderate / Severe ? | Tableau 1, Figure 1, §4.3 ; Tableau 1 jamais appelé dans le texte | **D1 appliqué** |
| 11 | §2.1 | Le drapeau « clamped » correspond-il à H1 ? | Non, à H2 ; H1 n'est pas définie au §2.1 | **D2 appliqué** |
| 12 | §2.1 | Rétention basse en sain : la PaO₂ monte-t-elle encore ? | Surtout oscillation du Vt et SpO₂ à 100 % (§S4 : 225 → 53) ; les 34 sains `implausible` = PaO₂ > 600 (§2.4) | Réponse ; incise au §2.1 à discuter plus tard |
| 15 | §2.2 | La FC de sortie dépend surtout de la FC d'entrée ? | Oui, dans les 8 cellules ; FC d'entrée = valeur de départ (§4.3) | Réponse |
| 16, 18 | §2.2, §2.3 | Le Vt varie aussi en clinique : pourquoi « instable » ? Faux positifs ? | Le drapeau dit « la moyenne résume mal » (Tableau 2) ; le filtre sans échec grave garde ces runs (1 134 / 1 280) | **D14 appliqué** (« oscillation ») |
| 19 | §2.3 | L'interprétation en dyssynchronie relève de la Discussion | Courte, prudente, reprise au résumé ; analyse cycle par cycle au §S8.3 | Garder |
| 20 | §2.3 | Le mode par défaut est-il assisté ? | Oui : `AssistedControl` (`engine/run_atlas_engine.py` L191–192), déclencheur du modèle respiratoire par défaut (`SEMechanicalVentilatorVolumeControl.cpp` L120–128 ; testé seulement pendant l'expiration, `MechanicalVentilatorModel.cpp` L798–818, REL_4_3_1) | **D3 appliqué** |
| 21 | §2.3 | Pourquoi ce réglage serait-il délétère ? | Voir §5, Q4 | **Appliqué** (`874fced`, `61884c5`, `5fe2378` ; voir §7) |
| 23, 24 | §2.4 | Stable ou fiable ? Sous 760 mmHg, est-ce acceptable ? | Drapeau dû à la borne de 600 mmHg, volontairement prudente sous ≈ 663 (§S3) ; avec 700, 32 / 34 ne sont plus signalés. Fenêtre de 120 s trop courte : avec 300 s, 40 / 44 reruns se stabilisent (médiane 643) ; 6 instables. 760 = pression totale | **D4 appliqué** |
| 26 | §2.5 | Pas de discussion dans les Résultats (approbation) | — | — |
| 27, 28 | §2.5 | Le Vt est-il rapporté au poids ? (lien : table SRLF, Richard, *Réanimation* 15:87, 2006, doi:10.1016/j.reaurg.2005.12.017) | Vt en mL absolus, identiques pour les deux corps (§4.3, §S6.2). La table SRLF (0,91 kg/cm) ≠ Pulse (Devine en pouces, `SetupPatient.cpp` L131–146) : ne pas l'utiliser pour nos chiffres | **D5 appliqué** ; pas de référence ajoutée |
| 30 | §2.6 | La tachycardie vient-elle du seul SDRA ? | Oui par construction ; mécanisme non isolé (§S15) | Réponse |

## 3. Commentaires 32–50 (Discussion)

| # | Sujet (résumé) | Réponse (source) | Suite |
|---|---|---|---|
| 32 | Doute sur « pas une recommandation clinique » ; la variabilité est naturelle | Lié à C21 | Avec Q4 |
| 33 | « plus long » : que quoi ? | Pas de point de comparaison | **D7 appliqué** |
| 34 | Impact de la divergence du solveur ? | Run sans sortie utilisable (Tableau 2) | **D8 appliqué** |
| 35, 36, 38, 39 | Tachycardie « hors gamme » et en rouge (Figure 2) ; un patient sédaté et curarisé est vers 60 bpm | Rouge = écart de plus de 30 % avec le scénario sain chez l'homme ; « hors gamme » = au-dessus des FC d'entrée (50–110) ; nos scénarios n'ont ni sédatif ni curare (aucune action médicamenteuse dans `src/` ni `engine/`) | **D12 appliqué** (§S15) |
| 37, 40 | Compréhension de l'objectif, accord | — | — |
| 41 | Les différences hommes-femmes existent en clinique | La mise en garde vise la réutilisation des données | **D9 appliqué** |
| 42 | Effets croisés ventilation → hémodynamique non regardés | Mesuré (`results/morris_indices.parquet`, recoupé par `results/s034/mu_star_by_screen.csv`) : PEEP, FR, FiO₂ déplacent la FC jusqu'à 9, 10, 14 bpm, la PAM ≤ 0,22 / 2,1 mmHg ; Pulse modélise l'effet de la PEEP sur le retour veineux (`CardiovascularModel.cpp`) ; mécanisme non isolé | Plus tard |
| 43 | Deux corps de référence : est-ce une limite ? | Corps jeunes et minces (18 ans, IMC ≈ 21) ; Pulse refuse moins de 18 ans | **D15 appliqué** |
| 44 | Toujours le même déclencheur ? | Oui : 0 des 1 280 configurations ne fixe un seuil (les 64 reruns s014 en ont un) | **D10 appliqué** |
| 45, 47 | Ne pas annoncer la suite pédiatrique | Passages : papier L146, L322 (iii), L324 ; supplément L193, L557 | **En discussion avec l'auteur** |
| 46 | La PAS pèse plus que la PAD sur la PAM | Vrai (μ* 17–20 contre 3–7 mmHg) et pas un artefact du plafond (§S3.7) ; mécanisme non établi | **D13 appliqué** |
| 48 | Une validation sur MIMIC-IV serait complexe | Phrase plus précise possible | Plus tard |
| 49 | Parler des asynchronies : un filtre retirerait beaucoup de données | Exact : le filtre à quatre drapeaux exclut tous les runs qui oscillent (`src/detector.py` L352) | **D11 appliqué** |
| 50 | Une fin plus ambitieuse | Demanderait des faits et sources nouvelles | Plus tard |

## 4. npj, première soumission (page *Submission guidelines* relue le 2026-10-09)

- Le format n'est exigé qu'à l'acceptation (« do not need to adhere to our formatting requirements at the point of initial submission »).
- À la première soumission : un seul fichier, PDF compilé ; figures dans le texte ou groupées en fin ; chaque légende sur la même page que sa figure. Notre PDF est conforme : aucun « Float too large » ; pages vérifiées à l'œil.
- « Tables at the end » et « legends … after references » relèvent des consignes de préparation finale.
- *Materials availability* n'est pas demandée : seules *Data availability* et *Code availability* le sont ; la politique Nature Portfolio demande d'indiquer les restrictions sur des « unique materials », et l'atlas n'en a pas.

## 5. Changements appliqués (`7021cce`, 2026-10-09, validés par l'auteur)

D1–D15, texte exact dans le commit :
- D1 Tableau 1 appelé au §2.1 ;
- D2 H1 définie ;
- D3 déclencheur assisté par défaut ;
- D4 « window-length artefact » ;
- D5 Vt en mL ;
- D6 suppression de *Materials availability* ;
- D7 ≥ 300 s plutôt que 120 s ;
- D8 définition de la divergence ;
- D9 écarts H/F ;
- D10 déclencheur par défaut en Méthodes ;
- D11 quatrième mise en garde ;
- D12 sans sédatif ni curare (§S15) ;
- D13 dominance de la PAS hors artefact ;
- D14 « instability » → « oscillation » (papier, métadonnées, monographie) ;
- D15 corps jeunes et minces (papier et §S2).

Compilation : 0 erreur, 24 et 58 pages inchangées ; contrôles du dépôt au vert.

## 5 bis. Suites du 2026-10-09 (décisions de l'auteur ; aucune citation de message)

- Passages pédiatriques : retirés dans la Discussion (limite (iii), phrase
  « pediatric translation layer ») et dans le supplément (§S2 (iii) ; §S5 :
  titre « Adult-only tuning. », phrase finale retirée), commit `dad75bd`.
  L'Introduction (L146) garde sa deuxième raison (choix de l'auteur). Le
  nettoyage du plan de thèse dans la monographie et le dépôt se fera à la
  création du dépôt public ; `preregistration.md` reste intact.
- Q1 tranchée : affiliations d'A.W. 3, 4, 6 ; Q3 tranchée : sigle écrit
  « PEDIATRICS » (à signaler dans la liste de la v56 pour P.J. et M.S.) ;
  Q2 : ville confirmée, nom d'A.W. conservé dans le dépôt ; Q7 : accord
  pour soumettre. Commit `874fced`.
- Q4 : nouvelle phrase du §2.3 appliquée (`874fced`), acceptée par A.W. ;
  à confirmer par M.S. en tête de la liste des changements de la v56. Le
  §S8.4 et la monographie gardent « shift … toward controlled ventilation »
  (contenu validé par M.S.), à lui soumettre en même temps.

## 6. Questions ouvertes

- **Q1** (A.W.) Affiliation : 2,3,4,6 ou 3,4,6 ?
- **Q2** (A.W.) Ville de l'affiliation INSERM ; noms ou initiales dans les fichiers du dépôt public.
- **Q3** (P.J.) « PE-DIATRICS » ou autre forme officielle ?
- **Q4** (A.W. et M.S., C21 + C32) Phrase proposée :
  - « In a real patient, any fixed trigger threshold, this one included, leaves efforts too weak to reach it unrewarded, a form of patient–ventilator dyssynchrony that is clinically undesirable. »
  - Sources relues le 2026-10-09 : Thille 2006 (« Ineffective triggering was associated with a less sensitive inspiratory trigger ») ; Blanch 2015 (association avec la mortalité, causalité non établie). « clinically undesirable » est conservé (registre des références : ne pas renforcer).
  - La mise en garde actuelle a été validée par M.S. (`d83fdf4`, reformulée dans `d0361de`).
- **Q5** (auteur) Passages pédiatriques (C3, C45, C47).
- **Q6** (auteur) Pistes facultatives : C12, C42, C48, C50.
- **Q7** (A.W.) OK pour soumettre.

## 7. Suite du 2026-10-12

- Q4 : la phrase du §2.3 reprend le terme et la définition de la source citée,
  « fail to trigger a breath (ineffective triggering) » (Thille 2006, texte
  intégral relu le 2026-10-12 : « ineffective triggering occurs when the
  patient's inspiratory effort fails to trigger a ventilator breath » ;
  « Factors associated with ineffective triggering include a weak inspiratory
  effort »), `61884c5`. Alignement sur décision de l'auteur, `5fe2378` :
  légende de la Figure 4 (« not a clinical recommendation »), §S8.4 et
  monographie §4.2 (même phrase que le §2.3, sans « shift … toward controlled
  ventilation »), lettre (« adjustments »). Re-gels 57 (envoyé) et 58.
- **Erratum, message de `5fe2378`** : il justifie le changement de légende en
  écrivant qu'un déclencheur en pression à −2 cmH₂O « is a setting used in
  clinical ventilation ». Aucune source primaire n'a été trouvée en séance
  (Thille 2006 utilise un déclenchement en débit ; le résumé de Sassoon 2011,
  PMID 21235837, n'en dit rien). Cette phrase du message est donc **non
  vérifiée**. Le manuscrit ne l'affirme nulle part : la légende dit seulement
  « not a clinical recommendation », les mots du §2.3 et du §S8.4.
- **Erratum 2, même message** : « so a real patient is not moved to controlled
  ventilation » généralise trop. Seuls les efforts trop faibles pour atteindre
  le seuil restent sans cycle ; chez un patient dont les efforts sont presque
  tous trop faibles, l'effet revient à une ventilation contrôlée (Sassoon 2011,
  résumé : les efforts perdus sont « aggravated by respiratory muscle
  weakness »). Le manuscrit n'affirme ni l'un ni l'autre.
- **Erratum 3, même message** : « The paper calls the −2 cmH2O lock a
  data-generation lever, not a correction » est inexact : le titre de la légende
  de la Figure 4 dit « Two operator-actionable corrections surfaced by the
  atlas ». Le papier emploie les deux mots (« lever » au §2.3, « corrections »
  pour les deux panneaux de la Figure 4) ; le changement de la lettre
  (« fixes » → « adjustments ») reste une décision de l'auteur, sans
  contradiction avec le papier.
