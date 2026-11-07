# Fork nexk — Dreame Vacuum sans DVC

Fork de [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) (MIT), branche `nexk`.

Différences avec l'upstream (tag de base indiqué dans `manifest.json`) :

- `custom_components/dreame_vacuum/frontend.py` supprimé : code obscurci gérant la licence
  « Dreame Vacuum Card » (DVC), qui contacte `api.tasshack.com` et fait exécuter dans le
  navigateur du JavaScript téléchargé et signé par l'auteur quand une clé DVC est saisie.
- Constante `FRONTEND` retirée de `const.py` (bundle JS obscurci de la carte DVC, auto-injecté
  dans tous les tableaux de bord).
- `hacs.json` : installation depuis le dépôt (plus de `zip_release`), pour que la Marketplace
  installe exactement ce code.

La suppression de `frontend.py` est prévue par l'upstream (`__init__.py` : « Dynamically load
frontend.py so that it can be easily stripped ») : sans lui, l'étape DVC du config flow et la
notification DVC sont simplement ignorées. Le reste du code est identique à l'upstream.

Pour l'affichage de la carte, utiliser PiotrMachowski/lovelace-xiaomi-vacuum-map-card.

## Mise à jour automatique

Le workflow `.github/workflows/sync-upstream.yml` vérifie chaque jour la dernière release
stable de Tasshack. Pour une nouvelle version `vX.Y.Z`, il reconstruit la branche `nexk` sur
ce tag, applique `.github/scripts/strip_dvc.py` et publie la release `vX.Y.Z.1`. Si la
structure upstream change (frontend.py n'est plus optionnel, code DVC ailleurs…), le script
échoue et rien n'est publié : GitHub envoie alors un e-mail d'échec du workflow.
