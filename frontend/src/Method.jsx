export default function Method() {
  return (
    <article className="page method">
      <h1>La méthode</h1>
      <p className="lead">Comment GRAVITY CARE transforme des mesures en statuts et en alertes, et où s'arrêtent ses limites.</p>

      <h2>1. Une ligne de base par astronaute</h2>
      <p>Pour chaque indicateur, on calcule la moyenne et l'écart-type des <strong>7 premiers jours</strong> de l'astronaute.
        C'est sa « normale » à lui. Pendant ces 7 jours, le statut est <em>Calibration</em>.</p>

      <h2>2. Une valeur par jour</h2>
      <p>Les capteurs envoient plusieurs mesures par jour. On les regroupe : <strong>moyenne</strong> pour les signaux continus
        (fréquence cardiaque, SpO2, HRV), <strong>somme</strong> pour les totaux (sommeil, activité, radiations).</p>

      <h2>3. L'écart (z-score)</h2>
      <p>z = (valeur du jour − moyenne de base) / écart-type de base. Il indique de combien d'écarts-types la valeur s'éloigne
        de la normale de l'astronaute. L'écart-type a un plancher de 2 % de la moyenne pour éviter les divisions par presque zéro.</p>

      <h2>4. Les règles de démonstration</h2>
      <table className="table">
        <thead><tr><th>Statut</th><th>Condition</th></tr></thead>
        <tbody>
          <tr><td>Orange · à surveiller</td><td>|z| ≥ 2 pendant 2 jours consécutifs</td></tr>
          <tr><td>Rouge · attention requise</td><td>|z| ≥ 3 un jour, ou |z| ≥ 2 pendant 4 jours consécutifs</td></tr>
        </tbody>
      </table>
      <p className="notice">Ces règles sont des <strong>règles de démonstration</strong>. Ce ne sont pas des seuils médicaux et elles n'ont
        aucune valeur clinique. Un vrai déploiement exigerait une validation par des cliniciens.</p>

      <h2>5. Prévision de tendance</h2>
      <p>Une régression linéaire sur les 7 derniers jours projette 3 jours (ligne en pointillé). C'est une estimation grossière,
        affichée avec un avertissement d'incertitude.</p>

      <h2>6. Capteurs et données</h2>
      <p>Les mesures sont <strong>simulées</strong> : nous n'avons ni capteurs réels ni données d'astronautes. Un simulateur
        joue le rôle des appareils. La source des mesures est séparée de l'analyse : un vrai flux pourrait la remplacer.
        Si un astronaute n'envoie plus rien depuis plus de 24 h, l'interface signale des « capteurs silencieux ».</p>

      <h2>7. Rôles</h2>
      <table className="table">
        <thead><tr><th>Rôle</th><th>Peut</th></tr></thead>
        <tbody>
          <tr><td>Astronaute</td><td>Voir son propre suivi, accuser réception de ses alertes</td></tr>
          <tr><td>Médecin au sol</td><td>Tout voir, annoter, accuser réception, exporter un rapport, lancer la simulation</td></tr>
          <tr><td>Responsable de mission</td><td>Consulter l'équipage, lancer la simulation</td></tr>
        </tbody>
      </table>

      <h2>8. Limites connues</h2>
      <ul>
        <li>La valeur absolue de z déclenche aussi une alerte sur une hausse (par exemple du sommeil).</li>
        <li>« Jours consécutifs » signifie jours consécutifs ayant des mesures.</li>
        <li>Faux positifs (alerte à tort) et faux négatifs (écart manqué) sont possibles, quelle que soit la règle.</li>
        <li>Sécurité de niveau prototype : ne pas utiliser en production.</li>
      </ul>
    </article>
  )
}
