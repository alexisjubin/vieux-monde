"use strict";

const FICHIERS = [
  "anciens",
  "empire",
  "empire-sigmar",
  "empire-electeurs",
  "ouest",
  "nord-et-orient",
  "nains-et-peaux-vertes",
  "elfes",
  "morts-vivants",
  "skavens-et-lustrie",
  "fin-des-temps",
].map((nom) => `donnees/evenements-${nom}.json`);

const LANGUES = ["fr", "en", "de"];

// À augmenter à chaque publication qui change les données ou la carte, pour
// que les navigateurs ne gardent pas l'ancienne version en cache.
const VERSION = 12;

const TEXTES = {
  fr: {
    titreDocument: "Le Vieux Monde, une chronologie",
    titre: "Le Vieux Monde",
    chapeau: "Une chronologie de l'univers de Warhammer Fantasy et de The Old World, des Anciens à la Fin des Temps. Chaque événement renvoie aux livres et aux pages qui en parlent, et signale quand les sources ne s'accordent pas.",
    vue: "Vue d'ensemble",
    legendeFrise: "L'échelle n'est pas linéaire : chaque âge a sa propre largeur, pour que les huit mille ans restent lisibles. La bande hachurée marque l'époque où se déroule The Old World.",
    epoqueTow: "Époque de The Old World",
    carte: "Carte du Vieux Monde",
    cadrageMonde: "Monde",
    cadrageVieuxMonde: "Vieux Monde",
    calques: "Calques",
    nomsCalques: { lieux: "Lieux de la chronologie", regions: "Noms des régions", mers: "Noms des mers", frontieres: "Frontières des provinces", provinces: "Provinces", colonies: "Colonies" },
    legendeCarte: "Carte redessinée d'après la carte du monde de Total War: Warhammer III et les cartes de Games Workshop. Molette, pincement ou double clic pour zoomer, glisser pour se déplacer. Les colonies et les provinces apparaissent en zoomant. Cliquez sur un lieu pour ne garder que ses événements.",
    aucunLieu: "Aucun lieu choisi.",
    evenementsLieu: (n) => (n > 1 ? `${n} événements` : `${n} événement`),
    voirChronique: "Voir dans la chronique",
    typesLieux: { capitale: "Capitale", ville: "Ville", forteresse: "Forteresse", site: "Site", ruine: "Ruine", bataille: "Champ de bataille" },
    filtrer: "Filtrer",
    chercher: "Chercher",
    exempleRecherche: "Nagash, Altdorf, peste…",
    factions: "Factions",
    regions: "Régions",
    lieux: "Lieux",
    fiabilite: "Fiabilité",
    importance: "Importance",
    importances: { 3: "Tournants majeurs", 2: "Événements importants", 1: "Détails" },
    retirer: "Retirer",
    toutAfficher: "Tout afficher",
    compte: (n, total) => `${n} sur ${total}`,
    sources: (n, fiab) => `Sources (${n}), ${fiab}`,
    vide: "Aucun événement ne correspond à ces filtres.",
    erreur: (m) => `Impossible de charger les données (${m}).`,
    pied: `Projet personnel d'Alexis Jubin. Warhammer, The Old World et tous les noms associés appartiennent à Games Workshop. Les résumés sont rédigés à partir des livres officiels, de <a href="https://whfb.lexicanum.com/">Lexicanum</a> et de la Bibliothèque Impériale. Une erreur ou une source manquante ? <a href="mailto:aj@alexisjubin.com">Écrivez-moi</a>.`,
    langue: "Langue",
    nomLangue: "Français",
    entrer: "Entrer",
    annee: (a) => (a < 0 ? `${-a} av. CI` : `${a} CI`),
    nombre: (a) => String(Math.abs(a)),
    jusqua: " - ",
    vers: (t) => `vers ${t}`,
  },
  en: {
    titreDocument: "The Old World, a chronology",
    titre: "The Old World",
    chapeau: "A chronology of the Warhammer Fantasy and The Old World setting, from the Old Ones to the End Times. Every event points to the books and pages that cover it, and flags where the sources disagree.",
    vue: "Overview",
    legendeFrise: "The scale is not linear: each age has its own width, so that eight thousand years stay readable. The hatched band marks the period in which The Old World is set.",
    epoqueTow: "The Old World period",
    carte: "Map of the Old World",
    cadrageMonde: "World",
    cadrageVieuxMonde: "Old World",
    calques: "Layers",
    nomsCalques: { lieux: "Chronicle places", regions: "Region names", mers: "Sea names", frontieres: "Province borders", provinces: "Provinces", colonies: "Settlements" },
    legendeCarte: "Redrawn after the Total War: Warhammer III world map and the Games Workshop maps. Scroll, pinch or double-click to zoom, drag to move. Settlements and provinces appear as you zoom in. Click a place to keep only its events.",
    aucunLieu: "No place selected.",
    evenementsLieu: (n) => (n > 1 ? `${n} events` : `${n} event`),
    voirChronique: "Show in the chronicle",
    typesLieux: { capitale: "Capital", ville: "City", forteresse: "Fortress", site: "Site", ruine: "Ruin", bataille: "Battlefield" },
    filtrer: "Filter",
    chercher: "Search",
    exempleRecherche: "Nagash, Altdorf, plague…",
    factions: "Factions",
    regions: "Regions",
    lieux: "Places",
    fiabilite: "Reliability",
    importance: "Importance",
    importances: { 3: "Turning points", 2: "Major events", 1: "Details" },
    retirer: "Remove",
    toutAfficher: "Show everything",
    compte: (n, total) => `${n} of ${total}`,
    sources: (n, fiab) => `Sources (${n}), ${fiab}`,
    vide: "No event matches these filters.",
    erreur: (m) => `Could not load the data (${m}).`,
    pied: `A personal project by Alexis Jubin. Warhammer, The Old World and all associated names belong to Games Workshop. The summaries are written from the official books, <a href="https://whfb.lexicanum.com/">Lexicanum</a> and the Imperial Library. Found a mistake or a missing source? <a href="mailto:aj@alexisjubin.com">Write to me</a>.`,
    langue: "Language",
    nomLangue: "English",
    entrer: "Enter",
    annee: (a) => `${a} IC`,
    nombre: (a) => String(a),
    jusqua: " to ",
    vers: (t) => `c. ${t}`,
  },
  de: {
    titreDocument: "Die Alte Welt, eine Chronik",
    titre: "Die Alte Welt",
    chapeau: "Eine Chronik der Welt von Warhammer Fantasy und The Old World, von den Alten bis zur Endzeit. Jedes Ereignis verweist auf die Bücher und Seiten, die davon berichten, und zeigt an, wo sich die Quellen widersprechen.",
    vue: "Überblick",
    legendeFrise: "Der Maßstab ist nicht linear: Jedes Zeitalter hat seine eigene Breite, damit achttausend Jahre lesbar bleiben. Das schraffierte Band markiert die Zeit, in der The Old World spielt.",
    epoqueTow: "Zeit von The Old World",
    carte: "Karte der Alten Welt",
    cadrageMonde: "Welt",
    cadrageVieuxMonde: "Alte Welt",
    calques: "Ebenen",
    nomsCalques: { lieux: "Orte der Chronik", regions: "Regionsnamen", mers: "Meeresnamen", frontieres: "Provinzgrenzen", provinces: "Provinzen", colonies: "Siedlungen" },
    legendeCarte: "Neu gezeichnet nach der Weltkarte von Total War: Warhammer III und den Karten von Games Workshop. Mausrad, Zwei-Finger-Geste oder Doppelklick zum Zoomen, Ziehen zum Verschieben. Siedlungen und Provinzen erscheinen beim Hineinzoomen. Ein Klick auf einen Ort zeigt nur seine Ereignisse.",
    aucunLieu: "Kein Ort ausgewählt.",
    evenementsLieu: (n) => (n > 1 ? `${n} Ereignisse` : `${n} Ereignis`),
    voirChronique: "In der Chronik zeigen",
    typesLieux: { capitale: "Hauptstadt", ville: "Stadt", forteresse: "Festung", site: "Ort", ruine: "Ruine", bataille: "Schlachtfeld" },
    filtrer: "Filtern",
    chercher: "Suchen",
    exempleRecherche: "Nagash, Altdorf, Pest…",
    factions: "Fraktionen",
    regions: "Regionen",
    lieux: "Orte",
    fiabilite: "Verlässlichkeit",
    importance: "Bedeutung",
    importances: { 3: "Wendepunkte", 2: "Wichtige Ereignisse", 1: "Einzelheiten" },
    retirer: "Entfernen",
    toutAfficher: "Alles zeigen",
    compte: (n, total) => `${n} von ${total}`,
    sources: (n, fiab) => `Quellen (${n}), ${fiab}`,
    vide: "Kein Ereignis entspricht diesen Filtern.",
    erreur: (m) => `Die Daten konnten nicht geladen werden (${m}).`,
    pied: `Ein privates Projekt von Alexis Jubin. Warhammer, The Old World und alle zugehörigen Namen gehören Games Workshop. Die Zusammenfassungen beruhen auf den offiziellen Büchern, <a href="https://whfb.lexicanum.com/">Lexicanum</a> und der Imperial Library. Ein Fehler oder eine fehlende Quelle? <a href="mailto:aj@alexisjubin.com">Schreiben Sie mir</a>.`,
    langue: "Sprache",
    nomLangue: "Deutsch",
    entrer: "Eintreten",
    annee: (a) => `${a} IK`,
    nombre: (a) => String(a),
    jusqua: " bis ",
    vers: (t) => `um ${t}`,
  },
};

