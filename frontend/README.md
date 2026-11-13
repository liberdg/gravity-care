# GRAVITY CARE : frontend

Prototype de hackathon. **Données simulées, pas un dispositif médical.**

```
npm install
npm run dev        # http://localhost:5173 (le backend doit tourner sur le port 8000)
npm test
npm run build      # le mode hors-ligne (service worker) est actif dans le build
```

Écrans : connexion · équipage (statut de chacun, capteurs silencieux) · page astronaute (alertes expliquées,
recommandations informatives, 6 courbes avec prévision en pointillé, accusé de réception, notes et rapport pour le
médecin). Aucun formulaire de saisie de mesure : elles arrivent des capteurs.
