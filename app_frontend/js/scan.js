// Plate-scanning UI for the listing entry form: a full-width strip that opens a
// capture sheet (idle → reading → done). The sheet uploads a photo to
// POST /api/ocr/plate and offers the detected, EDITABLE number for the user to
// accept into the reg field. Scanning never blocks manual entry.

import { api, ApiError } from "./api.js";
import { closeDialog, el, toast } from "./ui.js";

// A small inline scan glyph (Lucide "scan-line", stroke 1.5) as an SVG node.
function scanIcon() {
  const svgNs = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNs, "svg");
  svg.setAttribute("width", "22");
  svg.setAttribute("height", "22");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "1.5");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  const paths = [
    "M3 7V5a2 2 0 0 1 2-2h2",
    "M17 3h2a2 2 0 0 1 2 2v2",
    "M21 17v2a2 2 0 0 1-2 2h-2",
    "M7 21H5a2 2 0 0 1-2-2v-2",
    "M7 12h10",
  ];
  for (const d of paths) {
    const path = document.createElementNS(svgNs, "path");
    path.setAttribute("d", d);
    svg.append(path);
  }
  return svg;
}

// The strip shown in the entry panel. `getReg` reads the current field value so
// the strip restyles between "empty" and "filled"; `onAccepted` writes the
// scanned number back into the form.
export function scanStrip(getReg, onAccepted) {
  const filled = Boolean(getReg().trim());

  const style = filled
    ? "background: transparent; color: var(--color-accent-800); border: 1px solid var(--color-divider)"
    : "background: var(--color-accent-100); color: var(--color-accent-900); border: 1px solid var(--color-accent)";

  const iconBox = el(
    "div",
    {
      style:
        "display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border: 1px solid currentColor; flex: none",
    },
    scanIcon()
  );

  const text = el("div", { style: "display: flex; flex-direction: column; gap: 2px; min-width: 0" }, [
    el("span", { style: "font-family: var(--font-heading); font-size: 18px; line-height: 1.15" }, "Scan the registration plate"),
    el("span", { style: "font-size: 12px; opacity: 0.75" }, "Take a photo and we read the number into the field — or type it below"),
  ]);

  const hint = el("span", { style: "margin-left: auto; font-size: 13px; white-space: nowrap; align-self: center" }, filled ? "Scan again →" : "Fastest way →");

  return el(
    "button",
    {
      type: "button",
      class: "scan-strip",
      style:
        "display: flex; align-items: center; gap: 14px; width: 100%; padding: 12px 16px; min-height: 68px; margin-bottom: 16px; text-align: left; cursor: pointer; " +
        style,
      onClick: () => openCaptureSheet(onAccepted),
    },
    [iconBox, text, hint]
  );
}

// --- the capture sheet -----------------------------------------------------