const etat = {
  langue: "fr",
  ref: null,
  carte: null,
  evenements: [],
  factions: new Set(),
  regions: new Set(),
  fiabilites: new Set(),
  importances: new Set(),
  lieux: new Set(),
  calquesMasques: new Set(),
  texte: "",
};

const $ = (sel) => document.querySelector(sel);
const SVG = "http://www.w3.org/2000/svg";

const T = () => TEXTES[etat.langue];

// Un texte des données est soit une chaîne, soit un objet { fr, en, de }.
function t(valeur) {
  if (valeur == null || typeof valeur === "string") return valeur ?? "";
  return valeur[etat.langue] || valeur.fr || "";
}

function formaterAnnee(annee) {
  return T().annee(annee);
}

function formaterDate(ev) {
  let texte = formaterAnnee(ev.annee);
  if (ev.fin != null && ev.fin !== ev.annee) {
    texte = Math.sign(ev.annee) === Math.sign(ev.fin)
      ? `${T().nombre(ev.annee)}${T().jusqua}${formaterAnnee(ev.fin)}`
      : `${formaterAnnee(ev.annee)}${T().jusqua}${formaterAnnee(ev.fin)}`;
  }
  return ev.approx ? T().vers(texte) : texte;
}

// Position (de 0 à 1) d'une année sur la frise : chaque âge a une largeur
// proportionnelle à son poids, et l'année est placée linéairement dans son âge.
function position(annee) {
  const eres = etat.ref.eres;
  const total = eres.reduce((s, e) => s + e.poids, 0);
  let cumul = 0;
  for (const ere of eres) {
    if (annee < ere.fin || ere === eres[eres.length - 1]) {
      const dedans = Math.min(Math.max((annee - ere.debut) / (ere.fin - ere.debut), 0), 1);
      return (cumul + dedans * ere.poids) / total;
    }
    cumul += ere.poids;
  }
  return 1;
}

function retenu(ev) {
  if (etat.factions.size && !ev.factions.some((f) => etat.factions.has(f))) return false;
  if (etat.regions.size && !ev.regions.some((r) => etat.regions.has(r))) return false;
  if (etat.lieux.size && !(ev.lieux ?? []).some((l) => etat.lieux.has(l))) return false;
  if (etat.fiabilites.size && !etat.fiabilites.has(ev.fiabilite)) return false;
  if (etat.importances.size && !etat.importances.has(String(ev.importance))) return false;
  if (etat.texte && !botte(ev).includes(etat.texte)) return false;
  return true;
}

