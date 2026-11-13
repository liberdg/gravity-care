import { HeroArt, Icon, INDICATOR_ICON } from './Art.jsx'

const STEPS = [
  ['sensor', 'Collecter', 'Des capteurs envoient les mesures automatiquement. Personne ne saisit rien.'],
  ['chart', 'Analyser', 'Chaque astronaute est comparé à sa propre ligne de base, calculée sur ses 7 premiers jours.'],
  ['shield', 'Évaluer', 'Un statut clair : normal, à surveiller ou attention requise.'],
  ['bell', 'Alerter', 'Chaque alerte dit quelle valeur, quel écart et quelle règle l\'a déclenchée.'],
  ['search', 'Accompagner', 'Courbes, prévision de tendance, notes du médecin et rapport exportable.'],
]

const INDICATORS = [
  ['heart_rate_rest', 'Fréquence cardiaque au repos', 'Reflète l\'adaptation du cœur à la microgravité et à l\'effort.', 'Dépend de l\'activité du moment.'],
  ['spo2', 'SpO2', 'Part d\'oxygène dans le sang, mesurée par un oxymètre.', 'Le capteur optique est bruité.'],
  ['sleep_hours', 'Sommeil', 'Durée de sommeil, indice de récupération et de rythme jour-nuit.', 'Mesure indirecte, par montre ou capteur.'],
  ['activity_minutes', 'Activité physique', 'Minutes d\'exercice, utiles pour limiter la perte osseuse et musculaire.', 'Indirect pour la santé des os.'],
  ['hrv', 'Variabilité cardiaque (HRV)', 'Indice indirect de fatigue ou de stress, dérivé du capteur cardiaque.', 'À interpréter avec prudence.'],
  ['radiation_dose', 'Radiations (simulé)', 'Illustre le suivi d\'une dose cumulée.', 'Valeur fictive, sans portée scientifique.'],
]

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-text">
          <span className="pill">Prototype · données simulées · pas un dispositif médical</span>
          <h1>Surveiller la santé des astronautes, même loin de la Terre.</h1>
          <p className="lead">
            GRAVITY CARE compare chaque astronaute à lui-même, explique chaque alerte et reste utile quand la
            communication avec le sol est difficile.
          </p>
          <div className="cta">
            <a className="btn primary" href="#/dashboard">Ouvrir le tableau de bord</a>
            <a className="btn" href="#/methode">Comprendre la méthode</a>
          </div>
          <p className="small">Projet du NASA Space Apps Challenge 2026 · EPL, Université de Lomé</p>
        </div>
        <HeroArt />
      </section>

      <section className="block">
        <h2>Pourquoi ce projet</h2>
        <div className="grid3">
          <div className="tile"><h3>Missions longues</h3><p>Microgravité, radiations, sommeil perturbé, isolement : la santé de l'équipage est mise à l'épreuve pendant des mois.</p></div>
          <div className="tile"><h3>Le sol est loin</h3><p>Plus la mission s'éloigne de la Terre, plus le soutien médical depuis le sol est lent, parfois interrompu.</p></div>
          <div className="tile"><h3>Besoin d'autonomie</h3><p>L'équipage a besoin d'un outil qui repère un écart tôt et l'explique simplement, sans connexion permanente.</p></div>
        </div>
      </section>

      <section className="block">
        <h2>Comment ça marche</h2>
        <div className="steps">
          {STEPS.map(([icon, title, text], i) => (
            <div className="step" key={title}>
              <div className="step-icon"><Icon name={icon} size={26} /></div>
              <span className="step-n">{i + 1}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="block">
        <h2>Six indicateurs suivis</h2>
        <div className="grid3">
          {INDICATORS.map(([key, title, text, limit]) => (
            <div className="tile" key={key}>
              <div className="tile-head"><span className="ico"><Icon name={INDICATOR_ICON[key]} size={22} /></span><h3>{title}</h3></div>
              <p>{text}</p>
              <p className="limit">Limite : {limit}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="block">
        <h2>Ce qui nous distingue</h2>
        <div className="grid2">
          <div className="tile"><h3>Comparé à soi-même</h3><p>Pas de seuils médicaux inventés : chaque astronaute a sa propre ligne de base.</p></div>
          <div className="tile"><h3>Des alertes expliquées</h3><p>Valeur, base, écart et règle appliquée sont affichés. On comprend pourquoi.</p></div>
          <div className="tile"><h3>Collecte automatique</h3><p>Les mesures arrivent des capteurs (simulés ici). Un vrai flux pourrait remplacer le simulateur sans toucher au reste.</p></div>
          <div className="tile"><h3>Utilisable hors-ligne</h3><p>L'interface et les dernières données consultées restent disponibles sans connexion.</p></div>
        </div>
      </section>

      <section className="block honesty">
        <div className="honesty-icon"><Icon name="shield" size={34} /></div>
        <div>
          <h2>Rigueur et honnêteté</h2>
          <ul>
            <li>Toutes les données sont <strong>simulées</strong> et marquées comme telles, à l'écran et en base.</li>
            <li>Les règles d'alerte sont des <strong>règles de démonstration</strong>, pas des seuils médicaux.</li>
            <li>Aucun diagnostic. Le prototype aide à surveiller, il ne remplace pas les professionnels de santé.</li>
            <li>Les faux positifs et les faux négatifs existent : nous les expliquons au lieu de les cacher.</li>
          </ul>
        </div>
      </section>

      <section className="block final">
        <h2>Essayez la démonstration</h2>
        <p>Connectez-vous avec un compte de démonstration, puis cliquez sur « Lancer la simulation des capteurs ».</p>
        <a className="btn primary" href="#/dashboard">Ouvrir le tableau de bord</a>
      </section>

      <footer className="footer">
        GRAVITY CARE · NASA Space Apps Challenge 2026 · Projet tutoré, EPL, Université de Lomé · Données simulées, usage pédagogique
      </footer>
    </div>
  )
}