function openCaptureSheet(onAccepted) {
  const root = document.getElementById("dialog-root");

  const stepLabel = el("span", { style: "margin-left: auto; font-size: 12px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.08em" }, "Step 1 of 2");
  const stageSlot = el("div");

  // Hidden file inputs: one opens the camera, one the gallery.
  const cameraInput = el("input", { type: "file", accept: "image/*", capture: "environment", style: "display: none", onChange: (e) => onPicked(e) });
  const galleryInput = el("input", { type: "file", accept: "image/*", style: "display: none", onChange: (e) => onPicked(e) });

  function setStep(step) {
    stepLabel.textContent = `Step ${step} of 2`;
  }

  async function onPicked(event) {
    const file = event.target.files?.[0];
    event.target.value = ""; // allow re-picking the same file
    if (!file) return;
    await runDetection(file);
  }

  // --- stage: idle ---
  function showIdle(message) {
    setStep(1);
    const viewfinder = el(
      "div",
      {
        class: "blueprint",
        style: "padding: 22px; min-height: 190px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-style: dashed; margin-bottom: 16px",
      },
      [
        el("i", { class: "corner tl" }), el("i", { class: "corner tr" }), el("i", { class: "corner bl" }), el("i", { class: "corner br" }),
        el("div", { style: "font-family: var(--font-heading); font-size: 20px" }, "Camera preview"),
        el("div", { class: "text-muted", style: "font-size: 13px; max-width: 340px; margin-top: 6px" }, "Fill the frame with the plate — glare and steep angles are the usual cause of a misread."),
        message ? el("div", { style: "font-size: 12px; color: var(--color-accent-800); margin-top: 10px" }, message) : null,
      ]
    );
    stageSlot.replaceChildren(
      viewfinder,
      el("div", { style: "display: flex; flex-direction: column; gap: 10px" }, [
        el("button", { class: "btn btn-primary blueprint", style: "min-height: 54px; font-size: 17px", onClick: () => cameraInput.click() }, [
          el("i", { class: "corner tl" }), el("i", { class: "corner tr" }), el("i", { class: "corner bl" }), el("i", { class: "corner br" }), "Take a picture",
        ]),
        el("button", { class: "btn btn-secondary", style: "min-height: 46px", onClick: () => galleryInput.click() }, "Choose an existing photo"),
      ])
    );
  }

  // --- stage: reading ---
  function showReading() {
    setStep(1);
    stageSlot.replaceChildren(
      el("div", { style: "background: var(--color-accent-100); padding: 34px 22px; min-height: 190px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 16px" }, [
        el("div", { style: "font-family: var(--font-heading); font-size: 20px; color: var(--color-accent-900)" }, "Reading the plate…"),
        el("div", { class: "text-muted", style: "font-size: 13px; margin-top: 6px" }, "Hold still for a second."),
      ])
    );
  }

  // --- stage: done ---
  function showDone(detected) {
    setStep(2);
    let value = detected;
    const input = el("input", {
      class: "input num",
      value: detected,
      "aria-label": "Detected registration number",
      style: "min-height: 52px; font-size: 24px; font-family: var(--font-heading); letter-spacing: 0.06em; text-align: center; text-transform: uppercase",
      onInput: (e) => {
        value = e.target.value.toUpperCase();
        e.target.value = value;
      },
    });
    stageSlot.replaceChildren(
      el("div", { style: "background: var(--color-accent-100); padding: 16px 22px; text-align: center; margin-bottom: 14px" }, [
        el("div", { style: "font-family: var(--font-heading); font-size: 18px; color: var(--color-accent-900)" }, "Plate captured"),
        el("div", { class: "text-muted", style: "font-size: 13px; margin-top: 4px" }, "Not right? Retake the photo or correct the number below."),
      ]),
      el("div", { class: "field" }, [
        el("label", {}, "Detected registration number — check it before using"),
        input,
      ]),
      el("div", { style: "display: flex; flex-direction: column; gap: 10px; margin-top: 14px" }, [
        el("button", { class: "btn btn-primary blueprint", style: "min-height: 54px", onClick: () => accept(value) }, [
          el("i", { class: "corner tl" }), el("i", { class: "corner tr" }), el("i", { class: "corner bl" }), el("i", { class: "corner br" }), "Use this number",
        ]),
        el("button", { class: "btn btn-secondary", style: "min-height: 46px", onClick: () => showIdle() }, "Retake"),
      ])
    );
    setTimeout(() => input.focus(), 0);
  }

  async function runDetection(file) {
    showReading();
    const body = new FormData();
    body.append("image", file);
    try {
      const result = await api.postForm("/ocr/plate", body);
      if (result.reg_number) {
        showDone(result.reg_number);
      } else {
        showIdle("No plate found in that photo — try again, or type the number by hand.");
      }
    } catch (error) {
      const message =
        error instanceof ApiError && error.status === 503
          ? "The plate reader is unavailable right now — please type the number by hand."
          : "Couldn't read that photo — try again, or type the number by hand.";
      showIdle(message);
    }
  }

  function accept(value) {
    const cleaned = value.trim().toUpperCase();
    closeDialog();
    onAccepted(cleaned);
    toast("Registration filled from the photo — check it matches");
  }

  const sheet = el("div", { class: "dialog blueprint", style: "background: var(--color-bg); width: min(560px, 100%); max-height: 90vh; overflow-y: auto" }, [
    el("i", { class: "corner tl" }), el("i", { class: "corner tr" }), el("i", { class: "corner bl" }), el("i", { class: "corner br" }),
    el("div", { style: "display: flex; align-items: baseline; margin-bottom: 16px" }, [
      el("div", { class: "dialog-title" }, "Scan registration"),
      stepLabel,
    ]),
    stageSlot,
    cameraInput,
    galleryInput,
    el("button", { class: "btn btn-ghost", style: "min-height: 40px; width: 100%; margin-top: 12px", onClick: closeDialog }, "Cancel — type it by hand"),
  ]);

  showIdle();
  root.replaceChildren(el("div", { class: "dialog-backdrop" }, sheet));
}