// Texte de recherche d'un événement, sans accents, calculé une fois par langue.
const bottes = new Map();
function botte(ev) {
  const cle = `${etat.langue}:${ev.id}`;
  if (!bottes.has(cle)) bottes.set(cle, sansAccents(`${t(ev.titre)} ${t(ev.resume)} ${t(ev.note)}`));
  return bottes.get(cle);
}

function sansAccents(s) {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function index(liste) {
  return Object.fromEntries(liste.map((x) => [x.id, x]));
}

function creer(balise, attributs = {}, ...enfants) {
  const el = document.createElement(balise);
  for (const [cle, val] of Object.entries(attributs)) {
    if (cle === "style") el.style.cssText = val;
    else if (cle.startsWith("data-")) el.setAttribute(cle, val);
    else el[cle] = val;
  }
  el.append(...enfants.filter((e) => e != null));
  return el;
}

function creerSvg(balise, attributs = {}, texte) {
  const el = document.createElementNS(SVG, balise);
  for (const [cle, val] of Object.entries(attributs)) el.setAttribute(cle, val);
  if (texte != null) el.textContent = texte;
  return el;
}

/* Langue */

function langueInitiale() {
  const demandee = new URLSearchParams(location.search).get("lang");
  if (LANGUES.includes(demandee)) return demandee;
  try {
    const gardee = localStorage.getItem("langue");
    if (LANGUES.includes(gardee)) return gardee;
  } catch {
    // Stockage indisponible (navigation privée) : on demandera à chaque visite.
  }
  return null;
}

function langueNavigateur() {
  for (const l of navigator.languages ?? [navigator.language]) {
    const court = (l ?? "").slice(0, 2).toLowerCase();
    if (LANGUES.includes(court)) return court;
  }
  return "fr";
}

function choisirLangue(langue) {
  etat.langue = langue;
  try {
    localStorage.setItem("langue", langue);
  } catch {
    // Sans stockage, le choix vaut pour cette visite.
  }
  traduirePage();
  if (etat.ref) toutConstruire();
}

function traduirePage() {
  const textes = T();
  document.documentElement.lang = etat.langue;
  document.title = textes.titreDocument;
  document.querySelectorAll("[data-t]").forEach((el) => (el.textContent = textes[el.dataset.t]));
  $("#pied").innerHTML = textes.pied;
  $("#recherche").placeholder = textes.exempleRecherche;
  document.querySelectorAll(".langues button").forEach((b) =>
    b.setAttribute("aria-pressed", String(b.value === etat.langue)),
  );
}

function construireSelecteurLangue() {
  const zone = $("#langues");
  for (const l of LANGUES) {
    const bouton = creer("button", { type: "button", value: l, textContent: l.toUpperCase(), title: TEXTES[l].nomLangue });
    bouton.setAttribute("lang", l);
    bouton.addEventListener("click", () => choisirLangue(l));
    zone.append(bouton);
  }
}

// À la première visite, on demande la langue avant d'afficher le site.
function demanderLangue() {
  return new Promise((resoudre) => {
    const accueil = $("#accueil");
    const proposee = langueNavigateur();
    const choix = accueil.querySelector(".choix-langues");
    for (const l of LANGUES) {
      const bouton = creer("button", { type: "button", lang: l },
        creer("span", { className: "nom-langue", textContent: TEXTES[l].nomLangue }),
        creer("span", { className: "titre-langue", textContent: TEXTES[l].titre }),
      );
      bouton.addEventListener("click", () => {
        accueil.close();
        resoudre(l);
      });
      choix.append(bouton);
      if (l === proposee) bouton.autofocus = true;
    }
    accueil.addEventListener("cancel", (e) => e.preventDefault());
    accueil.showModal();
  });
}

/* Frise d'ensemble */

function construireFrise() {
  const frise = $("#frise");
  frise.replaceChildren();
  const total = etat.ref.eres.reduce((s, e) => s + e.poids, 0);

  for (const ere of etat.ref.eres) {
    frise.append(
      creer("div", { className: "age", style: `flex: ${ere.poids / total} 1 0` },
        creer("span", { className: "age-debut", textContent: String(ere.debut) }),
        creer("span", { className: "age-nom", textContent: t(ere.nom) }),
      ),
    );
  }

  const tow = etat.ref.epoque_tow;
  if (tow) {
    const g = position(tow.debut) * 100;
    const d = position(tow.fin) * 100;
    frise.append(creer("div", {
      className: "epoque-tow",
      title: `${T().epoqueTow}, ${formaterAnnee(tow.debut)}${T().jusqua}${formaterAnnee(tow.fin)}`,
      style: `left: ${g}%; width: ${d - g}%`,
    }));
  }

  const factions = index(etat.ref.factions);
  for (const ev of etat.evenements) {
    const couleur = factions[ev.factions[0]]?.couleur ?? "var(--encre)";
    const libelle = `${formaterDate(ev)}, ${t(ev.titre)}`;
    const trait = creer("button", {
      type: "button",
      className: "trait",
      title: libelle,
      "data-id": ev.id,
      "data-importance": ev.importance,
      style: `left: ${position(ev.annee) * 100}%; --couleur: ${couleur}`,
    });
    trait.setAttribute("role", "listitem");
    trait.setAttribute("aria-label", libelle);
    trait.addEventListener("click", () => montrer(ev.id));
    frise.append(trait);
  }
}

function montrer(id, fluide = true) {
  const cible = chroniqueConstruite.evenements.get(id);
  if (!cible) return;
  // L'événement est masqué par un filtre : on lève les filtres d'abord.
  if (cible.hidden) effacerFiltres();
  document.querySelectorAll(".evenement.choisi").forEach((e) => e.classList.remove("choisi"));
  cible.classList.add("choisi");
  evoquerLieux(etat.evenements.find((ev) => ev.id === id)?.lieux ?? []);
  cible.scrollIntoView({ behavior: fluide ? "smooth" : "auto", block: "start" });
  history.replaceState(null, "", `${location.search}#${id}`);
}

/* Carte */

// La carte est un SVG (repère de donnees/carte.json) qu'on parcourt en
// changeant son viewBox. vue.x, vue.y et vue.l décrivent la portion visible.
// Le fond est fait de tuiles d'image (outils/carte/tuiles.py), les noms et
// les lieux sont posés par-dessus en SVG.
const vue = { x: 0, y: 0, l: 0, largeur: 0, hauteur: 0 };
const tuiles = { manifeste: null, chargees: new Map(), groupes: new Map() };
const ZOOM_MAX = 16;
const CADRAGES = {
  monde: null,
  "vieux-monde": [1600, 600, 2100],
};

async function chargerFondDeCarte() {
  const reponse = await fetch(`tuiles/tuiles.json?v=${VERSION}`);
  if (!reponse.ok) throw new Error(`tuiles.json : ${reponse.status}`);
  const m = (tuiles.manifeste = await reponse.json());
  const svg = creerSvg("svg", { viewBox: `0 0 ${m.largeur} ${m.hauteur}`, role: "group", preserveAspectRatio: "xMidYMid meet" });
  const fond = creerSvg("g", { "aria-hidden": "true" });
  fond.append(image("tuiles/fond.webp", 0, 0, m.largeur, m.hauteur));
  for (const niveau of m.niveaux) {
    const groupe = creerSvg("g");
    tuiles.groupes.set(niveau, groupe);
    fond.append(groupe);
  }
  svg.append(
    fond,
    creerSvg("g", { id: "zones-carte" }),
    creerSvg("g", { id: "frontieres-carte" }),
    creerSvg("g", { id: "provinces-carte" }),
    creerSvg("g", { id: "colonies-carte" }),
    creerSvg("g", { id: "etiquettes-carte" }),
    creerSvg("g", { id: "lieux-carte" }),
  );
  $("#carte").append(svg);
  Object.assign(vue, { largeur: m.largeur, hauteur: m.hauteur });
  brancherDeplacements(svg);
  new ResizeObserver(() => {
    if (vue.l) cadrer(vue.x + vue.l / 2, vue.y + hauteurVisible() / 2, vue.l);
  }).observe($("#carte"));
}

function image(href, x, y, l, h) {
  return creerSvg("image", { href: `${href}?v=${VERSION}`, x, y, width: l, height: h, preserveAspectRatio: "none" });
}

// Charge les tuiles du niveau assez fin pour l'écran, sur la zone visible et
// une marge autour. Les niveaux plus grossiers restent dessous le temps que
// les tuiles fines arrivent, les niveaux plus fins sont masqués.
function majTuiles() {
  const m = tuiles.manifeste;
  if (!m) return;
  const pixelsParUnite = (boiteCarte().width * (window.devicePixelRatio || 1)) / vue.l;
  const niveau = m.niveaux.find((n) => n >= pixelsParUnite * 0.85) ?? m.niveaux.at(-1);
  const utile = pixelsParUnite > m.apercu * 1.2;
  for (const [n, groupe] of tuiles.groupes) groupe.style.display = utile && n <= niveau ? "" : "none";
  if (!utile) return;

  const cote = m.taille / niveau;
  const marge = vue.l * 0.25;
  const h = hauteurVisible();
  const i0 = Math.max(0, Math.floor((vue.x - marge) / cote));
  const i1 = Math.min(Math.ceil(m.largeur / cote) - 1, Math.floor((vue.x + vue.l + marge) / cote));
  const j0 = Math.max(0, Math.floor((vue.y - marge) / cote));
  const j1 = Math.min(Math.ceil(m.hauteur / cote) - 1, Math.floor((vue.y + h + marge) / cote));
  for (let j = j0; j <= j1; j++) {
    for (let i = i0; i <= i1; i++) {
      const cle = `${niveau}/${i}-${j}`;
      if (tuiles.chargees.has(cle)) continue;
      const x = i * cote;
      const y = j * cote;
      const tuile = image(`tuiles/${cle}.webp`, x, y, Math.min(cote, m.largeur - x), Math.min(cote, m.hauteur - y));
      tuiles.chargees.set(cle, tuile);
      tuiles.groupes.get(niveau).append(tuile);
    }
  }
}

function boiteCarte() {
  const b = $("#carte").getBoundingClientRect();
  return { left: b.left, top: b.top, width: Math.max(b.width, 1), height: Math.max(b.height, 1) };
}

function hauteurVisible(l = vue.l) {
  const b = boiteCarte();
  return l * (b.height / b.width);
}

// Largeur de vue qui montre toute la carte dans le cadre actuel.
function largeurMonde() {
  const b = boiteCarte();
  return Math.max(vue.largeur, vue.hauteur * (b.width / b.height));
}

// Pendant un geste, on se contente de déplacer et d'agrandir l'image déjà
// rendue (transformation CSS, faite par la carte graphique), puis on redessine
// la carte nette et on charge les tuiles une seule fois, quand le geste s'arrête.
const affichee = { x: 0, y: 0, l: 0 };
let redessin = null;

function cadrer(cx, cy, l, pendantUnGeste = false) {
  const svg = $("#carte svg");
  if (!svg) return;
  vue.l = Math.min(Math.max(l, vue.largeur / ZOOM_MAX), largeurMonde());
  const h = hauteurVisible();
  // Le centre reste dans la carte, et une carte plus petite que le cadre reste centrée.
  const borne = (c, taille, total) => (taille >= total ? total / 2 : Math.min(Math.max(c, taille / 2), total - taille / 2));
  vue.x = borne(cx, vue.l, vue.largeur) - vue.l / 2;
  vue.y = borne(cy, h, vue.hauteur) - h / 2;
  if (pendantUnGeste && affichee.l) {
    const parPixel = boiteCarte().width / vue.l;
    svg.style.transform = `translate(${(affichee.x - vue.x) * parPixel}px, ${(affichee.y - vue.y) * parPixel}px) scale(${affichee.l / vue.l})`;
    clearTimeout(redessin);
    redessin = setTimeout(afficherVue, 180);
  } else {
    afficherVue();
  }
}

function afficherVue() {
  const svg = $("#carte svg");
  clearTimeout(redessin);
  const h = hauteurVisible();
  svg.setAttribute("viewBox", `${vue.x.toFixed(1)} ${vue.y.toFixed(1)} ${vue.l.toFixed(1)} ${h.toFixed(1)}`);
  svg.style.transform = "";
  svg.style.setProperty("--e", (vue.l / boiteCarte().width).toFixed(4));
  const grossissement = vue.largeur / vue.l;
  svg.dataset.zoom = grossissement < 2 ? 1 : grossissement < 4 ? 2 : grossissement < 8 ? 3 : 4;
  Object.assign(affichee, { x: vue.x, y: vue.y, l: vue.l });
  majTuiles();
}

function cadrage(nom) {
  const c = CADRAGES[nom];
  if (!c) cadrer(vue.largeur / 2, vue.hauteur / 2, largeurMonde());
  else cadrer(c[0] + c[2] / 2, c[1] + hauteurVisible(c[2]) / 2, c[2]);
}

// Zoome d'un facteur en gardant fixe le point de la carte sous (clientX, clientY).
function zoomerAutour(clientX, clientY, facteur, pendantUnGeste = false) {
  const b = boiteCarte();
  const fx = (clientX - b.left) / b.width;
  const fy = (clientY - b.top) / b.height;
  const px = vue.x + fx * vue.l;
  const py = vue.y + fy * hauteurVisible();
  const l = Math.min(Math.max(vue.l / facteur, vue.largeur / ZOOM_MAX), largeurMonde());
  const h = hauteurVisible(l);
  cadrer(px - fx * l + l / 2, py - fy * h + h / 2, l, pendantUnGeste);
}

function brancherDeplacements(svg) {
  const pointeurs = new Map();
  let depart = null;
  let glisse = false;
  const noter = () => {
    depart = pointeurs.size ? { x: vue.x, y: vue.y, l: vue.l, pointeurs: new Map(pointeurs) } : null;
  };

  svg.addEventListener("wheel", (e) => {
    e.preventDefault();
    zoomerAutour(e.clientX, e.clientY, Math.pow(1.0015, -e.deltaY * (e.deltaMode === 1 ? 30 : 1)), true);
  }, { passive: false });

  svg.addEventListener("dblclick", (e) => zoomerAutour(e.clientX, e.clientY, 2));

  svg.addEventListener("pointerdown", (e) => {
    pointeurs.set(e.pointerId, [e.clientX, e.clientY]);
    noter();
    glisse = false;
  });

  svg.addEventListener("pointermove", (e) => {
    if (!pointeurs.has(e.pointerId) || !depart) return;
    pointeurs.set(e.pointerId, [e.clientX, e.clientY]);
    const b = boiteCarte();
    if (pointeurs.size === 1) {
      const [x0, y0] = [...depart.pointeurs.values()][0];
      const dx = e.clientX - x0;
      const dy = e.clientY - y0;
      if (!glisse && Math.hypot(dx, dy) < 5) return;
      if (!glisse) svg.setPointerCapture(e.pointerId);
      glisse = true;
      const parPixel = depart.l / b.width;
      cadrer(depart.x - dx * parPixel + depart.l / 2, depart.y - dy * parPixel + hauteurVisible(depart.l) / 2, depart.l, true);
    } else if (pointeurs.size === 2) {
      // Pincement : l'écart entre les deux doigts règle le zoom, autour de leur milieu de départ.
      const [a0, b0] = [...depart.pointeurs.values()];
      const [a1, b1] = [...pointeurs.values()];
      const ecart0 = Math.hypot(a0[0] - b0[0], a0[1] - b0[1]);
      const ecart1 = Math.hypot(a1[0] - b1[0], a1[1] - b1[1]);
      glisse = true;
      Object.assign(vue, { x: depart.x, y: depart.y, l: depart.l });
      zoomerAutour((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2, ecart1 / Math.max(ecart0, 1), true);
    }
  });

  const lever = (e) => {
    pointeurs.delete(e.pointerId);
    noter();
  };
  svg.addEventListener("pointerup", lever);
  svg.addEventListener("pointercancel", lever);
  // Un glissé ne doit pas valoir clic sur le lieu où il se termine.
  svg.addEventListener("click", (e) => {
    if (glisse) {
      e.stopPropagation();
      e.preventDefault();
      glisse = false;
    }
  }, true);

  document.querySelectorAll("[data-zoom-carte]").forEach((bouton) => bouton.addEventListener("click", () => {
    const b = boiteCarte();
    zoomerAutour(b.left + b.width / 2, b.top + b.height / 2, bouton.dataset.zoomCarte === "plus" ? 2 : 0.5);
  }));
  document.querySelectorAll("[data-cadrage]").forEach((bouton) => bouton.addEventListener("click", () => cadrage(bouton.dataset.cadrage)));
}

const MARQUES = {
  capitale: () => creerSvg("rect", { class: "marque", x: -5, y: -5, width: 10, height: 10 }),
  ville: () => creerSvg("circle", { class: "marque", r: 4.5 }),
  forteresse: () => creerSvg("path", { class: "marque", d: "M-6,5 L0,-6 L6,5 Z" }),
  site: () => creerSvg("circle", { class: "marque", r: 5 }),
  ruine: () => creerSvg("path", { class: "marque trait", d: "M-5,0a5,5 0 1,0 10,0a5,5 0 1,0 -10,0M-6,6L6,-6" }),
  bataille: () => creerSvg("path", { class: "marque trait", d: "M-6,-6L6,6M6,-6L-6,6M-6,-2L-2,-6M6,-2L2,-6" }),
};

function construireCarte() {
  const groupeLieux = $("#lieux-carte");
  if (!groupeLieux) return;
  for (const id of ["#zones-carte", "#frontieres-carte", "#provinces-carte", "#colonies-carte", "#etiquettes-carte"]) $(id).replaceChildren();
  groupeLieux.replaceChildren();
  $("#carte svg").setAttribute("aria-label", T().carte);

  // Zones des provinces (teintées au survol) et frontières entre elles.
  const trace = (points, ferme) => `M${points.map(([x, y]) => `${x} ${y}`).join("L")}${ferme ? "Z" : ""}`;
  for (const [nom, polygones] of etat.carte.zones ?? []) {
    const zone = creerSvg("path", { class: "zone", d: polygones.map((p) => trace(p, true)).join("") });
    zone.append(creerSvg("title", {}, nom));
    $("#zones-carte").append(zone);
  }
  $("#frontieres-carte").append(creerSvg("path", { class: "frontiere-province", d: (etat.carte.frontieres ?? []).map((f) => trace(f, false)).join("") }));
  for (const [nom, x, y] of etat.carte.provinces ?? []) {
    $("#provinces-carte").append(creerSvg("text", { x, y, class: "province" }, nom));
  }
  for (const [nom, x, y] of etat.carte.colonies ?? []) {
    const g = creerSvg("g", { class: "colonie", transform: `translate(${x} ${y})` });
    g.append(creerSvg("circle", { r: 3 }), creerSvg("text", { x: 6, y: 3 }, t(nom)));
    $("#colonies-carte").append(g);
  }
  for (const e of etat.carte.etiquettes ?? []) {
    const attributs = { x: e.x, y: e.y, class: `etiquette-${e.type}` };
    if (e.angle) attributs.transform = `rotate(${e.angle} ${e.x} ${e.y})`;
    $("#etiquettes-carte").append(creerSvg("text", attributs, t(e.nom)));
  }

  const compte = nombreParLieu();
  for (const lieu of etat.carte.lieux) {
    if (lieu.x == null) continue;
    const n = compte[lieu.id] ?? 0;
    const groupe = creerSvg("g", {
      class: `lieu lieu-${lieu.type}${n ? "" : " sans-evenement"}${etat.lieux.has(lieu.id) ? " retenu" : ""}`,
      "data-lieu": lieu.id,
      transform: `translate(${lieu.x} ${lieu.y})`,
    });
    // Le contenu garde la même taille à l'écran quel que soit le zoom (voir --e dans style.css).
    const contenu = creerSvg("g", { class: "a-l-echelle" });
    contenu.append(creerSvg("circle", { class: "prise", r: 13 }));
    if (lieu.type === "region") {
      contenu.append(creerSvg("text", { x: 0, y: 5, "text-anchor": "middle" }, t(lieu.nom)));
    } else {
      contenu.append((MARQUES[lieu.type] ?? MARQUES.site)(), creerSvg("text", { x: 9, y: 4.5 }, t(lieu.nom)));
    }
    const titre = `${t(lieu.nom)}, ${T().evenementsLieu(n)}`;
    contenu.append(creerSvg("title", {}, titre));
    groupe.append(contenu);
    if (n) {
      groupe.setAttribute("tabindex", "0");
      groupe.setAttribute("role", "button");
      groupe.setAttribute("aria-label", titre);
      groupe.setAttribute("aria-pressed", String(etat.lieux.has(lieu.id)));
      groupe.addEventListener("click", () => basculerLieu(lieu.id));
      groupe.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          basculerLieu(lieu.id);
        }
      });
    }
    groupeLieux.append(groupe);
  }
  if (!vue.l) {
    // ?carte=x,y,largeur ouvre la carte sur une vue précise, centrée sur (x, y).
    const demande = new URLSearchParams(location.search).get("carte")?.split(",").map(Number);
    if (demande?.length === 3 && demande.every(Number.isFinite)) cadrer(...demande);
    else cadrage("vieux-monde");
  }
}

