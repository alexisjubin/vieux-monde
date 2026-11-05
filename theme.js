"use strict";

// Chargé avant le premier affichage pour éviter un éclair de la mauvaise
// couleur. La politique CSP interdit les scripts écrits dans la page.
(function () {
  let mode = "auto";
  let teinte = "ardoise";
  try {
    mode = localStorage.getItem("mode") || mode;
    teinte = localStorage.getItem("teinte") || teinte;
  } catch {
    // Stockage indisponible : on garde les valeurs par défaut.
  }
  const sombre = mode === "sombre" || (mode === "auto" && matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.mode = sombre ? "sombre" : "clair";
  document.documentElement.dataset.teinte = teinte;
})();
