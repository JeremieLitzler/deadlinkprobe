// version-fill.js — fills the version badge and footer version from the
// latest GitHub release. Any error leaves the fallback "latest".
(function () {
  "use strict";

  var API =
    "https://api.github.com/repos/JeremieLitzler/deadlinkprobe/releases/latest";
  var TAG = /^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?$/;

  function apply(label) {
    var nodes = document.querySelectorAll("[data-version]");
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].textContent = label;
    }
  }

  fetch(API, { headers: { Accept: "application/vnd.github+json" } })
    .then(function (res) {
      if (!res.ok) {
        throw new Error("HTTP " + res.status);
      }
      return res.json();
    })
    .then(function (release) {
      var tag = release && release.tag_name;
      apply(typeof tag === "string" && TAG.test(tag) ? tag : "latest");
    })
    .catch(function () {
      apply("latest");
    });
})();