function nombreParLieu() {
  const compte = {};
  for (const ev of etat.evenements) for (const l of ev.lieux ?? []) compte[l] = (compte[l] ?? 0) + 1;
  return compte;
}

function basculerLieu(id) {
  etat.lieux.has(id) ? etat.lieux.delete(id) : etat.lieux.add(id);
  appliquer();
}

// Met en avant sur la carte les lieux d'un événement choisi dans la chronique.
function evoquerLieux(ids) {
  document.querySelectorAll(".lieu.evoque").forEach((g) => g.classList.remove("evoque"));
  for (const id of ids) document.querySelector(`.lieu[data-lieu="${id}"]`)?.classList.add("evoque");
}

function legendeLieux() {
  const zone = $("#lieux-choisis");
  zone.replaceChildren();
  if (!etat.lieux.size) {
    zone.append(creer("p", { className: "vide", textContent: T().aucunLieu }));
    return;
  }
  const lieux = index(etat.carte.lieux);
  const compte = nombreParLieu();
  const liste = creer("ul", {});
  for (const id of etat.lieux) {
    const retirer = creer("button", { type: "button", className: "retirer", textContent: "×", title: T().retirer });
    retirer.setAttribute("aria-label", `${T().retirer} ${t(lieux[id]?.nom)}`);
    retirer.addEventListener("click", () => basculerLieu(id));
    liste.append(creer("li", {},
      creer("strong", { textContent: t(lieux[id]?.nom) || id }),
      ` ${T().evenementsLieu(compte[id] ?? 0)} `,
      retirer,
    ));
  }
  const voir = creer("a", { href: "#chronique", textContent: T().voirChronique });
  zone.append(liste, voir);
}

