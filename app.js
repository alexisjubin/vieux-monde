"use strict";

const FICHIERS = ["donnees/evenements-anciens.json", "donnees/evenements-empire.json"];

const etat = {
  ref: null,
  evenements: [],
  factions: new Set(),
  regions: new Set(),
  fiabilites: new Set(),
  texte: "",
};

const $ = (sel) => document.querySelector(sel);

function formaterAnnee(annee) {
  if (annee < 0) return `${Math.abs(annee)} av. CI`;
  return `${annee} CI`;
}

function formaterDate(ev) {
  let texte = formaterAnnee(ev.annee);
  if (ev.fin != null && ev.fin !== ev.annee) {
    texte = ev.annee < 0 && ev.fin < 0
      ? `${Math.abs(ev.annee)} - ${formaterAnnee(ev.fin)}`
      : `${formaterAnnee(ev.annee)} - ${formaterAnnee(ev.fin)}`;
  }
  return ev.approx ? `vers ${texte}` : texte;
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
  if (etat.fiabilites.size && !etat.fiabilites.has(ev.fiabilite)) return false;
  if (etat.texte) {
    const botte = sansAccents(`${ev.titre} ${ev.resume} ${ev.note}`);
    if (!botte.includes(etat.texte)) return false;
  }
  return true;
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

/* Frise d'ensemble */

function construireFrise() {
  const frise = $("#frise");
  const total = etat.ref.eres.reduce((s, e) => s + e.poids, 0);

  for (const ere of etat.ref.eres) {
    frise.append(
      creer("div", { className: "age", style: `flex: ${ere.poids / total} 1 0` },
        creer("span", { className: "age-debut", textContent: String(ere.debut) }),
        creer("span", { className: "age-nom", textContent: ere.nom }),
      ),
    );
  }

  const tow = etat.ref.epoque_tow;
  if (tow) {
    const g = position(tow.debut) * 100;
    const d = position(tow.fin) * 100;
    frise.append(creer("div", {
      className: "epoque-tow",
      title: `Époque de The Old World, ${formaterAnnee(tow.debut)} - ${formaterAnnee(tow.fin)}`,
      style: `left: ${g}%; width: ${d - g}%`,
    }));
  }

  const factions = index(etat.ref.factions);
  for (const ev of etat.evenements) {
    const couleur = factions[ev.factions[0]]?.couleur ?? "var(--encre)";
    const trait = creer("button", {
      type: "button",
      className: "trait",
      title: `${formaterDate(ev)}, ${ev.titre}`,
      "data-id": ev.id,
      "data-importance": ev.importance,
      style: `left: ${position(ev.annee) * 100}%; --couleur: ${couleur}`,
    });
    trait.setAttribute("role", "listitem");
    trait.setAttribute("aria-label", `${formaterDate(ev)}, ${ev.titre}`);
    trait.addEventListener("click", () => montrer(ev.id));
    frise.append(trait);
  }
}

function montrer(id, fluide = true) {
  let cible = document.getElementById(id);
  if (!cible) {
    // L'événement est masqué par un filtre : on lève les filtres d'abord.
    effacerFiltres();
    cible = document.getElementById(id);
    if (!cible) return;
  }
  document.querySelectorAll(".evenement.choisi").forEach((e) => e.classList.remove("choisi"));
  cible.classList.add("choisi");
  cible.scrollIntoView({ behavior: fluide ? "smooth" : "auto", block: "start" });
  history.replaceState(null, "", `${location.search}#${id}`);
}

/* Filtres */

function construireFiltres() {
  const groupes = [
    ["#filtre-factions", etat.ref.factions, etat.factions, true],
    ["#filtre-regions", etat.ref.regions, etat.regions, false],
    ["#filtre-fiabilites", etat.ref.fiabilites, etat.fiabilites, false],
  ];

  for (const [sel, liste, ensemble, pastille] of groupes) {
    const conteneur = $(sel);
    for (const item of liste) {
      const nombre = etat.evenements.filter((ev) =>
        [ev.factions, ev.regions, [ev.fiabilite]].some((l) => l.includes(item.id)),
      ).length;
      if (!nombre) continue;

      const case_ = creer("input", { type: "checkbox", value: item.id, checked: ensemble.has(item.id) });
      case_.addEventListener("change", () => {
        case_.checked ? ensemble.add(item.id) : ensemble.delete(item.id);
        appliquer();
      });
      conteneur.append(
        creer("label", { title: item.aide ?? "" },
          case_,
          pastille ? creer("span", { className: "pastille", style: `--couleur: ${item.couleur}` }) : null,
          `${item.nom} (${nombre})`,
        ),
      );
    }
  }

  $("#recherche").addEventListener("input", (e) => {
    etat.texte = sansAccents(e.target.value.trim());
    appliquer();
  });
  $("#effacer").addEventListener("click", effacerFiltres);

  if (matchMedia("(max-width: 52rem)").matches) $("#panneau-filtres").open = false;
}

function effacerFiltres() {
  etat.factions.clear();
  etat.regions.clear();
  etat.fiabilites.clear();
  etat.texte = "";
  $("#recherche").value = "";
  document.querySelectorAll(".filtres input[type=checkbox]").forEach((c) => (c.checked = false));
  appliquer();
}

// Les filtres sont gardés dans l'adresse, pour pouvoir partager une vue
// comme ?faction=nains&region=montagnes.
function lireAdresse() {
  const p = new URLSearchParams(location.search);
  p.getAll("faction").forEach((v) => etat.factions.add(v));
  p.getAll("region").forEach((v) => etat.regions.add(v));
  p.getAll("fiabilite").forEach((v) => etat.fiabilites.add(v));
}

function ecrireAdresse() {
  const p = new URLSearchParams();
  etat.factions.forEach((v) => p.append("faction", v));
  etat.regions.forEach((v) => p.append("region", v));
  etat.fiabilites.forEach((v) => p.append("fiabilite", v));
  const q = p.toString();
  history.replaceState(null, "", `${location.pathname}${q ? `?${q}` : ""}${location.hash}`);
}

/* Chronique */

function carteEvenement(ev, factions, regions, fiabilites) {
  const etiquettes = creer("p", { className: "etiquettes" },
    ...ev.factions.map((f) =>
      creer("span", {},
        creer("span", { className: "pastille", style: `--couleur: ${factions[f]?.couleur}` }),
        factions[f]?.nom ?? f,
      ),
    ),
    creer("span", { textContent: ev.regions.map((r) => regions[r]?.nom ?? r).join(", ") }),
  );

  const sources = creer("details", { className: "sources" },
    creer("summary", { textContent: `Sources (${ev.sources.length}), ${fiabilites[ev.fiabilite]?.nom.toLowerCase()}` }),
    creer("ul", {},
      ...ev.sources.map((s) =>
        creer("li", {},
          s.url ? creer("a", { href: s.url, textContent: s.titre, rel: "noopener" }) : s.titre,
          s.detail ? `, ${s.detail}` : "",
        ),
      ),
    ),
    creer("p", { className: "fiabilite" },
      creer("strong", { textContent: `${fiabilites[ev.fiabilite]?.nom}. ` }),
      fiabilites[ev.fiabilite]?.aide ?? "",
    ),
    ev.note ? creer("p", { className: "fiabilite", textContent: ev.note }) : null,
  );

  return creer("article", {
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
      creer("h3", { textContent: ev.titre }),
      etiquettes,
      creer("p", { textContent: ev.resume }),
      sources,
    ),
  );
}

function appliquer() {
  const factions = index(etat.ref.factions);
  const regions = index(etat.ref.regions);
  const fiabilites = index(etat.ref.fiabilites);
  const visibles = etat.evenements.filter(retenu);
  const ids = new Set(visibles.map((ev) => ev.id));

  const chronique = $("#chronique");
  chronique.replaceChildren();

  for (const ere of etat.ref.eres) {
    const dansEre = visibles.filter((ev) => ev.ere === ere.id);
    if (!dansEre.length) continue;
    chronique.append(
      creer("h2", { textContent: ere.nom }),
      creer("p", { className: "bornes", textContent: `${formaterAnnee(ere.debut)} - ${formaterAnnee(ere.fin)}` }),
      ...dansEre.map((ev) => carteEvenement(ev, factions, regions, fiabilites)),
    );
  }

  if (!visibles.length) {
    chronique.append(creer("p", { className: "vide", textContent: "Aucun événement ne correspond à ces filtres." }));
  }

  document.querySelectorAll(".trait").forEach((t) => t.classList.toggle("estompe", !ids.has(t.dataset.id)));
  $("#compte").textContent = `${visibles.length} sur ${etat.evenements.length}`;
  ecrireAdresse();
}

async function charger() {
  const lire = (url) => fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${url} : ${r.status}`);
    return r.json();
  });

  etat.ref = await lire("donnees/referentiel.json");
  const lots = await Promise.allSettled(FICHIERS.map(lire));
  lots.filter((l) => l.status === "rejected").forEach((l) => console.warn(l.reason));

  etat.evenements = lots
    .filter((l) => l.status === "fulfilled")
    .flatMap((l) => l.value)
    .sort((a, b) => a.annee - b.annee);

  lireAdresse();
  construireFrise();
  construireFiltres();
  appliquer();

  const suivreAncre = () => {
    if (location.hash) montrer(decodeURIComponent(location.hash.slice(1)), false);
  };
  window.addEventListener("hashchange", suivreAncre);
  suivreAncre();
}

charger().catch((err) => {
  $("#chronique").append(creer("p", { className: "vide", textContent: `Impossible de charger les données (${err.message}).` }));
});