// Calques de la carte : chaque case affiche ou masque une famille de noms.
// Le choix est gardé dans l'adresse (?masquer=mers) et dans le navigateur.
const CALQUES = ["lieux", "regions", "mers", "frontieres", "provinces", "colonies"];

function construireCalques() {
  const liste = $("#liste-calques");
  liste.replaceChildren();
  for (const calque of CALQUES) {
    const case_ = creer("input", { type: "checkbox", value: calque, checked: !etat.calquesMasques.has(calque) });
    case_.addEventListener("change", () => {
      case_.checked ? etat.calquesMasques.delete(calque) : etat.calquesMasques.add(calque);
      appliquerCalques();
      ecrireAdresse();
      try {
        localStorage.setItem("calques-masques", [...etat.calquesMasques].join(" "));
      } catch {}
    });
    liste.append(creer("label", {}, case_, T().nomsCalques[calque]));
  }
  appliquerCalques();
}

function appliquerCalques() {
  const svg = $("#carte svg");
  if (svg) svg.dataset.masquer = [...etat.calquesMasques].join(" ");
}

function construireLegendeTypes() {
  const zone = $("#types-lieux");
  zone.replaceChildren();
  for (const [type, nom] of Object.entries(T().typesLieux)) {
    const svg = creerSvg("svg", { viewBox: "-8 -8 16 16", "aria-hidden": "true" });
    svg.append(MARQUES[type]());
    zone.append(creer("li", { className: `lieu-${type}` }, svg, nom));
  }
}

/* Filtres */

function construireFiltres() {
  const groupes = [
    ["#filtre-factions", etat.ref.factions, etat.factions, true],
    ["#filtre-regions", etat.ref.regions, etat.regions, false],
    ["#filtre-fiabilites", etat.ref.fiabilites, etat.fiabilites, false],
    ["#filtre-importances", ["3", "2", "1"].map((id) => ({ id, nom: T().importances[id] })), etat.importances, false],
  ];

  for (const [sel, liste, ensemble, pastille] of groupes) {
    const conteneur = $(sel);
    conteneur.replaceChildren();
    for (const item of liste) {
      const nombre = etat.evenements.filter((ev) =>
        [ev.factions, ev.regions, [ev.fiabilite], [String(ev.importance)]].some((l) => l.includes(item.id)),
      ).length;
      if (!nombre) continue;

      const case_ = creer("input", { type: "checkbox", value: item.id, checked: ensemble.has(item.id) });
      case_.addEventListener("change", () => {
        case_.checked ? ensemble.add(item.id) : ensemble.delete(item.id);
        appliquer();
      });
      conteneur.append(
        creer("label", { title: t(item.aide) },
          case_,
          pastille ? creer("span", { className: "pastille", style: `--couleur: ${item.couleur}` }) : null,
          `${t(item.nom)} (${nombre})`,
        ),
      );
    }
  }
}

function brancherFiltres() {
  // On attend une courte pause dans la frappe avant de filtrer.
  let attente = null;
  $("#recherche").addEventListener("input", (e) => {
    clearTimeout(attente);
    attente = setTimeout(() => {
      etat.texte = sansAccents(e.target.value.trim());
      appliquer();
    }, 120);
  });
  $("#effacer").addEventListener("click", effacerFiltres);
  if (matchMedia("(max-width: 52rem)").matches) $("#panneau-filtres").open = false;
}

function effacerFiltres() {
  etat.factions.clear();
  etat.regions.clear();
  etat.fiabilites.clear();
  etat.importances.clear();
  etat.lieux.clear();
  etat.texte = "";
  $("#recherche").value = "";
  document.querySelectorAll(".filtres input[type=checkbox]").forEach((c) => (c.checked = false));
  appliquer();
}

// Les filtres sont gardés dans l'adresse, pour pouvoir partager une vue
// comme ?faction=nains&region=montagnes&lieu=karaz-a-karak.
function lireAdresse() {
  const p = new URLSearchParams(location.search);
  p.getAll("faction").forEach((v) => etat.factions.add(v));
  p.getAll("region").forEach((v) => etat.regions.add(v));
  p.getAll("lieu").forEach((v) => etat.lieux.add(v));
  p.getAll("fiabilite").forEach((v) => etat.fiabilites.add(v));
  p.getAll("importance").forEach((v) => etat.importances.add(v));
  let masques = p.getAll("masquer");
  if (!p.has("masquer")) {
    try {
      masques = (localStorage.getItem("calques-masques") ?? "").split(" ");
    } catch {}
  }
  masques.filter((v) => CALQUES.includes(v)).forEach((v) => etat.calquesMasques.add(v));
}

function ecrireAdresse() {
  const p = new URLSearchParams();
  if (new URLSearchParams(location.search).has("lang")) p.set("lang", etat.langue);
  etat.factions.forEach((v) => p.append("faction", v));
  etat.regions.forEach((v) => p.append("region", v));
  etat.lieux.forEach((v) => p.append("lieu", v));
  etat.fiabilites.forEach((v) => p.append("fiabilite", v));
  etat.importances.forEach((v) => p.append("importance", v));
  etat.calquesMasques.forEach((v) => p.append("masquer", v));
  const q = p.toString();
  history.replaceState(null, "", `${location.pathname}${q ? `?${q}` : ""}${location.hash}`);
}

/* Chronique */

function carteEvenement(ev, factions, regions, fiabilites, lieux) {
  const etiquettes = creer("p", { className: "etiquettes" },
    ...ev.factions.map((f) =>
      creer("span", {},
        creer("span", { className: "pastille", style: `--couleur: ${factions[f]?.couleur}` }),
        t(factions[f]?.nom) || f,
      ),
    ),
    creer("span", { textContent: ev.regions.map((r) => t(regions[r]?.nom) || r).join(", ") }),
  );

  const nomsLieux = (ev.lieux ?? []).filter((l) => lieux[l]);
  const lignesLieux = nomsLieux.length
    ? creer("p", { className: "lieux-evenement" },
      `${T().lieux} : `,
      ...nomsLieux.flatMap((l, i) => {
        const bouton = creer("button", { type: "button", textContent: t(lieux[l].nom) });
        bouton.addEventListener("click", () => {
          if (!etat.lieux.has(l)) basculerLieu(l);
          $("#vue-carte").scrollIntoView({ behavior: "smooth", block: "start" });
        });
        return i ? [", ", bouton] : [bouton];
      }),
    )
    : null;

  const fiab = fiabilites[ev.fiabilite];
  const sources = creer("details", { className: "sources" },
    creer("summary", { textContent: T().sources(ev.sources.length, t(fiab?.nom).toLowerCase()) }),
    creer("ul", {},
      ...ev.sources.map((s) =>
        creer("li", {},
          s.url ? creer("a", { href: s.url, textContent: t(s.titre), rel: "noopener" }) : t(s.titre),
          t(s.detail) ? `, ${t(s.detail)}` : "",
        ),
      ),
    ),
    creer("p", { className: "fiabilite" },
      creer("strong", { textContent: `${t(fiab?.nom)}. ` }),
      t(fiab?.aide),
    ),
    t(ev.note) ? creer("p", { className: "fiabilite", textContent: t(ev.note) }) : null,
  );

  const article = creer("article", {
    className: "evenement",
    id: ev.id,
    "data-importance": ev.importance,
    "data-fiabilite": ev.fiabilite,
  },
    creer("div", { className: "date" },
      formaterAnnee(ev.annee),
      ev.approx || (ev.fin != null && ev.fin !== ev.annee)
        ? creer("small", { textContent: formaterDate(ev) })
        : null,
    ),
    creer("div", {},
      creer("h3", { textContent: t(ev.titre) }),
      etiquettes,
      creer("p", { textContent: t(ev.resume) }),
      lignesLieux,
      sources,
    ),
  );
  article.addEventListener("mouseenter", () => evoquerLieux(nomsLieux));
  return article;
}

// La chronique est construite une fois par langue. Les filtres se contentent
// ensuite de masquer ou d'afficher les événements et les titres d'âge.
const chroniqueConstruite = { evenements: new Map(), eres: new Map(), vide: null };

function construireChronique() {
  const factions = index(etat.ref.factions);
  const regions = index(etat.ref.regions);
  const fiabilites = index(etat.ref.fiabilites);
  const lieux = index(etat.carte?.lieux ?? []);
  const { evenements, eres } = chroniqueConstruite;
  evenements.clear();
  eres.clear();
  const chronique = $("#chronique");
  chronique.replaceChildren();

  for (const ere of etat.ref.eres) {
    const dansEre = etat.evenements.filter((ev) => ev.ere === ere.id);
    if (!dansEre.length) continue;
    const titres = [
      creer("h2", { textContent: t(ere.nom) }),
      creer("p", { className: "bornes", textContent: `${formaterAnnee(ere.debut)}${T().jusqua}${formaterAnnee(ere.fin)}` }),
    ];
    eres.set(ere.id, titres);
    chronique.append(...titres);
    for (const ev of dansEre) {
      const article = carteEvenement(ev, factions, regions, fiabilites, lieux);
      evenements.set(ev.id, article);
      chronique.append(article);
    }
  }
  chroniqueConstruite.vide = creer("p", { className: "vide", textContent: T().vide, hidden: true });
  chronique.append(chroniqueConstruite.vide);
}

function appliquer() {
  const visibles = etat.evenements.filter(retenu);
  const ids = new Set(visibles.map((ev) => ev.id));
  const eresVisibles = new Set(visibles.map((ev) => ev.ere));

  for (const [id, article] of chroniqueConstruite.evenements) article.hidden = !ids.has(id);
  for (const [id, titres] of chroniqueConstruite.eres) titres.forEach((el) => (el.hidden = !eresVisibles.has(id)));
  chroniqueConstruite.vide.hidden = visibles.length > 0;

  document.querySelectorAll(".trait").forEach((tr) => tr.classList.toggle("estompe", !ids.has(tr.dataset.id)));
  document.querySelectorAll(".lieu[data-lieu]").forEach((g) => {
    const retenuLieu = etat.lieux.has(g.dataset.lieu);
    g.classList.toggle("retenu", retenuLieu);
    if (g.hasAttribute("aria-pressed")) g.setAttribute("aria-pressed", String(retenuLieu));
  });
  if (etat.carte) legendeLieux();
  $("#compte").textContent = T().compte(visibles.length, etat.evenements.length);
  ecrireAdresse();
}

function toutConstruire() {
  construireFrise();
  construireFiltres();
  if (etat.carte) {
    construireCarte();
    construireLegendeTypes();
    construireCalques();
  }
  construireChronique();
  appliquer();
}

async function charger() {
  const lire = (url) => fetch(`${url}?v=${VERSION}`).then((r) => {
    if (!r.ok) throw new Error(`${url} : ${r.status}`);
    return r.json();
  });

  construireSelecteurLangue();
  etat.langue = langueInitiale() ?? (await demanderLangue());
  choisirLangue(etat.langue);
  brancherFiltres();

  const [ref, lots, carte] = await Promise.all([
    lire("donnees/referentiel.json"),
    Promise.allSettled(FICHIERS.map(lire)),
    Promise.all([lire("donnees/carte.json"), chargerFondDeCarte()]).then(([c]) => c).catch((err) => {
      console.warn(err);
      $("#vue-carte").hidden = true;
      return null;
    }),
  ]);
  etat.ref = ref;
  etat.carte = carte;
  lots.filter((l) => l.status === "rejected").forEach((l) => console.warn(l.reason));

  etat.evenements = lots
    .filter((l) => l.status === "fulfilled")
    .flatMap((l) => l.value)
    .sort((a, b) => a.annee - b.annee);

  lireAdresse();
  toutConstruire();

  const suivreAncre = () => {
    if (location.hash && location.hash !== "#chronique") montrer(decodeURIComponent(location.hash.slice(1)), false);
  };
  window.addEventListener("hashchange", suivreAncre);
  suivreAncre();
}

charger().catch((err) => {
  $("#chronique").append(creer("p", { className: "vide", textContent: T().erreur(err.message) }));
});
